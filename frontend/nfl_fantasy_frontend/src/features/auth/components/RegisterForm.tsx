import React, { useState } from 'react';
import api from '../../../services/apiService';
import { useNavigate, Link } from 'react-router-dom';
import { passwordErrorMessage } from '../../../utils/password';

const RegisterForm = () => {
	const [name, setName] = useState('');
	const [email, setEmail] = useState('');
	const [alias, setAlias] = useState('');
	const [password, setPassword] = useState('');
	const [confirmPassword, setConfirmPassword] = useState('');
	const [error, setError] = useState('');
	const [loading, setLoading] = useState(false);
	const [success, setSuccess] = useState(false);
	const navigate = useNavigate();

	const handleSubmit = async (e: React.FormEvent) => {
		e.preventDefault();
		setLoading(true);
		setError('');
    
		console.log('Iniciando registro...', { name, email, alias, passwordLength: password.length });

		if (password !== confirmPassword) {
			setError('Las contraseñas no coinciden.');
			setLoading(false);
			return;
		}

			const pwdErr = passwordErrorMessage(password);
			if (pwdErr) {
				setError(pwdErr);
				setLoading(false);
				return;
			}

		try {
			console.log('Enviando petición de registro...');
			console.log('Datos a enviar:', { name, email, alias, password: '***' });
			console.log('Password length:', password.length);
			console.log('Password value exists:', !!password);
      
			const response = await api.post('/register/', { name, email, alias, password });
			console.log('Respuesta del servidor:', response.data);
			console.log('Status de la respuesta:', response.status);
      
			setSuccess(true);
			console.log('Estado de éxito establecido');
			setTimeout(() => {
				console.log('Navegando al login...');
				navigate('/login');
			}, 2000);
		} catch (err: any) {
			console.error('Error en el registro:', err);
			console.error('Respuesta de error:', err.response);
      
			let errorMessage = 'Error al registrar. Inténtalo de nuevo.';
      
			if (err.response?.status === 422) {
				// Error de validación
				const validationErrors = err.response?.data?.errors;
				if (validationErrors && validationErrors.length > 0) {
					const errorMessages = validationErrors.map((error: any) => {
						if (error.loc && error.loc.includes('password')) {
							if (error.msg.includes('least 8 characters')) {
								return 'La contraseña debe tener al menos 8 caracteres';
							}
							if (error.msg.includes('most 12 characters')) {
								return 'La contraseña debe tener máximo 12 caracteres';
							}
							if (error.msg.includes('lowercase letter')) {
								return 'La contraseña debe contener al menos una letra minúscula';
							}
							if (error.msg.includes('uppercase letter')) {
								return 'La contraseña debe contener al menos una letra mayúscula';
							}
							if (error.msg.includes('digit')) {
								return 'La contraseña debe contener al menos un número';
							}
							if (error.msg.includes('too long')) {
								return 'La contraseña es demasiado larga';
							}
						}
						return error.msg;
					});
					errorMessage = errorMessages.join(', ');
				}
			} else {
				errorMessage = err.response?.data?.detail || errorMessage;
			}
      
			setError(errorMessage);
		} finally {
			setLoading(false);
			console.log('Loading establecido a false');
		}
	};

	if (success) {
		return (
			<div style={{
				minHeight: '100vh',
				display: 'flex',
				alignItems: 'center',
				justifyContent: 'center',
				backgroundColor: '#1a202c',
				padding: '20px'
			}}>
				<div style={{
					backgroundColor: '#2d3748',
					padding: '40px',
					borderRadius: '12px',
					boxShadow: '0 4px 20px rgba(0, 0, 0, 0.2)',
					width: '100%',
					maxWidth: '400px',
					textAlign: 'center'
				}}>
					<div style={{
						backgroundColor: 'rgba(100, 255, 100, 0.1)',
						color: '#a8e6cf',
						padding: '20px',
						borderRadius: '6px',
						border: '1px solid #63b3ed'
					}}>
						<h2 style={{ margin: '0 0 10px 0', color: '#e2e8f0' }}>¡Registro exitoso!</h2>
						<p style={{ margin: '0', color: '#a0aec0' }}>Serás redirigido al login en unos segundos...</p>
					</div>
				</div>
			</div>
		);
	}

	return (
		<div style={{
			minHeight: '100vh',
			display: 'flex',
			alignItems: 'center',
			justifyContent: 'center',
			backgroundColor: '#1a202c',
			padding: '20px'
		}}>
			<div style={{
				backgroundColor: '#2d3748',
				padding: '40px',
				borderRadius: '12px',
				boxShadow: '0 4px 20px rgba(0, 0, 0, 0.2)',
				width: '100%',
				maxWidth: '450px'
			}}>
				<form onSubmit={handleSubmit}>
					<h2 style={{
						textAlign: 'center',
						marginBottom: '30px',
						color: '#e2e8f0',
						fontSize: '28px',
						fontWeight: '600'
					}}>
						Registro
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
							color: '#a0aec0'
						}}>
							Nombre completo:
						</label>
						<input
							type="text"
							value={name}
							onChange={(e) => setName(e.target.value)}
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
							onFocus={(e) => (e.target as HTMLInputElement).style.borderColor = '#63b3ed'}
							onBlur={(e) => (e.target as HTMLInputElement).style.borderColor = '#4a5568'}
						/>
					</div>

					<div style={{ marginBottom: '20px' }}>
						<label style={{
							display: 'block',
							marginBottom: '8px',
							fontWeight: '500',
							color: '#a0aec0'
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
							onFocus={(e) => (e.target as HTMLInputElement).style.borderColor = '#63b3ed'}
							onBlur={(e) => (e.target as HTMLInputElement).style.borderColor = '#4a5568'}
						/>
					</div>

					<div style={{ marginBottom: '20px' }}>
						<label style={{
							display: 'block',
							marginBottom: '8px',
							fontWeight: '500',
							color: '#a0aec0'
						}}>
							Alias:
						</label>
						<input
							type="text"
							value={alias}
							onChange={(e) => setAlias(e.target.value)}
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
							onFocus={(e) => (e.target as HTMLInputElement).style.borderColor = '#63b3ed'}
							onBlur={(e) => (e.target as HTMLInputElement).style.borderColor = '#4a5568'}
						/>
					</div>

					<div style={{ marginBottom: '20px' }}>
						<label style={{
							display: 'block',
							marginBottom: '8px',
							fontWeight: '500',
							color: '#a0aec0'
						}}>
							Contraseña:
						</label>
						<input
							type="password"
							value={password}
							onChange={(e) => {
								console.log('Password changed:', e.target.value.length, 'chars');
								setPassword(e.target.value);
							}}
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
							onFocus={(e) => (e.target as HTMLInputElement).style.borderColor = '#63b3ed'}
							onBlur={(e) => (e.target as HTMLInputElement).style.borderColor = '#4a5568'}
						/>
						<small style={{
							color: '#a0aec0',
							fontSize: '12px',
							marginTop: '4px',
							display: 'block'
						}}>
							8-12 caracteres, al menos una mayúscula, una minúscula y un número
						</small>
					</div>

					<div style={{ marginBottom: '30px' }}>
						<label style={{
							display: 'block',
							marginBottom: '8px',
							fontWeight: '500',
							color: '#a0aec0'
						}}>
							Confirmar contraseña:
						</label>
						<input
							type="password"
							value={confirmPassword}
							onChange={(e) => {
								console.log('Confirm password changed:', e.target.value.length, 'chars');
								setConfirmPassword(e.target.value);
							}}
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
							onFocus={(e) => (e.target as HTMLInputElement).style.borderColor = '#63b3ed'}
							onBlur={(e) => (e.target as HTMLInputElement).style.borderColor = '#4a5568'}
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
						{loading ? 'Registrando...' : 'Registrarse'}
					</button>

					<p style={{
						textAlign: 'center',
						color: '#a0aec0',
						margin: '0'
					}}>
						¿Ya tienes cuenta?{' '}
						<Link
							to="/login"
							style={{
								color: '#63b3ed',
								textDecoration: 'none',
								fontWeight: '500'
							}}
						>
							Inicia sesión aquí
						</Link>
					</p>
				</form>
			</div>
		</div>
	);
};

export default RegisterForm;
// ...existing code from original RegisterForm.tsx...