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
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-xl">Cargando...</div>
      </div>
    );
  }

  if (!user) {
    return null;
  }

  return (
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
                Administrador
              </span>
            </div>
          </div>
        </div>

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
            >
              Crear Temporada
            </button>
          </div>

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
            </div>
          </div>
        </div>

        {/* Volver al perfil normal */}
        <div className="mt-6 text-center">
          <button
            onClick={() => navigate('/profile')}
            className="text-blue-600 hover:text-blue-800 font-semibold"
          >
            Ver perfil de usuario normal
          </button>
        </div>
      </div>
    </div>
  );
}
