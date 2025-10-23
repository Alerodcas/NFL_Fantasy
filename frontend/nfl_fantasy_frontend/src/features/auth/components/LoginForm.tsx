import React, { useState } from 'react';
import { useAuth } from '../../../shared/hooks/useAuth';
import { useNavigate, Link } from 'react-router-dom';
import api from '../../../services/apiService';

const LoginForm = () => {
	const [email, setEmail] = useState('');
	const [password, setPassword] = useState('');
	const [error, setError] = useState('');
	const [loading, setLoading] = useState(false);
	const auth = useAuth();
	const navigate = useNavigate();

	const handleSubmit = async (e: React.FormEvent) => {
		e.preventDefault();
		setLoading(true);
		setError('');
    
		try {
			// Cambiar a /login con JSON en lugar de /token con form-data
			const response = await api.post('/login', {
				email: email,
				password: password
			});
			
			auth.login(response.data.access_token);
			navigate('/profile');
		} catch (err: any) {
			// Mostrar el mensaje específico del backend
			const errorMessage = err.response?.data?.detail || 'Error al iniciar sesión.';
			setError(errorMessage);
		} finally {
			setLoading(false);
		}
	};

	return (
		<div style={{
			minHeight: '100vh',
			display: 'flex',
			alignItems: 'center',
			justifyContent: 'center',
			backgroundColor: '#1a202c', // Dark theme background
			padding: '20px'
		}}>
			<div style={{
				backgroundColor: '#2d3748', // Dark component background
				padding: '40px',
				borderRadius: '12px',
				boxShadow: '0 4px 20px rgba(0, 0, 0, 0.2)',
				width: '100%',
				maxWidth: '400px'
			}}>
				<form onSubmit={handleSubmit}>
					<h2 style={{
						textAlign: 'center',
						marginBottom: '30px',
						color: '#e2e8f0', // Light text
						fontSize: '28px',
						fontWeight: '600'
					}}>
						Iniciar Sesión
					</h2>
          
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

					<div style={{ marginBottom: '20px' }}>
						<label style={{
							display: 'block',
							marginBottom: '8px',
							fontWeight: '500',
							color: '#a0aec0' // Lighter gray text
						}}>
							Email:
						</label>
						<input
							type="email"
							value={email}
							onChange={(e) => setEmail(e.target.value)}
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

					<div style={{ marginBottom: '30px' }}>
						<label style={{
							display: 'block',
							marginBottom: '8px',
							fontWeight: '500',
							color: '#a0aec0' // Lighter gray text
						}}>
							Contraseña:
						</label>
						<input
							type="password"
							value={password}
							onChange={(e) => setPassword(e.target.value)}
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

					<button
						type="submit"
						disabled={loading}
						style={{
							width: '100%',
							padding: '14px',
							backgroundColor: loading ? '#4a5568' : '#63b3ed',
							color: loading ? '#a0aec0' : '#1a202c',
							border: 'none',
							borderRadius: '6px',
							fontSize: '16px',
							fontWeight: '600',
							cursor: loading ? 'not-allowed' : 'pointer',
							transition: 'background-color 0.3s',
							marginBottom: '20px'
						}}
					>
						{loading ? 'Iniciando sesión...' : 'Entrar'}
					</button>

					<p style={{
						textAlign: 'center',
						color: '#a0aec0',
						margin: '0'
					}}>
						¿No tienes cuenta?{' '}
						<Link
							to="/register"
							style={{
								color: '#63b3ed',
								textDecoration: 'none',
								fontWeight: '500'
							}}
						>
							Regístrate aquí
						</Link>
					</p>
				</form>
			</div>
		</div>
	);
};

export default LoginForm;