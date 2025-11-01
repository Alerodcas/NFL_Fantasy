import React, { useEffect, useState } from 'react';
import { useAuth } from '../../../shared/hooks/useAuth';
import { useNavigate } from 'react-router-dom';

const ProfilePage = () => {
	const { user, logout } = useAuth();
	const navigate = useNavigate();
	const [isLoading, setIsLoading] = useState(true);
	const [shouldCheckAuth, setShouldCheckAuth] = useState(true);

	useEffect(() => {
		console.log('ProfilePage - Estado actual del usuario:', user);
		console.log('ProfilePage - Token en localStorage:', localStorage.getItem('token'));
		
		// Si no hay usuario pero hay token, esperar más tiempo para que se cargue
		if (!user && localStorage.getItem('token') && shouldCheckAuth) {
			console.log('ProfilePage - Esperando carga del usuario desde token...');
			const timer = setTimeout(() => {
				console.log('ProfilePage - Finalizando carga, usuario:', user);
				setIsLoading(false);
				setShouldCheckAuth(false);
			}, 1500); // Dar más tiempo si hay token pero no usuario
			return () => clearTimeout(timer);
		}
		
		// Si ya hay usuario o no hay token, cargar normalmente
		const timer = setTimeout(() => {
			console.log('ProfilePage - Finalizando carga, usuario:', user);
			setIsLoading(false);
		}, 500);

		return () => clearTimeout(timer);
	}, [user, shouldCheckAuth]);

	useEffect(() => {
		// Solo redirigir si ya terminó de cargar, no hay usuario Y no hay token
		if (!isLoading && !user && !localStorage.getItem('token')) {
			console.log('ProfilePage - Redirigiendo a login (no hay usuario ni token)');
			navigate('/login');
		} else if (!isLoading && !user && localStorage.getItem('token')) {
			console.log('ProfilePage - Hay token pero no usuario, posible problema en AuthContext');
			// Recargar la página para forzar reinicialización del contexto
			window.location.reload();
		}
	}, [isLoading, user, navigate]);

	if (isLoading) {
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

	if (!user) {
		console.log('ProfilePage - Usuario no disponible después de cargar');
		return null;
	}

	const handleLogout = () => {
		logout();
		navigate('/login');
	};
	const handleCreateLeague = () => {
		navigate('/create-league');
	};
	const handleJoinLeague = () => {
		navigate('/join-league');
	};

	return (
		<div style={{
			minHeight: '100vh',
			backgroundColor: '#1a202c', // Dark theme background
			padding: '20px',
			display: 'flex',
			alignItems: 'center',
			justifyContent: 'center'
		}}>
			<div style={{
				width: '100%',
				maxWidth: '600px',
				margin: '0 auto',
				backgroundColor: '#2d3748', // Dark component background
				borderRadius: '12px',
				boxShadow: '0 4px 20px rgba(0, 0, 0, 0.2)',
				overflow: 'hidden'
			}}>
				{/* Header */}
				<div style={{
					backgroundColor: '#4a5568', // A mid-tone blue-gray
					color: '#e2e8f0',
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
							backgroundColor: '#1a202c',
							borderRadius: '8px',
							border: '1px solid #4a5568'
						}}>
							<label style={{
								display: 'block',
								fontWeight: '600',
								color: '#a0aec0',
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
								color: '#e2e8f0'
							}}>
								{user.id}
							</p>
						</div>

						<div style={{
							padding: '20px',
							backgroundColor: '#1a202c',
							borderRadius: '8px',
							border: '1px solid #4a5568'
						}}>
							<label style={{
								display: 'block',
								fontWeight: '600',
								color: '#a0aec0',
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
								color: '#e2e8f0'
							}}>
								{user.name}
							</p>
						</div>

						<div style={{
							padding: '20px',
							backgroundColor: '#1a202c',
							borderRadius: '8px',
							border: '1px solid #4a5568'
						}}>
							<label style={{
								display: 'block',
								fontWeight: '600',
								color: '#a0aec0',
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
								color: '#e2e8f0'
							}}>
								{user.email}
							</p>
						</div>

						<div style={{
							padding: '20px',
							backgroundColor: '#1a202c',
							borderRadius: '8px',
							border: '1px solid #4a5568'
						}}>
							<label style={{
								display: 'block',
								fontWeight: '600',
								color: '#a0aec0',
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
								color: '#e2e8f0'
							}}>
								{user.alias}
							</p>
						</div>

						<div style={{
							padding: '20px',
							backgroundColor: '#1a202c',
							borderRadius: '8px',
							border: '1px solid #4a5568'
						}}>
							<label style={{
								display: 'block',
								fontWeight: '600',
								color: '#a0aec0',
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
								color: '#e2e8f0'
							}}>
								{user.role}
							</p>
						</div>
					</div>

					<button
						onClick={handleCreateLeague}
						style={{
							width: '100%',
							padding: '14px',
							backgroundColor: '#63b3ed',
							color: 'white',
							border: 'none',
							borderRadius: '6px',
							fontSize: '16px',
							fontWeight: '600',
							cursor: 'pointer',
							transition: 'background-color 0.3s',
							marginBottom: '10px'
						}}
					>
						Crear Liga
					</button>

					<button
						onClick={handleJoinLeague}
						style={{
							width: '100%',
							padding: '14px',
							backgroundColor: '#68d391',
							color: 'white',
							border: 'none',
							borderRadius: '6px',
							fontSize: '16px',
							fontWeight: '600',
							cursor: 'pointer',
							transition: 'background-color 0.3s',
							marginBottom: '10px'
						}}
					>
						Unirse a Liga
					</button>

					<button
						onClick={handleLogout}
						style={{
							width: '100%',
							padding: '14px',
							backgroundColor: '#e53e3e', // A more vibrant red
							color: 'white',
							border: 'none',
							borderRadius: '6px',
							fontSize: '16px',
							fontWeight: '600',
							cursor: 'pointer',
							transition: 'background-color 0.3s'
						}}
					>
						Cerrar Sesión
					</button>
				</div>
			</div>
		</div>
	);
};

export default ProfilePage;