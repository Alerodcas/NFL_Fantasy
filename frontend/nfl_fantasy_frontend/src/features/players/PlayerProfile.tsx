import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getPlayer, getPlayerNews } from '../../services/players';
import { getTeam } from '../../services/teams';
import PlayerNewsForm from './components/PlayerNewsForm';
import { useAuth } from '../../shared/hooks/useAuth';

export default function PlayerProfile() {
  const { id } = useParams();
  const playerId = id ? Number(id) : null;
  const [player, setPlayer] = useState<any | null>(null);
  const [team, setTeam] = useState<any | null>(null);
  const [news, setNews] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  const { user } = useAuth();

  const load = async () => {
    if (!playerId) return;
    setLoading(true);
    try {
      const p = await getPlayer(playerId);
      setPlayer(p);
      // load team if available
      if (p && p.team_id) {
        try {
          const t = await getTeam(p.team_id);
          setTeam(t);
        } catch (e) {
          console.warn('Could not load team for player', e);
          setTeam(null);
        }
      } else {
        setTeam(null);
      }
      const n = await getPlayerNews(playerId);
      setNews(n);
    } catch (e) {
      console.error('Error loading player/profile', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, [id]);

  if (!playerId) return <div style={{ padding: 20 }}>Player id required in path</div>;

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#1a202c', padding: 20 }}>
      <div style={{ maxWidth: 1000, margin: '0 auto' }}>
        <div style={{ background: '#2d3748', padding: 16, borderRadius: 8, border: '1px solid #4a5568', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h2 style={{ color: '#e2e8f0', margin: 0 }}>{player ? player.name : `Jugador #${playerId}`}</h2>
            <p style={{ color: '#a0aec0', margin: 0 }}>{player ? `Posición: ${player.position}` : ''}</p>
            {team && (
              <p style={{ color: '#a0aec0', margin: 0 }}>
                Equipo:{' '}
                <a
                  onClick={() => navigate(`/teams/${team.id}`)}
                  style={{ color: '#63b3ed', cursor: 'pointer', textDecoration: 'none', marginLeft: 6 }}
                >
                  {team.name}
                </a>
              </p>
            )}
            {!team && player && player.team_id && (
              <p style={{ color: '#a0aec0', margin: 0 }}>Equipo: ID {player.team_id}</p>
            )}
          </div>
          <div>
            <button
              onClick={() => navigate(user && user.role === 'admin' ? '/admin' : '/profile')}
              style={{ padding: '8px 12px', background: 'transparent', color: '#63b3ed', border: '1px solid #4a5568', borderRadius: 6, cursor: 'pointer' }}
            >
              Volver
            </button>
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 360px', gap: 16, marginTop: 16 }}>
          <div>
            <div style={{ background: '#2d3748', padding: 12, borderRadius: 8, border: '1px solid #4a5568' }}>
              <h3 style={{ color: '#e2e8f0', marginTop: 0 }}>Noticias</h3>
              {loading && <div style={{ color: '#a0aec0' }}>Cargando...</div>}
              {!loading && news.length === 0 && <div style={{ color: '#a0aec0' }}>No hay noticias para este jugador.</div>}
              {!loading && news.map(n => (
                <div key={n.id} style={{ marginBottom: 12, padding: 10, background: '#1f2937', borderRadius: 6 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <strong style={{ color: '#e2e8f0' }}>{n.summary}</strong>
                    <span style={{ color: '#a0aec0', fontSize: 12 }}>{new Date(n.created_at).toLocaleString()}</span>
                  </div>
                  <div style={{ color: '#cbd5e1', marginTop: 6 }}>{n.text}</div>
                  {n.is_injury && <div style={{ marginTop: 8, color: '#f6ad55' }}>Lesión: {n.injury_type}</div>}
                </div>
              ))}
            </div>
          </div>

          <div>
            <div style={{ background: '#2d3748', padding: 12, borderRadius: 8, border: '1px solid #4a5568' }}>
              <h4 style={{ color: '#e2e8f0', marginTop: 0 }}>Estado</h4>
              {player ? (
                (() => {
                  // Prefer the latest news to determine visible status
                  const latest = news && news.length > 0 ? news[0] : null;
                  const isActive = !!player.is_active;

                  const INJURY_LABELS: Record<string, string> = {
                    O: 'Fuera (O): No jugará',
                    D: 'Dudoso (D): Muy poco probable que juegue',
                    Q: 'Cuestionable (Q): Probabilidad ~50%',
                    P: 'Probable (P): Probablemente juega',
                    FP: 'Participación Plena (FP): Juega (práctica completa)',
                    IR: 'Reserva de Lesionados (IR): Fuera por periodo extendido',
                    PUP: 'PUP: Incapaz físicamente de jugar',
                    SUS: 'Suspendido (SUS): No elegible por sanción',
                  };

                  if (!isActive) {
                    return <p style={{ color: '#f56565', fontWeight: 700 }}>Inactivo</p>;
                  }

                  if (latest) {
                    if (latest.is_injury) {
                      const label = INJURY_LABELS[latest.injury_type] || latest.injury_type || '';
                      return (
                        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                          <span style={{ padding: '6px 10px', background: '#f6ad55', color: '#1a202c', borderRadius: 6, fontWeight: 700 }}>Está lesionado</span>
                          <span style={{ color: '#a0aec0' }}>{label}</span>
                        </div>
                      );
                    }
                    // latest news exists but not an injury
                    return <p style={{ color: '#68d391', fontWeight: 700 }}>Está activo y juega</p>;
                  }

                  // fallback to stored visible_designation if no news
                  const code = player.visible_designation;
                  if (code) {
                    const label = INJURY_LABELS[code] || code;
                    return (
                      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <span style={{ padding: '6px 10px', background: '#f6ad55', color: '#1a202c', borderRadius: 6, fontWeight: 700 }}>Está lesionado</span>
                        <span style={{ color: '#a0aec0' }}>{label}</span>
                      </div>
                    );
                  }

                  return <p style={{ color: '#68d391', fontWeight: 700 }}>Está activo y juega</p>;
                })()
              ) : (
                <p style={{ color: '#a0aec0' }}>N/A</p>
              )}
            </div>
            <div style={{ height: 12 }} />
            {user && user.role === 'admin' ? (
              <PlayerNewsForm playerId={playerId} onCreated={() => load()} />
            ) : (
              <div style={{ color: '#a0aec0', fontSize: 14 }}>Solo los administradores pueden publicar noticias.</div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
