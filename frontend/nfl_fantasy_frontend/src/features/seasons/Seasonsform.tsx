import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from '../../shared/hooks/useAuth';
import { createSeason, SeasonCreatePayload, SeasonCreatedResponse } from "../../services/seasons";

export default function SeasonForm() {
  const nav = useNavigate();
  const auth = useAuth();

  // --- State ---
  const [name, setName] = useState("");
  const [year, setYear] = useState<number>(new Date().getFullYear());
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [description, setDescription] = useState("");
  const [numWeeks, setNumWeeks] = useState<number>(17); // Default NFL season length
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [result, setResult] = useState<SeasonCreatedResponse | null>(null);

  // --- Validation ---
  const validate = (): string | null => {
    const nm = name.trim();
    if (nm.length < 1 || nm.length > 100)
      return "El nombre de la temporada debe tener entre 1 y 100 caracteres.";
    if (!year || year < 1900 || year > 2100)
      return "Año de la temporada inválido.";
    if (!startDate || !endDate)
      return "Debes especificar las fechas de inicio y fin.";
    if (new Date(startDate) >= new Date(endDate))
      return "La fecha de fin debe ser posterior a la fecha de inicio.";
    return null;
  };

  // --- Submit handler ---
  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setSuccess(null);
    setResult(null);

    const v = validate();
    if (v) {
      setError(v);
      return;
    }

    // Modify the payload object in the onSubmit function
    const payload: SeasonCreatePayload = {
      name: name.trim(),
      year,
      start_date: startDate,
      end_date: endDate,
      description: description.trim() || undefined,
      num_weeks: numWeeks, 
      is_current: true 
    };

    try {
      setSubmitting(true);
      const data = await createSeason(payload);
      setResult(data);
      setSuccess("Temporada creada exitosamente. Redirigiendo...");
      setTimeout(() => nav("/profile"), 1300);
    } catch (e: any) {
      const status = e?.response?.status;
      const raw = e?.response?.data;
      const msg = (typeof raw === "string" ? raw : raw?.detail || "").toLowerCase();

      if (status === 409 && msg.includes("already exists")) {
        setError("Ya existe una temporada con ese nombre o año.");
      } else if (status === 422) {
        setError("Revisa los campos requeridos. Formato inválido.");
      } else {
        setError(e?.message || "No se pudo crear la temporada.");
      }
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div style={{
      minHeight: "100vh",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      backgroundColor: "#1a202c",
      padding: "20px"
    }}>
      <div style={{
        backgroundColor: "#2d3748",
        padding: "40px",
        borderRadius: "12px",
        boxShadow: "0 4px 20px rgba(0, 0, 0, 0.2)",
        width: "100%",
        maxWidth: "640px"
      }}>
        <form onSubmit={onSubmit}>
          <h2 style={{
            textAlign: "center",
            marginBottom: "30px",
            color: "#e2e8f0",
            fontSize: "28px",
            fontWeight: 600
          }}>
            Crear Temporada
          </h2>

          {/* Volver */}
          <div style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            marginBottom: "20px"
          }}>
            <Link
              to="/profile"
              style={{
                padding: "8px 16px",
                backgroundColor: "#2d3748",
                color: "#e2e8f0",
                border: "2px solid #4a5568",
                borderRadius: "6px",
                textDecoration: "none",
                fontSize: "16px",
                transition: "all 0.3s",
                display: "flex",
                alignItems: "center",
                gap: "8px"
              }}
              onMouseOver={(e) => (e.currentTarget.style.borderColor = "#63b3ed")}
              onMouseOut={(e) => (e.currentTarget.style.borderColor = "#4a5568")}
            >
              ← Volver al Perfil
            </Link>
          </div>

          {error && (
            <div style={{
              backgroundColor: "rgba(255, 100, 100, 0.1)",
              color: "#ff8a8a",
              padding: "12px",
              borderRadius: "6px",
              marginBottom: "20px",
              border: "1px solid #c33"
            }}>
              {error}
            </div>
          )}

          {success && (
            <div style={{
              backgroundColor: "rgba(100, 255, 100, 0.08)",
              color: "#b2f5ea",
              padding: "12px",
              borderRadius: "6px",
              marginBottom: "20px",
              border: "1px solid #38b2ac"
            }}>
              {success}
            </div>
          )}

          {/* --- Campos del formulario --- */}
          <div style={{ marginBottom: "20px" }}>
            <label style={{ display: "block", marginBottom: "8px", color: "#a0aec0" }}>
              Nombre de la temporada:
            </label>
            <input
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              maxLength={100}
              style={{
                width: "100%",
                padding: "12px",
                border: "2px solid #4a5568",
                borderRadius: "6px",
                fontSize: "16px",
                backgroundColor: "#1a202c",
                color: "#e2e8f0"
              }}
            />
          </div>

          <div style={{ marginBottom: "20px" }}>
            <label style={{ display: "block", marginBottom: "8px", color: "#a0aec0" }}>
              Año:
            </label>
            <input
              type="number"
              value={year}
              onChange={(e) => setYear(parseInt(e.target.value, 10))}
              required
              min="1900"
              max="2100"
              style={{
                width: "100%",
                padding: "12px",
                border: "2px solid #4a5568",
                borderRadius: "6px",
                fontSize: "16px",
                backgroundColor: "#1a202c",
                color: "#e2e8f0"
              }}
            />
          </div>

          <div style={{ marginBottom: "20px" }}>
            <label style={{ display: "block", marginBottom: "8px", color: "#a0aec0" }}>
              Fecha de inicio:
            </label>
            <input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              required
              style={{
                width: "100%",
                padding: "12px",
                border: "2px solid #4a5568",
                borderRadius: "6px",
                backgroundColor: "#1a202c",
                color: "#e2e8f0"
              }}
            />
          </div>

          <div style={{ marginBottom: "20px" }}>
            <label style={{ display: "block", marginBottom: "8px", color: "#a0aec0" }}>
              Fecha de fin:
            </label>
            <input
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              required
              style={{
                width: "100%",
                padding: "12px",
                border: "2px solid #4a5568",
                borderRadius: "6px",
                backgroundColor: "#1a202c",
                color: "#e2e8f0"
              }}
            />
          </div>

          <div style={{ marginBottom: "24px" }}>
            <label style={{ display: "block", marginBottom: "8px", color: "#a0aec0" }}>
              Descripción (opcional):
            </label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              maxLength={1000}
              rows={3}
              style={{
                width: "100%",
                padding: "12px",
                border: "2px solid #4a5568",
                borderRadius: "6px",
                fontSize: "16px",
                backgroundColor: "#1a202c",
                color: "#e2e8f0"
              }}
            />
          </div>

          <div style={{ marginBottom: "20px" }}>
            <label style={{ display: "block", marginBottom: "8px", color: "#a0aec0" }}>
              Número de Semanas:
            </label>
            <input
              type="number"
              value={numWeeks}
              onChange={(e) => setNumWeeks(parseInt(e.target.value, 10))}
              required
              min="1"
              max="52"
              style={{
                width: "100%",
                padding: "12px",
                border: "2px solid #4a5568",
                borderRadius: "6px",
                fontSize: "16px",
                backgroundColor: "#1a202c",
                color: "#e2e8f0"
              }}
            />
          </div>

          {/* Resultado */}
          {result && (
            <div style={{
              backgroundColor: "rgba(100, 255, 100, 0.08)",
              color: "#b2f5ea",
              padding: "12px",
              borderRadius: "6px",
              marginBottom: "20px",
              border: "1px solid #38b2ac"
            }}>
              <p><strong>{result.name}</strong> creada (ID {result.id}).</p>
              <p>Año: <strong>{result.year}</strong></p>
            </div>
          )}

          <button
            type="submit"
            disabled={submitting}
            style={{
              width: "100%",
              padding: "14px",
              backgroundColor: submitting ? "#4a5568" : "#63b3ed",
              color: submitting ? "#a0aec0" : "#1a202c",
              border: "none",
              borderRadius: "6px",
              fontSize: "16px",
              fontWeight: 600,
              cursor: submitting ? "not-allowed" : "pointer"
            }}
          >
            {submitting ? "Creando…" : "Crear Temporada"}
          </button>
        </form>
      </div>
    </div>
  );
}
