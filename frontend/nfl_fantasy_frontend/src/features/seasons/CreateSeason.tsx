import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

interface Week {
  week_number: number;
  start_date: string;
  end_date: string;
}

interface FormData {
  name: string;
  week_count: number;
  start_date: string;
  end_date: string;
  is_current: boolean;
}

export default function CreateSeason() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  const [formData, setFormData] = useState<FormData>({
    name: '',
    week_count: 18,
    start_date: '',
    end_date: '',
    is_current: false
  });

  const [weeks, setWeeks] = useState<Week[]>([]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type, checked } = e.target;
    const newValue = type === 'checkbox' ? checked : value;
    setFormData(prev => ({
      ...prev,
      [name]: newValue
    }));

    // Validación en tiempo real para fechas
    if (name === 'start_date' || name === 'end_date') {
      const currentFormData = { ...formData, [name]: newValue };
      const startDate = new Date(currentFormData.start_date);
      const endDate = new Date(currentFormData.end_date);
      const today = new Date();
      today.setHours(0, 0, 0, 0);

      if (endDate <= startDate) {
        setError('La fecha de fin debe ser posterior a la fecha de inicio');
      } else if (endDate < today) {
        setError('La fecha de fin no puede estar en el pasado');
      } else if (weeks.length > 0) {
        const lastWeekEndDate = new Date(weeks[weeks.length - 1].end_date);
        if (endDate < lastWeekEndDate) {
          setError('La fecha de fin debe ser posterior o igual a la fecha de fin de la última semana generada');
        } else {
          setError(''); // Limpiar error si todo está bien
        }
      } else {
        setError(''); // Limpiar error si todo está bien
      }
    }
  };

  const generateWeeks = () => {
    if (!formData.start_date || !formData.week_count) {
      setError('Por favor ingrese fecha de inicio y cantidad de semanas');
      return;
    }

    const startDate = new Date(formData.start_date);
    const generatedWeeks: Week[] = [];

    for (let i = 0; i < parseInt(String(formData.week_count)); i++) {
      const weekStart = new Date(startDate);
      weekStart.setDate(startDate.getDate() + (i * 7));
      
      const weekEnd = new Date(weekStart);
      weekEnd.setDate(weekStart.getDate() + 6);

      generatedWeeks.push({
        week_number: i + 1,
        start_date: weekStart.toISOString().split('T')[0],
        end_date: weekEnd.toISOString().split('T')[0]
      });
    }

    setWeeks(generatedWeeks);
    
    // Validar fecha fin después de generar semanas
    if (formData.end_date) {
      const endDate = new Date(formData.end_date);
      const lastWeekEndDate = new Date(generatedWeeks[generatedWeeks.length - 1].end_date);
      if (endDate < lastWeekEndDate) {
        setError('La fecha de fin debe ser posterior o igual a la fecha de fin de la última semana generada');
      } else {
        setError('');
      }
    } else {
      setError('');
    }
  };

  const handleWeekChange = (index: number, field: keyof Week, value: string | number) => {
    const newWeeks = [...weeks];
    newWeeks[index] = { ...newWeeks[index], [field]: value };
    setWeeks(newWeeks);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    // Validaciones
    const startDate = new Date(formData.start_date);
    const endDate = new Date(formData.end_date);
    const today = new Date();
    today.setHours(0, 0, 0, 0); // Reset time to start of day

    if (endDate <= startDate) {
      setError('La fecha de fin debe ser posterior a la fecha de inicio');
      setLoading(false);
      return;
    }

    // Validar que no haya otra temporada actual si se marca como actual
    if (formData.is_current) {
      try {
        const token = localStorage.getItem('token');
        const seasonsResponse = await axios.get('http://localhost:8000/api/seasons/', {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });
        
        const existingCurrentSeason = seasonsResponse.data.find((season: any) => season.is_current);
        if (existingCurrentSeason) {
          setError(`Ya existe una temporada actual: ${existingCurrentSeason.name}. Desmarca la opción "Marcar como temporada actual" o cambia la temporada existente.`);
          setLoading(false);
          return;
        }
      } catch (err: any) {
        console.error('Error checking existing seasons:', err);
        // Si no podemos verificar, permitimos continuar pero mostramos una advertencia
        console.warn('No se pudo verificar temporadas existentes, procediendo con la creación...');
      }
    }

    try {
      const token = localStorage.getItem('token');
      const payload = {
        ...formData,
        week_count: parseInt(String(formData.week_count)),
        weeks: weeks
      };

      await axios.post('http://localhost:8000/api/seasons/', payload, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      alert('Temporada creada exitosamente');
<<<<<<< HEAD
      navigate('/admin');
=======
      navigate('/admin/seasons');
>>>>>>> main
    } catch (err: any) {
      console.error('Error creating season:', err);
      setError(err.response?.data?.detail || 'Error al crear la temporada');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      backgroundColor: '#1a202c',
      padding: '20px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center'
    }}>
      <div style={{
        width: '100%',
        maxWidth: '800px',
        margin: '0 auto',
        backgroundColor: '#2d3748',
        borderRadius: '12px',
        boxShadow: '0 4px 20px rgba(0, 0, 0, 0.2)',
        overflow: 'hidden'
      }}>
        <div style={{
          backgroundColor: '#4a5568',
          color: '#e2e8f0',
          padding: '30px',
          textAlign: 'center'
        }}>
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: '20px'
          }}>
            <h1 style={{
              margin: '0',
              fontSize: '28px',
              fontWeight: '600'
            }}>
              Crear Nueva Temporada
            </h1>
            <button
              onClick={() => navigate('/admin')}
              style={{
                color: '#a0aec0',
                background: 'none',
                border: 'none',
                cursor: 'pointer',
                fontSize: '16px'
              }}
            >
              Volver
            </button>
          </div>
        </div>

        <div style={{ padding: '40px' }}>
          {error && (
            <div style={{
              backgroundColor: 'rgba(255, 100, 100, 0.1)',
              color: '#ff8a8a',
              padding: '12px',
              borderRadius: '6px',
              marginBottom: '20px',
              border: '1px solid #c33'
            }}>
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit}>
            {/* Información Básica */}
            <div style={{ marginBottom: '30px' }}>
              <h2 style={{
                color: '#e2e8f0',
                fontSize: '20px',
                fontWeight: '600',
                marginBottom: '20px'
              }}>
                Información de la Temporada
              </h2>
              
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
                gap: '20px'
              }}>
                <div>
                  <label style={{
                    display: 'block',
                    marginBottom: '8px',
                    fontWeight: '500',
                    color: '#a0aec0'
                  }}>
                    Nombre de la Temporada *
                  </label>
                  <input
                    type="text"
                    name="name"
                    value={formData.name}
                    onChange={handleInputChange}
                    required
                    maxLength={100}
                    style={{
                      width: '100%',
                      padding: '12px',
                      border: '2px solid #4a5568',
                      borderRadius: '6px',
                      fontSize: '16px',
                      transition: 'border-color 0.3s',
                      outline: 'none',
                      backgroundColor: '#1a202c',
                      color: '#e2e8f0'
                    }}
                    onFocus={(e) => e.target.style.borderColor = '#63b3ed'}
                    onBlur={(e) => e.target.style.borderColor = '#4a5568'}
                    placeholder="Ej: NFL 2024-2025"
                  />
                </div>

                <div>
                  <label style={{
                    display: 'block',
                    marginBottom: '8px',
                    fontWeight: '500',
                    color: '#a0aec0'
                  }}>
                    Cantidad de Semanas *
                  </label>
                  <input
                    type="number"
                    name="week_count"
                    value={formData.week_count}
                    onChange={handleInputChange}
                    required
                    min={1}
                    max={52}
                    style={{
                      width: '100%',
                      padding: '12px',
                      border: '2px solid #4a5568',
                      borderRadius: '6px',
                      fontSize: '16px',
                      transition: 'border-color 0.3s',
                      outline: 'none',
                      backgroundColor: '#1a202c',
                      color: '#e2e8f0'
                    }}
                    onFocus={(e) => e.target.style.borderColor = '#63b3ed'}
                    onBlur={(e) => e.target.style.borderColor = '#4a5568'}
                  />
                </div>

                <div>
                  <label style={{
                    display: 'block',
                    marginBottom: '8px',
                    fontWeight: '500',
                    color: '#a0aec0'
                  }}>
                    Fecha de Inicio *
                  </label>
                  <input
                    type="date"
                    name="start_date"
                    value={formData.start_date}
                    onChange={handleInputChange}
                    required
                    style={{
                      width: '100%',
                      padding: '12px',
                      border: '2px solid #4a5568',
                      borderRadius: '6px',
                      fontSize: '16px',
                      transition: 'border-color 0.3s',
                      outline: 'none',
                      backgroundColor: '#1a202c',
                      color: '#e2e8f0'
                    }}
                    onFocus={(e) => e.target.style.borderColor = '#63b3ed'}
                    onBlur={(e) => e.target.style.borderColor = '#4a5568'}
                  />
                </div>

                <div>
                  <label style={{
                    display: 'block',
                    marginBottom: '8px',
                    fontWeight: '500',
                    color: '#a0aec0'
                  }}>
                    Fecha de Fin *
                  </label>
                  <input
                    type="date"
                    name="end_date"
                    value={formData.end_date}
                    onChange={handleInputChange}
                    required
                    style={{
                      width: '100%',
                      padding: '12px',
                      border: '2px solid #4a5568',
                      borderRadius: '6px',
                      fontSize: '16px',
                      transition: 'border-color 0.3s',
                      outline: 'none',
                      backgroundColor: '#1a202c',
                      color: '#e2e8f0'
                    }}
                    onFocus={(e) => e.target.style.borderColor = '#63b3ed'}
                    onBlur={(e) => e.target.style.borderColor = '#4a5568'}
                  />
                </div>
              </div>

              <div style={{ marginTop: '20px' }}>
                <label style={{
                  display: 'flex',
                  alignItems: 'center',
                  color: '#a0aec0'
                }}>
                  <input
                    type="checkbox"
                    name="is_current"
                    checked={formData.is_current}
                    onChange={handleInputChange}
                    style={{
                      width: '16px',
                      height: '16px',
                      marginRight: '8px',
                      accentColor: '#63b3ed'
                    }}
                  />
                  Marcar como temporada actual
                </label>
              </div>
            </div>

            {/* Generar Semanas */}
            <div style={{ marginBottom: '30px' }}>
              <h2 style={{
                color: '#e2e8f0',
                fontSize: '20px',
                fontWeight: '600',
                marginBottom: '20px'
              }}>
                Configuración de Semanas
              </h2>
              <button
                type="button"
                onClick={generateWeeks}
                style={{
                  padding: '12px 24px',
                  backgroundColor: '#68d391',
                  color: '#1a202c',
                  border: 'none',
                  borderRadius: '6px',
                  fontSize: '16px',
                  fontWeight: '600',
                  cursor: 'pointer',
                  transition: 'background-color 0.3s'
                }}
                onMouseOver={(e) => (e.target as HTMLElement).style.backgroundColor = '#5cb85c'}
                onMouseOut={(e) => (e.target as HTMLElement).style.backgroundColor = '#68d391'}
              >
                Generar Semanas Automáticamente
              </button>
            </div>

            {/* Lista de Semanas */}
            {weeks.length > 0 && (
              <div>
                <h2 style={{
                  color: '#e2e8f0',
                  fontSize: '20px',
                  fontWeight: '600',
                  marginBottom: '20px'
                }}>
                  Semanas ({weeks.length})
                </h2>
                <div style={{
                  maxHeight: '400px',
                  overflowY: 'auto',
                  display: 'grid',
                  gap: '15px'
                }}>
                  {weeks.map((week, index) => (
                    <div key={index} style={{
                      backgroundColor: '#1a202c',
                      padding: '20px',
                      borderRadius: '8px',
                      border: '1px solid #4a5568'
                    }}>
                      <div style={{
                        display: 'grid',
                        gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
                        gap: '15px'
                      }}>
                        <div>
                          <label style={{
                            display: 'block',
                            fontWeight: '600',
                            color: '#a0aec0',
                            marginBottom: '8px',
                            fontSize: '14px',
                            textTransform: 'uppercase',
                            letterSpacing: '0.5px'
                          }}>
                            Semana #{week.week_number}
                          </label>
                          <input
                            type="number"
                            value={week.week_number}
                            style={{
                              width: '100%',
                              padding: '10px',
                              border: '2px solid #4a5568',
                              borderRadius: '6px',
                              fontSize: '14px',
                              backgroundColor: '#2d3748',
                              color: '#e2e8f0'
                            }}
                            readOnly
                          />
                        </div>
                        <div>
                          <label style={{
                            display: 'block',
                            fontWeight: '600',
                            color: '#a0aec0',
                            marginBottom: '8px',
                            fontSize: '14px',
                            textTransform: 'uppercase',
                            letterSpacing: '0.5px'
                          }}>
                            Fecha Inicio
                          </label>
                          <input
                            type="date"
                            value={week.start_date}
                            onChange={(e) => handleWeekChange(index, 'start_date', e.target.value)}
                            style={{
                              width: '100%',
                              padding: '10px',
                              border: '2px solid #4a5568',
                              borderRadius: '6px',
                              fontSize: '14px',
                              transition: 'border-color 0.3s',
                              outline: 'none',
                              backgroundColor: '#1a202c',
                              color: '#e2e8f0'
                            }}
                            onFocus={(e) => e.target.style.borderColor = '#63b3ed'}
                            onBlur={(e) => e.target.style.borderColor = '#4a5568'}
                          />
                        </div>
                        <div>
                          <label style={{
                            display: 'block',
                            fontWeight: '600',
                            color: '#a0aec0',
                            marginBottom: '8px',
                            fontSize: '14px',
                            textTransform: 'uppercase',
                            letterSpacing: '0.5px'
                          }}>
                            Fecha Fin
                          </label>
                          <input
                            type="date"
                            value={week.end_date}
                            onChange={(e) => handleWeekChange(index, 'end_date', e.target.value)}
                            style={{
                              width: '100%',
                              padding: '10px',
                              border: '2px solid #4a5568',
                              borderRadius: '6px',
                              fontSize: '14px',
                              transition: 'border-color 0.3s',
                              outline: 'none',
                              backgroundColor: '#1a202c',
                              color: '#e2e8f0'
                            }}
                            onFocus={(e) => e.target.style.borderColor = '#63b3ed'}
                            onBlur={(e) => e.target.style.borderColor = '#4a5568'}
                          />
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Botones */}
            <div style={{
              display: 'flex',
              justifyContent: 'flex-end',
              gap: '15px',
              marginTop: '30px'
            }}>
              <button
                type="button"
                onClick={() => navigate('/admin')}
                style={{
                  padding: '12px 24px',
                  border: '2px solid #4a5568',
                  borderRadius: '6px',
                  fontSize: '16px',
                  fontWeight: '600',
                  cursor: 'pointer',
                  transition: 'all 0.3s',
                  backgroundColor: 'transparent',
                  color: '#a0aec0'
                }}
                onMouseOver={(e) => {
                  (e.target as HTMLElement).style.backgroundColor = '#4a5568';
                  (e.target as HTMLElement).style.color = '#e2e8f0';
                }}
                onMouseOut={(e) => {
                  (e.target as HTMLElement).style.backgroundColor = 'transparent';
                  (e.target as HTMLElement).style.color = '#a0aec0';
                }}
              >
                Cancelar
              </button>
              <button
                type="submit"
                disabled={loading || weeks.length === 0}
                style={{
                  padding: '12px 24px',
                  backgroundColor: loading || weeks.length === 0 ? '#4a5568' : '#63b3ed',
                  color: loading || weeks.length === 0 ? '#a0aec0' : '#1a202c',
                  border: 'none',
                  borderRadius: '6px',
                  fontSize: '16px',
                  fontWeight: '600',
                  cursor: loading || weeks.length === 0 ? 'not-allowed' : 'pointer',
                  transition: 'background-color 0.3s'
                }}
              >
                {loading ? 'Creando...' : 'Crear Temporada'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
