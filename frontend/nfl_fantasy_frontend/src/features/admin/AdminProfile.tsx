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
<<<<<<< HEAD
      <div style={{ minHeight: '100vh', backgroundColor: '#1a202c', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div style={{ color: '#e2e8f0', fontSize: 18 }}>Cargando...</div>
=======
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-xl">Cargando...</div>
>>>>>>> main
      </div>
    );
  }

  if (!user) {
    return null;
  }

  return (
<<<<<<< HEAD
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
=======
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                Panel de Administración
              </h1>
              <p className="mt-2 text-gray-600">
                Bienvenido, {user.alias || user.name}
              </p>
            </div>
            <div className="flex items-center space-x-2">
              <span className="px-3 py-1 bg-red-100 text-red-800 rounded-full text-sm font-semibold">
>>>>>>> main
                Administrador
              </span>
            </div>
          </div>
        </div>

<<<<<<< HEAD
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
=======
        {/* Admin Actions Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          
          {/* Gestión de Temporadas */}
          <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Gestión de Temporadas
            </h3>
            <p className="text-gray-600 text-sm mb-4">
              Crear y administrar temporadas de la NFL
            </p>
            <button
              onClick={() => navigate('/admin/seasons/create')}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded-lg transition-colors"
>>>>>>> main
            >
              Crear Temporada
            </button>
          </div>

<<<<<<< HEAD
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

          {/* Jugadores */}
          <div style={{ backgroundColor: '#2d3748', border: '1px solid #4a5568', borderRadius: 12, padding: 20 }}>
            <h3 style={{ color: '#e2e8f0', fontSize: 18, fontWeight: 600, margin: '0 0 6px 0' }}>Gestión de Jugadores</h3>
            <p style={{ color: '#a0aec0', fontSize: 14, margin: '0 0 16px 0' }}>Crear y administrar jugadores asociados a equipos</p>
            <button
              onClick={() => navigate('/players/new')}
              style={{
                width: '100%', padding: '12px', backgroundColor: '#63b3ed', color: 'white',
                border: 'none', borderRadius: 6, fontWeight: 600, cursor: 'pointer'
              }}
            >
              Crear Jugador
            </button>
          </div>

          {/* Creación batch de jugadores */}
          <div style={{ backgroundColor: '#2d3748', border: '1px solid #4a5568', borderRadius: 12, padding: 20 }}>
            <h3 style={{ color: '#e2e8f0', fontSize: 18, fontWeight: 600, margin: '0 0 6px 0' }}>
              Creación batch de jugadores
            </h3>
            <p style={{ color: '#a0aec0', fontSize: 14, margin: '0 0 16px 0' }}>
              Creación batch de jugadores NFL por archivo JSON
            </p>
            <button
              onClick={() => navigate('/players/batch')}
              style={{
                width: '100%', padding: '12px', backgroundColor: '#63b3ed', color: 'white',
                border: 'none', borderRadius: 6, fontWeight: 600, cursor: 'pointer'
              }}
            >
              Cargar jugadores batch
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
=======
        </div>

        {/* Quick Stats */}
        <div className="mt-6 bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Información del Administrador
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-gray-600">Usuario</p>
              <p className="text-lg font-semibold text-gray-900">{user.name}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Email</p>
              <p className="text-lg font-semibold text-gray-900">{user.email}</p>
>>>>>>> main
            </div>
          </div>
        </div>

<<<<<<< HEAD
        {/* Back link */}
        <div style={{ marginTop: 20, textAlign: 'center' }}>
          <button
            onClick={() => navigate('/profile')}
            style={{ color: '#63b3ed', background: 'transparent', border: 'none', fontWeight: 600, cursor: 'pointer' }}
=======
        {/* Volver al perfil normal */}
        <div className="mt-6 text-center">
          <button
            onClick={() => navigate('/profile')}
            className="text-blue-600 hover:text-blue-800 font-semibold"
>>>>>>> main
          >
            Ver perfil de usuario normal
          </button>
        </div>
      </div>
    </div>
  );
}
