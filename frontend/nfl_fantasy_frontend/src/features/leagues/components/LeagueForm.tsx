import { useEffect, useMemo, useRef, useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { createLeague, LeagueCreatePayload, LeagueCreatedResponse, uploadFantasyTeamImage } from "../../../services/leagues";
import { isValidPassword, passwordErrorMessage } from "../../../utils/password";

const TEAM_SIZES = [4,6,8,10,12,14,16,18,20] as const;

import { useAuth } from "../../../shared/hooks/useAuth";

function getCurrentUserId(user: any): number | null {
  return user?.id || null;
}

export default function LeagueForm() {
  const nav = useNavigate();

  // League
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [maxTeams, setMaxTeams] = useState<number>(10);
  const [password, setPassword] = useState("");
  const [playoffFormat, setPlayoffFormat] = useState<number>(4);
  const [allowDecimal, setAllowDecimal] = useState(true);

  // Fantasy team (commissioner) fields
  const [fantasyTeamName, setFantasyTeamName] = useState("");
  const [fantasyTeamCity, setFantasyTeamCity] = useState("");
  const [fantasyTeamImageUrl, setFantasyTeamImageUrl] = useState("");
  const [fantasyTeamThumbUrl, setFantasyTeamThumbUrl] = useState("");
  const [uploadingImage, setUploadingImage] = useState(false);
  const [uploadedFileName, setUploadedFileName] = useState("");
  const fileInputRef = useRef<HTMLInputElement>(null);

  // UI state
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [result, setResult] = useState<LeagueCreatedResponse | null>(null);

  const auth = useAuth();
  const currentUserId = useMemo(() => getCurrentUserId(auth.user), [auth.user]);

  useEffect(() => {
    // No need to pre-load real teams; fantasy team is created with the league
  }, [currentUserId]);

  const validate = (): string | null => {
    const nm = name.trim();
    if (nm.length < 1 || nm.length > 100) return "El nombre de la liga debe tener entre 1 y 100 caracteres.";
    if (!TEAM_SIZES.includes(maxTeams as any)) return "Cantidad de equipos no válida.";
  const pwdErr = passwordErrorMessage(password);
  if (pwdErr) return pwdErr;
    if (![4,6].includes(playoffFormat)) return "El formato de playoffs debe ser 4 o 6.";
  if (fantasyTeamName.trim().length < 2) return "El nombre del equipo de fantasía debe tener al menos 2 caracteres.";
  if (fantasyTeamCity.trim().length < 2) return "La ciudad del equipo de fantasía debe tener al menos 2 caracteres.";
    return null;
  };

  const onFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setError(null);
    setUploadingImage(true);
    try {
      const { image_url, thumbnail_url } = await uploadFantasyTeamImage(file);
      setFantasyTeamImageUrl(image_url);
      setFantasyTeamThumbUrl(thumbnail_url);
      setUploadedFileName(file.name);
    } catch (err: any) {
      setError(err?.response?.data?.detail || "No se pudo subir la imagen.");
    } finally {
      setUploadingImage(false);
    }
  };

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setSuccess(null);
    setResult(null);

    const v = validate();
    if (v) { setError(v); return; }

    const payload: LeagueCreatePayload = {
      name: name.trim(),
      description: description.trim() || undefined,
      max_teams: maxTeams as any,
      password,
      playoff_format: playoffFormat as any,
      allow_decimal_scoring: allowDecimal,
      fantasy_team: {
        name: fantasyTeamName.trim(),
        city: fantasyTeamCity.trim(),
        image_url: fantasyTeamImageUrl.trim() || undefined,
      },
    };
    console.log('[DEBUG] Payload enviado al backend:', payload);

    try {
      setSubmitting(true);
      const data = await createLeague(payload);
      setResult(data);
      setSuccess("Liga creada exitosamente. Redirigiendo al perfil…");
      setTimeout(() => nav("/profile"), 1300);
    } catch (e: any) {
  const status = e?.response?.status;
  const raw = e?.response?.data;
  const msg = (typeof raw === "string" ? raw : raw?.detail || "").toLowerCase();

  if (status === 404) {
    setError("No se encontró el equipo seleccionado.");
  } else if (status === 403) {
    setError("Solo puedes asignar un equipo propio.");
  } else if (status === 409) {
    if (msg.includes("assigned")) {
      setError("Ese equipo ya está asignado a una liga.");
    } else if (msg.includes("already exists")) {
      setError("Ya existe una liga con ese nombre.");
    } else {
      setError("Conflicto de datos. Verifica la información.");
    }
  } else if (status === 422) {
    setError("Revisa los campos requeridos. Formato inválido.");
  } else {
    setError(e?.message || "No se pudo crear la liga.");
  }
}
 finally {
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
            Crear Liga
          </h2>

          {/* Barra superior: volver */}
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

          {/* --- Datos de la liga --- */}
          <div style={{ marginBottom: "20px" }}>
            <label style={{ display: "block", marginBottom: "8px", fontWeight: 500, color: "#a0aec0" }}>
              Nombre de la liga:
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
                outline: "none",
                backgroundColor: "#1a202c",
                color: "#e2e8f0",
                transition: "border-color 0.3s"
              }}
              onFocus={(e) => (e.target.style.borderColor = "#63b3ed")}
              onBlur={(e) => (e.target.style.borderColor = "#4a5568")}
            />
          </div>

          <div style={{ marginBottom: "20px" }}>
            <label style={{ display: "block", marginBottom: "8px", fontWeight: 500, color: "#a0aec0" }}>
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
                outline: "none",
                backgroundColor: "#1a202c",
                color: "#e2e8f0",
                transition: "border-color 0.3s",
                resize: "vertical"
              }}
              onFocus={(e) => (e.target.style.borderColor = "#63b3ed")}
              onBlur={(e) => (e.target.style.borderColor = "#4a5568")}
            />
          </div>

          <div style={{ marginBottom: "20px" }}>
            <label style={{ display: "block", marginBottom: "8px", fontWeight: 500, color: "#a0aec0" }}>
              Cantidad de equipos:
            </label>
            <select
              value={maxTeams}
              onChange={(e) => setMaxTeams(parseInt(e.target.value, 10))}
              style={{
                width: "100%",
                padding: "12px",
                border: "2px solid #4a5568",
                borderRadius: "6px",
                fontSize: "16px",
                outline: "none",
                backgroundColor: "#1a202c",
                color: "#e2e8f0",
                transition: "border-color 0.3s",
                appearance: "none"
              }}
              onFocus={(e) => (e.target.style.borderColor = "#63b3ed")}
              onBlur={(e) => (e.target.style.borderColor = "#4a5568")}
            >
              {TEAM_SIZES.map(n => <option key={n} value={n}>{n}</option>)}
            </select>
          </div>

          <div style={{ marginBottom: "20px" }}>
            <label style={{ display: "block", marginBottom: "8px", fontWeight: 500, color: "#a0aec0" }}>
              Contraseña de la liga:
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="8–12 (Aa0…)"
              style={{
                width: "100%",
                padding: "12px",
                border: "2px solid #4a5568",
                borderRadius: "6px",
                fontSize: "16px",
                outline: "none",
                backgroundColor: "#1a202c",
                color: "#e2e8f0",
                transition: "border-color 0.3s"
              }}
              onFocus={(e) => (e.target.style.borderColor = "#63b3ed")}
              onBlur={(e) => (e.target.style.borderColor = "#4a5568")}
            />
            <small style={{ color: "#a0aec0" }}>
              8–12 caracteres alfanuméricos, con al menos una minúscula y una mayúscula.
            </small>
          </div>

          <div style={{ marginBottom: "20px" }}>
            <label style={{ display: "block", marginBottom: "8px", fontWeight: 500, color: "#a0aec0" }}>
              Formato de playoffs:
            </label>
            <select
              value={playoffFormat}
              onChange={(e) => setPlayoffFormat(parseInt(e.target.value, 10))}
              style={{
                width: "100%",
                padding: "12px",
                border: "2px solid #4a5568",
                borderRadius: "6px",
                fontSize: "16px",
                outline: "none",
                backgroundColor: "#1a202c",
                color: "#e2e8f0",
                transition: "border-color 0.3s",
                appearance: "none"
              }}
              onFocus={(e) => (e.target.style.borderColor = "#63b3ed")}
              onBlur={(e) => (e.target.style.borderColor = "#4a5568")}
            >
              <option value={4}>4 equipos (semanas 16–17)</option>
              <option value={6}>6 equipos (semanas 16–18)</option>
            </select>
          </div>

          <div style={{ marginBottom: "24px" }}>
            <label style={{ display: "flex", gap: "10px", alignItems: "center", color: "#e2e8f0" }}>
              <input
                type="checkbox"
                checked={allowDecimal}
                onChange={(e) => setAllowDecimal(e.target.checked)}
                style={{ accentColor: "#63b3ed" }}
              />
              Permitir puntajes con decimales
            </label>
          </div>

          <hr style={{ borderColor: "#4a5568", margin: "24px 0" }} />

          {/* --- Equipo de Fantasía del comisionado (se crea con la liga) --- */}
          <h3 style={{ color: "#e2e8f0", marginBottom: "12px", fontWeight: 600 }}>Equipo de Fantasía (Comisionado)</h3>
          <div style={{ marginBottom: "16px" }}>
            <label style={{ display: "block", marginBottom: "8px", fontWeight: 500, color: "#a0aec0" }}>
              Nombre del equipo:
            </label>
            <input
              value={fantasyTeamName}
              onChange={(e) => setFantasyTeamName(e.target.value)}
              required
              style={{
                width: "100%",
                padding: "12px",
                border: "2px solid #4a5568",
                borderRadius: "6px",
                fontSize: "16px",
                outline: "none",
                backgroundColor: "#1a202c",
                color: "#e2e8f0",
                transition: "border-color 0.3s"
              }}
              onFocus={(e) => (e.target.style.borderColor = "#63b3ed")}
              onBlur={(e) => (e.target.style.borderColor = "#4a5568")}
            />
          </div>

          <div style={{ marginBottom: "16px" }}>
            <label style={{ display: "block", marginBottom: "8px", fontWeight: 500, color: "#a0aec0" }}>
              Ciudad:
            </label>
            <input
              value={fantasyTeamCity}
              onChange={(e) => setFantasyTeamCity(e.target.value)}
              required
              style={{
                width: "100%",
                padding: "12px",
                border: "2px solid #4a5568",
                borderRadius: "6px",
                fontSize: "16px",
                outline: "none",
                backgroundColor: "#1a202c",
                color: "#e2e8f0",
                transition: "border-color 0.3s"
              }}
              onFocus={(e) => (e.target.style.borderColor = "#63b3ed")}
              onBlur={(e) => (e.target.style.borderColor = "#4a5568")}
            />
          </div>

          <div style={{ marginBottom: "22px" }}>
            <label style={{ display: "block", marginBottom: "8px", fontWeight: 500, color: "#a0aec0" }}>
              Imagen (URL opcional):
            </label>
            <input
              value={fantasyTeamImageUrl}
              onChange={(e) => setFantasyTeamImageUrl(e.target.value)}
              placeholder="https://…"
              style={{
                width: "100%",
                padding: "12px",
                border: "2px solid #4a5568",
                borderRadius: "6px",
                fontSize: "16px",
                outline: "none",
                backgroundColor: "#1a202c",
                color: "#e2e8f0",
                transition: "border-color 0.3s"
              }}
              onFocus={(e) => (e.target.style.borderColor = "#63b3ed")}
              onBlur={(e) => (e.target.style.borderColor = "#4a5568")}
            />
            <div style={{ marginTop: 12 }}>
              <label style={{ color: "#a0aec0", display: 'block', marginBottom: 6 }}>…o sube un archivo:</label>
              <input ref={fileInputRef} type="file" accept=".png,.jpg,.jpeg,.webp" onChange={onFileChange} style={{ display: 'none' }} />
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                disabled={uploadingImage}
                style={{
                  width: "100%",
                  padding: "12px",
                  backgroundColor: "#2d3748",
                  color: "#e2e8f0",
                  border: "2px solid #4a5568",
                  borderRadius: "6px",
                  fontSize: "16px",
                  cursor: uploadingImage ? 'not-allowed' : 'pointer',
                  transition: "all 0.3s",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  gap: "8px"
                }}
                onMouseOver={(e) => (e.currentTarget.style.borderColor = "#63b3ed")}
                onMouseOut={(e) => (e.currentTarget.style.borderColor = "#4a5568")}
              >
                {uploadedFileName ? uploadedFileName : (uploadingImage ? "Subiendo…" : "Elegir archivo")}
              </button>
            </div>

            <div style={{
              marginTop: 12,
              height: 160,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              border: '2px dashed #4a5568',
              borderRadius: 6,
              backgroundColor: '#1a202c'
            }}>
              {(fantasyTeamThumbUrl || fantasyTeamImageUrl) ? (
                <img src={fantasyTeamThumbUrl || fantasyTeamImageUrl} style={{ maxWidth: 100, maxHeight: 100, borderRadius: 4 }} alt="Thumbnail Preview" />
              ) : (
                <span style={{ color: '#a0aec0' }}>Preview del thumbnail</span>
              )}
            </div>
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
              <p>Cupos restantes: <strong>{result.slots_remaining}</strong></p>
              {"commissioner_team_id" in result && (
                <p>Tu equipo ID: <strong>{(result as any).commissioner_team_id}</strong></p>
              )}
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
              cursor: submitting ? "not-allowed" : "pointer",
              transition: "background-color 0.3s"
            }}
          >
            {submitting ? "Creando…" : "Crear Liga"}
          </button>
        </form>
      </div>
    </div>
  );
}
