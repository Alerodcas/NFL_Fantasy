import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../shared/hooks/useAuth';
import { useEffect, useState } from 'react';
import axios from 'axios';

interface User {
  id: number;
  name: string;
  email: string;
  alias: string;
  role: string;
}

export default function AdminProfile() {
  const navigate = useNavigate();
  const { token } = useAuth();
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadUser = async () => {
      try {
        const storedToken = localStorage.getItem('token') || token;
        if (!storedToken) {
          navigate('/login');
          return;
        }

        const response = await axios.get('http://localhost:8000/users/me/', {
          headers: { Authorization: `Bearer ${storedToken}` }
        });

        console.log('AdminProfile - User:', response.data);
        
        if (response.data.role !== 'admin') {
          console.log('Not admin, redirecting to profile');
          navigate('/profile');
        } else {
          setUser(response.data);
        }
      } catch (error) {
        console.error('Error loading user:', error);
        navigate('/login');
      } finally {
        setLoading(false);
      }
    };

    loadUser();
  }, [token, navigate]);

  if (loading) {
    return (
      <div style={{ minHeight: '100vh', backgroundColor: '#1a202c', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div style={{ color: '#e2e8f0', fontSize: 18 }}>Cargando...</div>
      </div>
    );
  }

  if (!user) {
    return null;
  }

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#1a202c', padding: 20 }}>
      <div style={{ maxWidth: 1100, margin: '0 auto' }}>
        {/* Header */}
        <div style={{
          backgroundColor: '#2d3748',
          borderRadius: 12,
          border: '1px solid #4a5568',
          padding: 24,
          marginBottom: 20
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 16, flexWrap: 'wrap' }}>
            <div>
              <h1 style={{ color: '#e2e8f0', fontSize: 28, fontWeight: 700, margin: 0 }}>Panel de Administración</h1>
              <p style={{ color: '#a0aec0', marginTop: 6 }}>Bienvenido, {user.alias || user.name}</p>
            </div>
            <div>
              <span style={{ padding: '6px 12px', backgroundColor: '#9b2c2c', color: '#fff', borderRadius: 999, fontSize: 12, fontWeight: 700 }}>
                Administrador
              </span>
            </div>
          </div>
        </div>

        {/* Actions */}
        <div style={{ display: 'grid', gap: 16, gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))' }}>
          {/* Temporadas */}
          <div style={{ backgroundColor: '#2d3748', border: '1px solid #4a5568', borderRadius: 12, padding: 20 }}>
            <h3 style={{ color: '#e2e8f0', fontSize: 18, fontWeight: 600, margin: '0 0 6px 0' }}>Gestión de Temporadas</h3>
            <p style={{ color: '#a0aec0', fontSize: 14, margin: '0 0 16px 0' }}>Crear y administrar temporadas de la NFL</p>
            <button
              onClick={() => navigate('/admin/seasons/create')}
              style={{
                width: '100%', padding: '12px', backgroundColor: '#63b3ed', color: 'white',
                border: 'none', borderRadius: 6, fontWeight: 600, cursor: 'pointer'
              }}
            >
              Crear Temporada
            </button>
          </div>

          {/* Equipos reales */}
          <div style={{ backgroundColor: '#2d3748', border: '1px solid #4a5568', borderRadius: 12, padding: 20 }}>
            <h3 style={{ color: '#e2e8f0', fontSize: 18, fontWeight: 600, margin: '0 0 6px 0' }}>Gestión de Equipos</h3>
            <p style={{ color: '#a0aec0', fontSize: 14, margin: '0 0 16px 0' }}>Crear y administrar equipos (reales) del sistema</p>
            <button
              onClick={() => navigate('/teams/new')}
              style={{
                width: '100%', padding: '12px', backgroundColor: '#63b3ed', color: 'white',
                border: 'none', borderRadius: 6, fontWeight: 600, cursor: 'pointer'
              }}
            >
              Crear Equipo
            </button>
          </div>
        </div>

        {/* Admin info */}
        <div style={{ marginTop: 20, backgroundColor: '#2d3748', border: '1px solid #4a5568', borderRadius: 12, padding: 20 }}>
          <h2 style={{ color: '#e2e8f0', fontSize: 20, fontWeight: 700, margin: '0 0 12px 0' }}>Información del Administrador</h2>
          <div style={{ display: 'grid', gap: 12, gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))' }}>
            <div>
              <p style={{ color: '#a0aec0', fontSize: 12, textTransform: 'uppercase', letterSpacing: 0.5, margin: '0 0 4px 0' }}>Usuario</p>
              <p style={{ color: '#e2e8f0', fontSize: 16, margin: 0 }}>{user.name}</p>
            </div>
            <div>
              <p style={{ color: '#a0aec0', fontSize: 12, textTransform: 'uppercase', letterSpacing: 0.5, margin: '0 0 4px 0' }}>Email</p>
              <p style={{ color: '#e2e8f0', fontSize: 16, margin: 0 }}>{user.email}</p>
            </div>
          </div>
        </div>

        {/* Back link */}
        <div style={{ marginTop: 20, textAlign: 'center' }}>
          <button
            onClick={() => navigate('/profile')}
            style={{ color: '#63b3ed', background: 'transparent', border: 'none', fontWeight: 600, cursor: 'pointer' }}
          >
            Ver perfil de usuario normal
          </button>
        </div>
      </div>
    </div>
  );
}
