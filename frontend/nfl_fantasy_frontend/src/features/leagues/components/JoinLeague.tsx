<<<<<<< HEAD
import React, { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { searchLeagues, joinLeague, LeagueSearchResult, JoinLeagueRequest, uploadFantasyTeamImage } from '../../../services/leagues';
=======
import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { searchLeagues, joinLeague, LeagueSearchResult, JoinLeagueRequest } from '../../../services/leagues';
import { listTeams, Team } from '../../../services/teams';
>>>>>>> main
import { useAuth } from '../../../shared/hooks/useAuth';

const JoinLeague = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [leagues, setLeagues] = useState<LeagueSearchResult[]>([]);
<<<<<<< HEAD
=======
  const [teams, setTeams] = useState<Team[]>([]);
>>>>>>> main
  const [loading, setLoading] = useState(false);
  const [loadingLeagues, setLoadingLeagues] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  
  // Filtros de búsqueda
  const [searchName, setSearchName] = useState('');
  const [filterStatus, setFilterStatus] = useState<string>('');
  
  // Modal state
  const [selectedLeague, setSelectedLeague] = useState<LeagueSearchResult | null>(null);
  const [showModal, setShowModal] = useState(false);
  const [password, setPassword] = useState('');
  const [userAlias, setUserAlias] = useState('');
<<<<<<< HEAD
  // Fantasy team fields
  const [fantasyName, setFantasyName] = useState('');
  // City removed for fantasy teams
  const [fantasyImageUrl, setFantasyImageUrl] = useState('');
  const [fantasyThumbUrl, setFantasyThumbUrl] = useState('');
  const [uploadingImage, setUploadingImage] = useState(false);
  const [uploadedFileName, setUploadedFileName] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);
=======
  const [selectedTeamId, setSelectedTeamId] = useState<number | null>(null);
>>>>>>> main

  // Cargar ligas al inicio
  useEffect(() => {
    loadLeagues();
<<<<<<< HEAD
=======
    loadUserTeams();
>>>>>>> main
  }, []);

  const loadLeagues = async () => {
    setLoadingLeagues(true);
    setError('');
    try {
      const filters: any = {};
      if (searchName) filters.name = searchName;
      if (filterStatus) filters.status = filterStatus;
      
      const data = await searchLeagues(filters);
      setLeagues(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al cargar las ligas');
    } finally {
      setLoadingLeagues(false);
    }
  };

<<<<<<< HEAD
  // No need to load user teams. Fantasy team is created on join
=======
  const loadUserTeams = async () => {
    try {
      if (!user) return;
      // Obtener solo equipos del usuario que NO estén en una liga
      const allTeams = await listTeams({ user_id: user.id });
      // Nota: El backend debería filtrar esto, pero por ahora lo hacemos aquí
      setTeams(allTeams);
    } catch (err) {
      console.error('Error al cargar equipos:', err);
    }
  };
>>>>>>> main

  const handleSearch = () => {
    loadLeagues();
  };

  const handleSelectLeague = (league: LeagueSearchResult) => {
    if (league.slots_available <= 0) {
      setError('Esta liga no tiene cupos disponibles');
      return;
    }
    setSelectedLeague(league);
    setShowModal(true);
    setPassword('');
    setUserAlias('');
<<<<<<< HEAD
  setFantasyName('');
  setFantasyImageUrl('');
  setFantasyThumbUrl('');
=======
    setSelectedTeamId(null);
>>>>>>> main
    setError('');
    setSuccess('');
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setSelectedLeague(null);
    setPassword('');
    setUserAlias('');
<<<<<<< HEAD
  setFantasyName('');
  setFantasyImageUrl('');
  setFantasyThumbUrl('');
=======
    setSelectedTeamId(null);
>>>>>>> main
    setError('');
  };

  const handleSubmitJoin = async (e: React.FormEvent) => {
    e.preventDefault();
    
<<<<<<< HEAD
    if (!selectedLeague) return;
    if (fantasyName.trim().length < 2) {
      setError('Ingresa un nombre válido para tu equipo de fantasía');
      return;
    }
=======
    if (!selectedLeague || !selectedTeamId) return;
>>>>>>> main
    
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const payload: JoinLeagueRequest = {
        password,
        user_alias: userAlias,
<<<<<<< HEAD
        fantasy_team: {
          name: fantasyName.trim(),
          image_url: fantasyImageUrl.trim() || undefined,
        },
=======
        team_id: selectedTeamId,
>>>>>>> main
      };

      const result = await joinLeague(selectedLeague.id, payload);
      setSuccess(result.message);
      
      // Cerrar modal después de 2 segundos y recargar ligas
      setTimeout(() => {
        handleCloseModal();
        loadLeagues();
      }, 2000);
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || 'Error al unirse a la liga';
      setError(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadgeColor = (status: string) => {
    switch (status) {
      case 'pre_draft': return '#63b3ed'; // blue
      case 'draft': return '#f6ad55'; // orange
      case 'in_season': return '#68d391'; // green
      case 'completed': return '#fc8181'; // red
      default: return '#a0aec0'; // gray
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'pre_draft': return 'Pre-Draft';
      case 'draft': return 'Draft en Curso';
      case 'in_season': return 'En Temporada';
      case 'completed': return 'Completada';
      default: return status;
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      backgroundColor: '#1a202c',
      padding: '20px',
    }}>
      <div style={{
        maxWidth: '1200px',
        margin: '0 auto',
      }}>
        {/* Header */}
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '30px',
        }}>
          <h1 style={{
            color: '#e2e8f0',
            fontSize: '32px',
            fontWeight: '700',
            margin: 0,
          }}>
            Unirse a una Liga
          </h1>
          <button
            onClick={() => navigate('/profile')}
            style={{
              padding: '10px 20px',
              backgroundColor: '#4a5568',
              color: '#e2e8f0',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              fontWeight: '600',
            }}
          >
            Volver al Perfil
          </button>
        </div>

        {/* Filtros de búsqueda */}
        <div style={{
          backgroundColor: '#2d3748',
          padding: '20px',
          borderRadius: '8px',
          marginBottom: '20px',
        }}>
          <div style={{
            display: 'grid',
            gridTemplateColumns: '1fr 1fr auto',
            gap: '15px',
            alignItems: 'end',
          }}>
            <div>
              <label style={{
                display: 'block',
                color: '#a0aec0',
                fontSize: '14px',
                marginBottom: '8px',
                fontWeight: '600',
              }}>
                Nombre de Liga
              </label>
              <input
                type="text"
                value={searchName}
                onChange={(e) => setSearchName(e.target.value)}
                placeholder="Buscar por nombre..."
                style={{
                  width: '100%',
                  padding: '10px',
                  backgroundColor: '#1a202c',
                  border: '1px solid #4a5568',
                  borderRadius: '6px',
                  color: '#e2e8f0',
<<<<<<< HEAD
=======
                  fontSize: '14px',
>>>>>>> main
                }}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              />
            </div>
            
            <div>
              <label style={{
                display: 'block',
                color: '#a0aec0',
                fontSize: '14px',
                marginBottom: '8px',
                fontWeight: '600',
              }}>
                Estado
              </label>
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                style={{
                  width: '100%',
                  padding: '10px',
                  backgroundColor: '#1a202c',
                  border: '1px solid #4a5568',
                  borderRadius: '6px',
                  color: '#e2e8f0',
                  fontSize: '14px',
                }}
              >
                <option value="">Todos</option>
                <option value="pre_draft">Pre-Draft</option>
                <option value="draft">Draft</option>
                <option value="in_season">En Temporada</option>
              </select>
            </div>

            <button
              onClick={handleSearch}
              disabled={loadingLeagues}
              style={{
                padding: '10px 30px',
                backgroundColor: '#63b3ed',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                cursor: loadingLeagues ? 'not-allowed' : 'pointer',
                fontWeight: '600',
                fontSize: '14px',
                opacity: loadingLeagues ? 0.6 : 1,
              }}
            >
              {loadingLeagues ? 'Buscando...' : 'Buscar'}
            </button>
          </div>
        </div>

        {/* Error general */}
        {error && !showModal && (
          <div style={{
            backgroundColor: '#fc8181',
            color: 'white',
            padding: '15px',
            borderRadius: '6px',
            marginBottom: '20px',
          }}>
            {error}
          </div>
        )}

        {/* Lista de ligas */}
        {loadingLeagues ? (
          <div style={{
            textAlign: 'center',
            padding: '40px',
            color: '#a0aec0',
          }}>
            Cargando ligas...
          </div>
        ) : leagues.length === 0 ? (
          <div style={{
            textAlign: 'center',
            padding: '40px',
            backgroundColor: '#2d3748',
            borderRadius: '8px',
            color: '#a0aec0',
          }}>
            No se encontraron ligas disponibles
          </div>
        ) : (
          <div style={{
            display: 'grid',
            gap: '15px',
          }}>
            {leagues.map((league) => (
              <div
                key={league.id}
                style={{
                  backgroundColor: '#2d3748',
                  padding: '20px',
                  borderRadius: '8px',
                  border: '1px solid #4a5568',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  transition: 'all 0.3s',
                  cursor: league.slots_available > 0 ? 'pointer' : 'default',
                }}
                onMouseEnter={(e) => {
                  if (league.slots_available > 0) {
                    e.currentTarget.style.borderColor = '#63b3ed';
                    e.currentTarget.style.transform = 'translateY(-2px)';
                  }
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.borderColor = '#4a5568';
                  e.currentTarget.style.transform = 'translateY(0)';
                }}
                onClick={() => handleSelectLeague(league)}
              >
                <div style={{ flex: 1 }}>
                  <h3 style={{
                    color: '#e2e8f0',
                    fontSize: '20px',
                    fontWeight: '600',
                    margin: '0 0 8px 0',
                  }}>
                    {league.name}
                  </h3>
                  {league.description && (
                    <p style={{
                      color: '#a0aec0',
                      fontSize: '14px',
                      margin: '0 0 12px 0',
                    }}>
                      {league.description}
                    </p>
                  )}
                  <div style={{
                    display: 'flex',
                    gap: '15px',
                    flexWrap: 'wrap',
                  }}>
                    <span style={{
                      display: 'inline-block',
                      padding: '4px 12px',
                      backgroundColor: getStatusBadgeColor(league.status),
                      color: 'white',
                      borderRadius: '12px',
                      fontSize: '12px',
                      fontWeight: '600',
                    }}>
                      {getStatusLabel(league.status)}
                    </span>
                    <span style={{
                      color: '#a0aec0',
                      fontSize: '14px',
                    }}>
                      🏆 {league.season_name}
                    </span>
                    <span style={{
                      color: '#a0aec0',
                      fontSize: '14px',
                    }}>
                      👥 {league.max_teams} equipos máx.
                    </span>
                  </div>
                </div>
                
                <div style={{
                  textAlign: 'center',
                  minWidth: '120px',
                }}>
                  <div style={{
                    fontSize: '32px',
                    fontWeight: '700',
                    color: league.slots_available > 0 ? '#68d391' : '#fc8181',
                  }}>
                    {league.slots_available}
                  </div>
                  <div style={{
                    fontSize: '12px',
                    color: '#a0aec0',
                    textTransform: 'uppercase',
                    letterSpacing: '0.5px',
                  }}>
                    Cupos Disponibles
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Modal para unirse */}
      {showModal && selectedLeague && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0, 0, 0, 0.8)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000,
          padding: '20px',
        }}>
          <div style={{
            backgroundColor: '#2d3748',
            borderRadius: '12px',
            width: '100%',
            maxWidth: '500px',
            maxHeight: '90vh',
            overflow: 'auto',
          }}>
            {/* Modal Header */}
            <div style={{
              backgroundColor: '#4a5568',
              padding: '20px',
              borderTopLeftRadius: '12px',
              borderTopRightRadius: '12px',
            }}>
              <h2 style={{
                color: '#e2e8f0',
                fontSize: '24px',
                fontWeight: '600',
                margin: 0,
              }}>
                Unirse a {selectedLeague.name}
              </h2>
            </div>

            {/* Modal Body */}
            <form onSubmit={handleSubmitJoin} style={{ padding: '20px' }}>
              {success && (
                <div style={{
                  backgroundColor: '#68d391',
                  color: 'white',
                  padding: '15px',
                  borderRadius: '6px',
                  marginBottom: '20px',
                  fontWeight: '600',
                }}>
                  ✓ {success}
                </div>
              )}

              {error && (
                <div style={{
                  backgroundColor: '#fc8181',
                  color: 'white',
                  padding: '15px',
                  borderRadius: '6px',
                  marginBottom: '20px',
                }}>
                  {error}
                </div>
              )}

              <div style={{ marginBottom: '20px' }}>
                <label style={{
                  display: 'block',
                  color: '#a0aec0',
                  fontSize: '14px',
                  marginBottom: '8px',
                  fontWeight: '600',
                }}>
                  Contraseña de la Liga *
                </label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  minLength={8}
                  maxLength={12}
                  placeholder="Ingresa la contraseña..."
                  style={{
                    width: '100%',
                    padding: '12px',
                    backgroundColor: '#1a202c',
                    border: '1px solid #4a5568',
                    borderRadius: '6px',
                    color: '#e2e8f0',
                    fontSize: '14px',
                  }}
                  disabled={loading}
                />
              </div>

              <div style={{ marginBottom: '20px' }}>
                <label style={{
                  display: 'block',
                  color: '#a0aec0',
                  fontSize: '14px',
                  marginBottom: '8px',
                  fontWeight: '600',
                }}>
                  Tu Alias en esta Liga *
                </label>
                <input
                  type="text"
                  value={userAlias}
                  onChange={(e) => setUserAlias(e.target.value)}
                  required
                  minLength={1}
                  maxLength={50}
                  placeholder="Ej: DragonMaster, ElCapitán..."
                  style={{
                    width: '100%',
                    padding: '12px',
                    backgroundColor: '#1a202c',
                    border: '1px solid #4a5568',
                    borderRadius: '6px',
                    color: '#e2e8f0',
                    fontSize: '14px',
                  }}
                  disabled={loading}
                />
                <small style={{
                  color: '#a0aec0',
                  fontSize: '12px',
                  display: 'block',
                  marginTop: '6px',
                }}>
                  Este alias debe ser único en la liga
                </small>
              </div>

              <div style={{ marginBottom: '20px' }}>
                <label style={{
                  display: 'block',
                  color: '#a0aec0',
                  fontSize: '14px',
                  marginBottom: '8px',
                  fontWeight: '600',
                }}>
<<<<<<< HEAD
                  Equipo de Fantasía
                </label>
                <input
                  type="text"
                  placeholder="Nombre del equipo"
                  value={fantasyName}
                  onChange={(e) => setFantasyName(e.target.value)}
                  required
                  style={{
                    width: '100%', padding: '12px', backgroundColor: '#1a202c',
                    border: '1px solid #4a5568', borderRadius: '6px', color: '#e2e8f0', fontSize: '14px'
                  }}
                  disabled={loading}
                />
                {/* City removed for fantasy teams */}
                <div style={{ height: 10 }} />
                <input
                  type="text"
                  placeholder="Imagen (URL opcional)"
                  value={fantasyImageUrl}
                  onChange={(e) => setFantasyImageUrl(e.target.value)}
                  style={{
                    width: '100%', padding: '12px', backgroundColor: '#1a202c',
                    border: '1px solid #4a5568', borderRadius: '6px', color: '#e2e8f0', fontSize: '14px'
                  }}
                  disabled={loading}
                />
                <div style={{ marginTop: 12 }}>
                  <label style={{ color: '#a0aec0', display: 'block', marginBottom: 6 }}>…o sube un archivo:</label>
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept=".png,.jpg,.jpeg,.webp"
                    disabled={loading || uploadingImage}
                    style={{ display: 'none' }}
                    onChange={async (e) => {
                      const file = e.target.files?.[0];
                      if (!file) return;
                      setUploadingImage(true);
                      setError('');
                      try {
                        const { image_url, thumbnail_url } = await uploadFantasyTeamImage(file);
                        setFantasyImageUrl(image_url);
                        setFantasyThumbUrl(thumbnail_url);
                        setUploadedFileName(file.name);
                      } catch (err: any) {
                        setError(err?.response?.data?.detail || 'No se pudo subir la imagen.');
                      } finally {
                        setUploadingImage(false);
                      }
                    }}
                  />
                  <button
                    type="button"
                    onClick={() => fileInputRef.current?.click()}
                    disabled={loading || uploadingImage}
                    style={{
                      width: '100%',
                      padding: '12px',
                      backgroundColor: '#2d3748',
                      color: '#e2e8f0',
                      border: '2px solid #4a5568',
                      borderRadius: '6px',
                      fontSize: '14px',
                      cursor: (loading || uploadingImage) ? 'not-allowed' : 'pointer',
                      transition: 'all 0.3s',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      gap: '8px'
                    }}
                    onMouseOver={(e) => (e.currentTarget.style.borderColor = '#63b3ed')}
                    onMouseOut={(e) => (e.currentTarget.style.borderColor = '#4a5568')}
                  >
                    {uploadedFileName ? uploadedFileName : (uploadingImage ? 'Subiendo…' : 'Elegir archivo')}
                  </button>
                </div>
                <div style={{
                  marginTop: 12,
                  height: 160,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  border: '2px dashed #4a5568',
                  borderRadius: 6,
                  backgroundColor: '#1a202c'
                }}>
                  {(fantasyThumbUrl || fantasyImageUrl) ? (
                    <img src={fantasyThumbUrl || fantasyImageUrl} style={{ maxWidth: 100, maxHeight: 100, borderRadius: 4 }} alt="Thumbnail Preview" />
                  ) : (
                    <span style={{ color: '#a0aec0' }}>Preview del thumbnail</span>
                  )}
                </div>
=======
                  Selecciona tu Equipo *
                </label>
                <select
                  value={selectedTeamId || ''}
                  onChange={(e) => setSelectedTeamId(Number(e.target.value))}
                  required
                  style={{
                    width: '100%',
                    padding: '12px',
                    backgroundColor: '#1a202c',
                    border: '1px solid #4a5568',
                    borderRadius: '6px',
                    color: '#e2e8f0',
                    fontSize: '14px',
                  }}
                  disabled={loading}
                >
                  <option value="">-- Selecciona un equipo --</option>
                  {teams.map((team) => (
                    <option key={team.id} value={team.id}>
                      {team.name} ({team.city})
                    </option>
                  ))}
                </select>
                <small style={{
                  color: '#a0aec0',
                  fontSize: '12px',
                  display: 'block',
                  marginTop: '6px',
                }}>
                  Solo se muestran equipos que no están en otra liga
                </small>
>>>>>>> main
              </div>

              {/* Buttons */}
              <div style={{
                display: 'flex',
                gap: '10px',
                marginTop: '30px',
              }}>
                <button
                  type="button"
                  onClick={handleCloseModal}
                  disabled={loading}
                  style={{
                    flex: 1,
                    padding: '12px',
                    backgroundColor: '#4a5568',
                    color: '#e2e8f0',
                    border: 'none',
                    borderRadius: '6px',
                    cursor: loading ? 'not-allowed' : 'pointer',
                    fontWeight: '600',
                    opacity: loading ? 0.6 : 1,
                  }}
                >
                  Cancelar
                </button>
                <button
                  type="submit"
<<<<<<< HEAD
                  disabled={loading || !password || !userAlias || fantasyName.trim().length < 2}
=======
                  disabled={loading || !password || !userAlias || !selectedTeamId}
>>>>>>> main
                  style={{
                    flex: 1,
                    padding: '12px',
                    backgroundColor: '#68d391',
                    color: 'white',
                    border: 'none',
                    borderRadius: '6px',
<<<<<<< HEAD
                    cursor: (loading || !password || !userAlias || fantasyName.trim().length < 2) ? 'not-allowed' : 'pointer',
                    fontWeight: '600',
                    opacity: (loading || !password || !userAlias || fantasyName.trim().length < 2) ? 0.6 : 1,
=======
                    cursor: (loading || !password || !userAlias || !selectedTeamId) ? 'not-allowed' : 'pointer',
                    fontWeight: '600',
                    opacity: (loading || !password || !userAlias || !selectedTeamId) ? 0.6 : 1,
>>>>>>> main
                  }}
                >
                  {loading ? 'Uniéndose...' : 'Unirse a la Liga'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default JoinLeague;
