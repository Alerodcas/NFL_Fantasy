import React, { useState } from 'react';
import { createPlayerNews } from '../../../services/players';

type Props = {
  playerId: number;
  onCreated?: (newsId: number) => void;
};

const INJURY_OPTIONS = [
  { value: 'O', label: 'Fuera (O)' },
  { value: 'D', label: 'Dudoso (D)' },
  { value: 'Q', label: 'Cuestionable (Q)' },
  { value: 'P', label: 'Probable (P)' },
  { value: 'FP', label: 'Participación Plena (FP)' },
  { value: 'IR', label: 'Reserva de Lesionados (IR)' },
  { value: 'PUP', label: 'PUP' },
  { value: 'SUS', label: 'Suspendido (SUS)' },
];

export default function PlayerNewsForm({ playerId, onCreated }: Props) {
  const [summary, setSummary] = useState('');
  const [text, setText] = useState('');
  const [isInjury, setIsInjury] = useState(false);
  const [updateState, setUpdateState] = useState(false);
  const [injuryType, setInjuryType] = useState<string | undefined>(undefined);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const validate = (): string | null => {
    if (!summary || summary.trim().length === 0) return 'Resumen requerido';
    if (summary.length > 30) return 'Resumen máximo 30 caracteres';
    if (!text || text.trim().length < 10) return 'Texto mínimo 10 caracteres';
    if (text.length > 300) return 'Texto máximo 300 caracteres';
    if (isInjury && !injuryType) return 'Seleccione el tipo de lesión';
    return null;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    const v = validate();
    if (v) {
      setError(v);
      return;
    }

    setLoading(true);
    try {
      const payload = {
        player_id: playerId,
        summary: summary.trim(),
        text: text.trim(),
        is_injury: isInjury,
        injury_type: isInjury ? injuryType : undefined,
        update_state: updateState,
      };
      const created = await createPlayerNews(playerId, payload);
      setSummary('');
      setText('');
      setIsInjury(false);
        setUpdateState(false);
      setInjuryType(undefined);
      if (onCreated) onCreated(created.id);
    } catch (err: any) {
      const msg = err?.serverDetail || err?.message || 'Error al crear noticia';
      setError(String(msg));
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} style={{ background: '#2d3748', padding: 16, borderRadius: 8, border: '1px solid #4a5568' }}>
      <h3 style={{ color: '#e2e8f0', marginTop: 0 }}>Agregar noticia</h3>
      <div style={{ marginBottom: 10 }}>
        <label style={{ color: '#a0aec0', display: 'block', marginBottom: 6 }}>Resumen</label>
        <input value={summary} onChange={(e) => setSummary(e.target.value)} maxLength={30} style={{ width: '95%', padding: 8, borderRadius: 6 }} />
      </div>
      <div style={{ marginBottom: 10 }}>
        <label style={{ color: '#a0aec0', display: 'block', marginBottom: 6 }}>Texto</label>
        <textarea value={text} onChange={(e) => setText(e.target.value)} rows={4} maxLength={300} style={{ width: '95%', padding: 8, borderRadius: 6 }} />
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 8, alignItems: 'flex-start', marginBottom: 10 }}>
        <label style={{ color: '#a0aec0' }}>
          <input type="checkbox" checked={isInjury} onChange={(e) => setIsInjury(e.target.checked)} /> <span style={{ marginLeft: 6 }}>Es lesión</span>
        </label>
        <label style={{ color: '#a0aec0' }}>
          <input type="checkbox" checked={updateState} onChange={(e) => setUpdateState(e.target.checked)} /> <span style={{ marginLeft: 6 }}>Actualizar estado del jugador</span>
        </label>
        {isInjury && (
          <select value={injuryType} onChange={(e) => setInjuryType(e.target.value)} style={{ padding: 8, borderRadius: 6 }}>
            <option value="">-- Seleccione tipo de lesión --</option>
            {INJURY_OPTIONS.map((op) => (
              <option key={op.value} value={op.value}>{op.label}</option>
            ))}
          </select>
        )}
      </div>
      {error && <div style={{ color: '#f56565', marginBottom: 8 }}>{error}</div>}
      <div style={{ display: 'flex', gap: 8 }}>
        <button type="submit" disabled={loading} style={{ padding: '10px 14px', background: '#63b3ed', color: '#fff', border: 'none', borderRadius: 6, fontWeight: 700 }}>
          {loading ? 'Guardando...' : 'Guardar noticia'}
        </button>
      </div>
    </form>
  );
}
