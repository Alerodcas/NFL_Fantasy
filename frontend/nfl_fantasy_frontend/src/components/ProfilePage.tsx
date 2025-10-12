import React from 'react';
import { useAuth } from '../hooks/useAuth';
import { useNavigate } from 'react-router-dom';
import { Link } from 'react-router-dom';


const ProfilePage = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  if (!user) {
    return (
      <div style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        backgroundColor: '#f5f5f5'
      }}>
        <div style={{
          backgroundColor: 'white',
          padding: '40px',
          borderRadius: '12px',
          boxShadow: '0 4px 20px rgba(0, 0, 0, 0.1)',
          textAlign: 'center'
        }}>
          <p style={{ color: '#666', fontSize: '18px' }}>Cargando perfil...</p>
        </div>
      </div>
    );
  }

  const handleCreateTeam = () => {
    navigate('/teams/new');
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div style={{
      minHeight: '100vh',
      backgroundColor: '#f5f5f5',
      padding: '20px'
    }}>
      <div style={{
        maxWidth: '600px',
        margin: '0 auto',
        backgroundColor: 'white',
        borderRadius: '12px',
        boxShadow: '0 4px 20px rgba(0, 0, 0, 0.1)',
        overflow: 'hidden'
      }}>
        {/* Header */}
        <div style={{
          backgroundColor: '#007bff',
          color: 'white',
          padding: '30px',
          textAlign: 'center'
        }}>
          <h2 style={{
            margin: '0 0 10px 0',
            fontSize: '28px',
            fontWeight: '600'
          }}>
            Perfil de Usuario
          </h2>
          <p style={{
            margin: '0',
            opacity: '0.9',
            fontSize: '16px'
          }}>
            Bienvenido, {user.name}
          </p>
        </div>

        {/* Content */}
        <div style={{ padding: '40px' }}>
          <div style={{
            display: 'grid',
            gap: '20px',
            marginBottom: '30px'
          }}>
            <div style={{
              padding: '20px',
              backgroundColor: '#f8f9fa',
              borderRadius: '8px',
              border: '1px solid #e9ecef'
            }}>
              <label style={{
                display: 'block',
                fontWeight: '600',
                color: '#495057',
                marginBottom: '8px',
                fontSize: '14px',
                textTransform: 'uppercase',
                letterSpacing: '0.5px'
              }}>
                ID de Usuario
              </label>
              <p style={{
                margin: '0',
                fontSize: '18px',
                color: '#212529'
              }}>
                {user.id}
              </p>
            </div>

            <div style={{
              padding: '20px',
              backgroundColor: '#f8f9fa',
              borderRadius: '8px',
              border: '1px solid #e9ecef'
            }}>
              <label style={{
                display: 'block',
                fontWeight: '600',
                color: '#495057',
                marginBottom: '8px',
                fontSize: '14px',
                textTransform: 'uppercase',
                letterSpacing: '0.5px'
              }}>
                Nombre Completo
              </label>
              <p style={{
                margin: '0',
                fontSize: '18px',
                color: '#212529'
              }}>
                {user.name}
              </p>
            </div>

            <div style={{
              padding: '20px',
              backgroundColor: '#f8f9fa',
              borderRadius: '8px',
              border: '1px solid #e9ecef'
            }}>
              <label style={{
                display: 'block',
                fontWeight: '600',
                color: '#495057',
                marginBottom: '8px',
                fontSize: '14px',
                textTransform: 'uppercase',
                letterSpacing: '0.5px'
              }}>
                Correo Electrónico
              </label>
              <p style={{
                margin: '0',
                fontSize: '18px',
                color: '#212529'
              }}>
                {user.email}
              </p>
            </div>

            <div style={{
              padding: '20px',
              backgroundColor: '#f8f9fa',
              borderRadius: '8px',
              border: '1px solid #e9ecef'
            }}>
              <label style={{
                display: 'block',
                fontWeight: '600',
                color: '#495057',
                marginBottom: '8px',
                fontSize: '14px',
                textTransform: 'uppercase',
                letterSpacing: '0.5px'
              }}>
                Alias
              </label>
              <p style={{
                margin: '0',
                fontSize: '18px',
                color: '#212529'
              }}>
                {user.alias}
              </p>
            </div>

            <div style={{
              padding: '20px',
              backgroundColor: '#f8f9fa',
              borderRadius: '8px',
              border: '1px solid #e9ecef'
            }}>
              <label style={{
                display: 'block',
                fontWeight: '600',
                color: '#495057',
                marginBottom: '8px',
                fontSize: '14px',
                textTransform: 'uppercase',
                letterSpacing: '0.5px'
              }}>
                Rol
              </label>
              <p style={{
                margin: '0',
                fontSize: '18px',
                color: '#212529'
              }}>
                {user.role}
              </p>
            </div>
          </div>

            {/* Botón para crear equipo */}
            <button
              onClick={handleCreateTeam}
              style={{
                width: '100%',
                padding: '14px',
                backgroundColor: '#007bff',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                fontSize: '16px',
                fontWeight: '600',
                cursor: 'pointer',
                transition: 'background-color 0.3s',
                marginBottom: '15px'
              }}
              onMouseOver={(e) => (e.target as HTMLButtonElement).style.backgroundColor = '#0056b3'}
              onMouseOut={(e) => (e.target as HTMLButtonElement).style.backgroundColor = '#007bff'}
            >
              Crear Equipo
            </button>

            {/* Botón para cerrar sesión */}
            <button
              onClick={handleLogout}
              style={{
                width: '100%',
                padding: '14px',
                backgroundColor: '#dc3545',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                fontSize: '16px',
                fontWeight: '600',
                cursor: 'pointer',
                transition: 'background-color 0.3s'
              }}
              onMouseOver={(e) => (e.target as HTMLButtonElement).style.backgroundColor = '#c82333'}
              onMouseOut={(e) => (e.target as HTMLButtonElement).style.backgroundColor = '#dc3545'}
            >
              Cerrar Sesión
            </button>
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;