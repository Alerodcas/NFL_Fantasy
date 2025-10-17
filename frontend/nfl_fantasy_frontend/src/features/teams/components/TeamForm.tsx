import React, { useState } from 'react';
import { useAuth } from '../../../shared/hooks/useAuth';
import { useNavigate, Link } from 'react-router-dom';
import api from '../../../services/apiService';

const TeamForm = () => {
	const [name, setName] = useState('');
	const [leagueId, setLeagueId] = useState<number>(1); // cambia si quieres
	const [description, setDescription] = useState('');
	const [logoUrl, setLogoUrl] = useState('');
	const [error, setError] = useState('');
	const [loading, setLoading] = useState(false);

	const auth = useAuth();
	const navigate = useNavigate();

	const handleSubmit = async (e: React.FormEvent) => {
		e.preventDefault();
		setLoading(true);
		setError('');

		if (!name.trim() || name.trim().length < 3) {
			setError('El nombre debe tener al menos 3 caracteres.');
			setLoading(false);
			return;
		}
		if (!leagueId || leagueId <= 0) {
			setError('Debes indicar un league_id válido.');
			setLoading(false);
			return;
		}

		try {
			const payload = {
				name: name.trim(),
				description: description || undefined,
				logo_url: logoUrl || undefined,
				league_id: leagueId,
			};

			// rely on apiService request interceptor to add Authorization header
			const resp = await api.post('/teams', payload);

			// Éxito
			alert('Equipo creado con éxito');
			// Navega por ahora al perfil:
			navigate('/profile');

		} catch (err: any) {
			const msg =
				err?.response?.data?.detail ||
				err?.message ||
				'Error al crear el equipo.';
			setError(String(msg));
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
			backgroundColor: '#f5f5f5',
			padding: '20px'
		}}>
			<div style={{
				backgroundColor: 'white',
				padding: '40px',
				borderRadius: '12px',
				boxShadow: '0 4px 20px rgba(0, 0, 0, 0.1)',
				width: '100%',
				maxWidth: '500px'
			}}>
				<form onSubmit={handleSubmit}>
					<h2 style={{
						textAlign: 'center',
						marginBottom: '30px',
						color: '#333',
						fontSize: '28px',
						fontWeight: '600'
					}}>
						Crear Equipo
					</h2>

					{error && (
						<div style={{
							backgroundColor: '#fee',
							color: '#c33',
							padding: '12px',
							borderRadius: '6px',
							marginBottom: '20px',
							border: '1px solid #fcc'
						}}>
							{error}
						</div>
					)}

					<div style={{ marginBottom: '20px' }}>
						<label style={{
							display: 'block',
							marginBottom: '8px',
							fontWeight: '500',
							color: '#555'
						}}>
							Nombre*:
						</label>
						<input
							type="text"
							value={name}
							onChange={(e) => setName(e.target.value)}
							required
							minLength={3}
							style={{
								width: '100%',
								padding: '12px',
								border: '2px solid #ddd',
								borderRadius: '6px',
								fontSize: '16px',
								transition: 'border-color 0.3s',
								outline: 'none'
							}}
							onFocus={(e) => e.currentTarget.style.borderColor = '#007bff'}
							onBlur={(e) => e.currentTarget.style.borderColor = '#ddd'}
						/>
					</div>

					<div style={{ marginBottom: '20px' }}>
						<label style={{
							display: 'block',
							marginBottom: '8px',
							fontWeight: '500',
							color: '#555'
						}}>
							League ID*:
						</label>
						<label style={{
							display: 'block',
							marginBottom: '5px',
							fontWeight: '500',
							fontSize: '12px',
							color: '#555'
						}}>
							Liga a la que pertenece el equipo
						</label>
						<input
							type="number"
							value={leagueId}
							onChange={(e) => setLeagueId(Number(e.target.value))}
							min={1}
							required
							style={{
								width: '100%',
								padding: '12px',
								border: '2px solid #ddd',
								borderRadius: '6px',
								fontSize: '16px',
								transition: 'border-color 0.3s',
								outline: 'none'
							}}
							onFocus={(e) => e.currentTarget.style.borderColor = '#007bff'}
							onBlur={(e) => e.currentTarget.style.borderColor = '#ddd'}
						/>
					</div>

					<div style={{ marginBottom: '20px' }}>
						<label style={{
							display: 'block',
							marginBottom: '8px',
							fontWeight: '500',
							color: '#555'
						}}>
							Descripción:
						</label>
						<input
							type="text"
							value={description}
							onChange={(e) => setDescription(e.target.value)}
							style={{
								width: '100%',
								padding: '12px',
								border: '2px solid #ddd',
								borderRadius: '6px',
								fontSize: '16px',
								transition: 'border-color 0.3s',
								outline: 'none'
							}}
							onFocus={(e) => (e.currentTarget.style.borderColor = '#007bff')}
							onBlur={(e) => (e.currentTarget.style.borderColor = '#ddd')}
						/>
					</div>

					<div style={{ marginBottom: '30px' }}>
						<label style={{
							display: 'block',
							marginBottom: '8px',
							fontWeight: '500',
							color: '#555'
						}}>
							Logo URL:
						</label>
						<input
							type="url"
							value={logoUrl}
							onChange={(e) => setLogoUrl(e.target.value)}
							placeholder="https://ejemplo.com/logo.png"
							style={{
								width: '100%',
								padding: '12px',
								border: '2px solid #ddd',
								borderRadius: '6px',
								fontSize: '16px',
								transition: 'border-color 0.3s',
								outline: 'none'
							}}
							onFocus={(e) => e.currentTarget.style.borderColor = '#007bff'}
							onBlur={(e) => e.currentTarget.style.borderColor = '#ddd'}
						/>
					</div>

					<button
						type="submit"
						disabled={loading}
						style={{
							width: '100%',
							padding: '14px',
							backgroundColor: loading ? '#ccc' : '#007bff',
							color: 'white',
							border: 'none',
							borderRadius: '6px',
							fontSize: '16px',
							fontWeight: '600',
							cursor: loading ? 'not-allowed' : 'pointer',
							transition: 'background-color 0.3s',
							marginBottom: '20px'
						}}
						onMouseOver={(e) => {
							if (!loading) (e.target as HTMLButtonElement).style.backgroundColor = '#0056b3';
						}}
						onMouseOut={(e) => {
							if (!loading) (e.target as HTMLButtonElement).style.backgroundColor = '#007bff';
						}}
					>
						{loading ? 'Creando...' : 'Crear equipo'}
					</button>

					<p style={{
						textAlign: 'center',
						color: '#666',
						margin: 0
					}}>
						¿Volver al perfil?{' '}
						<Link
							to="/profile"
							style={{
								color: '#007bff',
								textDecoration: 'none',
								fontWeight: '500'
							}}
						>
							Ir al perfil
						</Link>
					</p>
				</form>
			</div>
		</div>
	);
};

export default TeamForm;
// ...existing code from original TeamForm.tsx...