import { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

interface PlayerPreview {
  id?: string;
  name: string;
  position: string;
  team: string;
  image: string;
}

export default function BatchPlayers() {
  const [file, setFile] = useState<File | null>(null);
  const [players, setPlayers] = useState<PlayerPreview[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setError(null);
    setSuccess(null);
    const uploadedFile = e.target.files?.[0] || null;
    setFile(uploadedFile);

    if (uploadedFile) {
      const reader = new FileReader();
      reader.onload = (event) => {
        try {
          const json = JSON.parse(event.target?.result as string);
          if (!Array.isArray(json)) throw new Error('El JSON debe contener un array de jugadores');
          setPlayers(json);
        } catch (err: any) {
          setError(`Error al leer el archivo: ${err.message}`);
          setPlayers([]);
        }
      };
      reader.readAsText(uploadedFile);
    } else {
      setPlayers([]);
    }

    e.target.value = ''; // permite recargar el mismo archivo otra vez
  };


  const handleUpload = async () => {
    if (!file) {
      setError('Por favor selecciona un archivo JSON primero.');
      return;
    }
    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      // Endpoint
      const token = localStorage.getItem('token');
      const response = await axios.post(
        'http://localhost:8000/players/batch-upload',
        formData,
        {
            headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'multipart/form-data'
            }
        }
      );


      setSuccess(response.data.message || 'Jugadores cargados exitosamente');
      setPlayers([]);
      setFile(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al subir el archivo');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#1a202c', color: '#e2e8f0', padding: 40 }}>
      <div style={{ maxWidth: 1000, margin: '0 auto' }}>
        <h1 style={{ fontSize: 28, fontWeight: 700, marginBottom: 8 }}>Creación batch de jugadores</h1>
        <p style={{ color: '#a0aec0', marginBottom: 24 }}>
          Cargá un archivo JSON con los datos de los jugadores NFL para su creación en lote.
        </p>

        {/* File input */}
        <div
          style={{
            backgroundColor: '#2d3748',
            border: '1px solid #4a5568',
            borderRadius: 12,
            padding: 24,
            marginBottom: 20,
          }}
        >
          <input
            type="file"
            accept=".json"
            onChange={handleFileChange}
            style={{
              backgroundColor: '#1a202c',
              border: '1px solid #4a5568',
              borderRadius: 6,
              padding: 10,
              color: '#e2e8f0',
              width: '100%',
            }}
          />

          {error && (
            <div style={{ marginTop: 16, backgroundColor: '#742a2a', padding: 12, borderRadius: 6, color: '#fff' }}>
              ⚠️ {error}
            </div>
          )}
          {success && (
            <div style={{ marginTop: 16, backgroundColor: '#22543d', padding: 12, borderRadius: 6, color: '#fff' }}>
              ✅ {success}
            </div>
          )}
        </div>

        {/* Preview */}
        {players.length > 0 && (
          <div
            style={{
              backgroundColor: '#2d3748',
              border: '1px solid #4a5568',
              borderRadius: 12,
              padding: 20,
              marginBottom: 20,
            }}
          >
            <h3 style={{ fontSize: 18, fontWeight: 600, marginBottom: 12 }}>Vista previa ({players.length} jugadores)</h3>
            <div style={{ maxHeight: 400, overflowY: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid #4a5568' }}>
                    <th style={{ textAlign: 'left', padding: 8 }}>Nombre</th>
                    <th style={{ textAlign: 'left', padding: 8 }}>Posición</th>
                    <th style={{ textAlign: 'left', padding: 8 }}>Equipo</th>
                    <th style={{ textAlign: 'left', padding: 8 }}>Imagen</th>
                  </tr>
                </thead>
                <tbody>
                  {players.map((p, i) => (
                    <tr key={i} style={{ borderBottom: '1px solid #4a5568' }}>
                      <td style={{ padding: 8 }}>{p.name}</td>
                      <td style={{ padding: 8 }}>{p.position}</td>
                      <td style={{ padding: 8 }}>{p.team}</td>
                      <td style={{ padding: 8 }}>
                        <img src={p.image} alt={p.name} width="40" height="40" style={{ borderRadius: '50%' }} />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Actions */}
        <div style={{ display: 'flex', gap: 12, marginTop: 20 }}>
          <button
            onClick={handleUpload}
            disabled={loading || !file}
            style={{
              backgroundColor: '#63b3ed',
              color: 'white',
              border: 'none',
              borderRadius: 6,
              padding: '12px 20px',
              fontWeight: 600,
              cursor: loading ? 'not-allowed' : 'pointer',
              opacity: loading ? 0.6 : 1,
            }}
          >
            {loading ? 'Procesando...' : 'Cargar jugadores'}
          </button>
          <button
            onClick={() => navigate('/admin')}
            style={{
              backgroundColor: 'transparent',
              border: '1px solid #4a5568',
              color: '#a0aec0',
              borderRadius: 6,
              padding: '12px 20px',
              fontWeight: 600,
              cursor: 'pointer',
            }}
          >
            Volver al panel
          </button>
        </div>
      </div>
    </div>
  );
}
