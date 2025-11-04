import { useEffect, useRef, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { createPlayerUpload } from "../../../services/players";
import { listTeams, Team } from "../../../services/teams";

const POSITIONS = [
  { value: "QB", label: "QuarterBack (QB)" },
  { value: "RB", label: "RunningBack (RB)" },
  { value: "WR", label: "Wide Receiver (WR)" },
  { value: "TE", label: "Tight End (TE)" },
  { value: "K", label: "Kicker (K)" },
  { value: "DST", label: "Defense/Special Teams (DST)" },
  { value: "FLEX", label: "Flexible (FLEX)" },
];

const generateThumbnail = (file: File): Promise<string> => {
  return new Promise((resolve) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      const img = new Image();
      img.onload = () => {
        const canvas = document.createElement("canvas");
        const ctx = canvas.getContext("2d");
        canvas.width = 100;
        canvas.height = 100;
        ctx?.drawImage(img, 0, 0, 100, 100);
        resolve(canvas.toDataURL());
      };
      img.src = e.target?.result as string;
    };
    reader.readAsDataURL(file);
  });
};

export default function PlayerForm() {
  const nav = useNavigate();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [name, setName] = useState("");
  const [position, setPosition] = useState("");
  const [teamId, setTeamId] = useState<number | "">("");
  const [file, setFile] = useState<File | null>(null);
  const [thumbnailPreview, setThumbnailPreview] = useState<string | null>(null);
  const [teams, setTeams] = useState<Team[]>([]);

  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [loadingTeams, setLoadingTeams] = useState(true);

  useEffect(() => {
    // Load teams to choose from
    setLoadingTeams(true);
    listTeams()
      .then((data) => {
        console.log("Teams loaded:", data);
        setTeams(data);
      })
      .catch((err) => {
        console.error("Failed to load teams:", err);
        setError("No se pudieron cargar los equipos. Verifica tu conexión.");
        setTeams([]);
      })
      .finally(() => {
        setLoadingTeams(false);
      });
  }, []);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0] || null;
    setFile(selectedFile);
    if (selectedFile) {
      generateThumbnail(selectedFile).then(setThumbnailPreview);
    } else {
      setThumbnailPreview(null);
    }
  };

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setSuccess(null);

    if (name.trim().length < 2) {
      setError("El nombre debe tener al menos 2 caracteres.");
      return;
    }
    if (!position.trim()) {
      setError("La posición es obligatoria.");
      return;
    }
    if (!teamId || Number(teamId) <= 0) {
      setError("Debes seleccionar un equipo.");
      return;
    }
    if (!file) {
      setError("Selecciona un archivo de imagen.");
      return;
    }

    try {
      setSubmitting(true);
      await createPlayerUpload({
        name: name.trim(),
        position: position.trim(),
        team_id: Number(teamId),
        file: file as File,
      });

      setSuccess("Jugador creado exitosamente. Redirigiendo…");
      setTimeout(() => nav("/admin"), 1200);
    } catch (e: any) {
      const status = e?.response?.status;
      if (status === 409) setError("Ya existe un jugador con ese nombre en ese equipo.");
      else if (status === 422) setError("Revisa los campos requeridos (todos son obligatorios).");
      else setError(e?.message || "No se pudo crear el jugador.");
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
            Crear Jugador
          </h2>

          <div style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            marginBottom: "20px"
          }}>
            <Link
              to="/admin"
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
              ← Volver al Panel de Administración
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

          <div style={{ marginBottom: "20px" }}>
            <label style={{ display: "block", marginBottom: "8px", fontWeight: 500, color: "#a0aec0" }}>
              Nombre:
            </label>
            <input
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              minLength={2}
              style={{
                width: "100%",
                padding: "12px",
                border: "2px solid #4a5568",
                borderRadius: "6px",
                fontSize: "16px",
                transition: "border-color 0.3s",
                outline: "none",
                backgroundColor: "#1a202c",
                color: "#e2e8f0"
              }}
              onFocus={(e) => (e.target.style.borderColor = "#63b3ed")}
              onBlur={(e) => (e.target.style.borderColor = "#4a5568")}
            />
          </div>

          <div style={{ marginBottom: "20px" }}>
            <label style={{ display: "block", marginBottom: "8px", fontWeight: 500, color: "#a0aec0" }}>
              Posición:
            </label>
            <select
              value={position}
              onChange={(e) => setPosition(e.target.value)}
              required
              style={{
                width: "100%",
                padding: "12px",
                border: "2px solid #4a5568",
                borderRadius: "6px",
                fontSize: "16px",
                backgroundColor: "#1a202c",
                color: "#e2e8f0",
                outline: "none"
              }}
              onFocus={(e) => (e.target.style.borderColor = "#63b3ed")}
              onBlur={(e) => (e.target.style.borderColor = "#4a5568")}
            >
              <option value="" disabled>
                Selecciona una posición
              </option>
              {POSITIONS.map((pos) => (
                <option key={pos.value} value={pos.value} style={{ backgroundColor: "#2d3748", color: "#e2e8f0" }}>
                  {pos.label}
                </option>
              ))}
            </select>
          </div>

          <div style={{ marginBottom: "20px" }}>
            <label style={{ display: "block", marginBottom: "8px", fontWeight: 500, color: "#a0aec0" }}>
              Equipo:
            </label>
            {loadingTeams ? (
              <div style={{ 
                padding: "12px", 
                color: "#a0aec0",
                backgroundColor: "#1a202c",
                border: "2px solid #4a5568",
                borderRadius: "6px"
              }}>
                Cargando equipos...
              </div>
            ) : teams.length === 0 ? (
              <div style={{ 
                padding: "12px", 
                color: "#ff8a8a",
                backgroundColor: "rgba(255, 100, 100, 0.1)",
                border: "2px solid #c33",
                borderRadius: "6px"
              }}>
                No hay equipos disponibles. Por favor crea un equipo primero.
              </div>
            ) : (
              <select
                value={teamId}
                onChange={(e) => setTeamId(e.target.value ? Number(e.target.value) : "")}
                required
                style={{
                  width: "100%",
                  padding: "12px",
                  border: "2px solid #4a5568",
                  borderRadius: "6px",
                  fontSize: "16px",
                  backgroundColor: "#1a202c",
                  color: "#e2e8f0",
                  outline: "none"
                }}
                onFocus={(e) => (e.target.style.borderColor = "#63b3ed")}
                onBlur={(e) => (e.target.style.borderColor = "#4a5568")}
              >
                <option value="" disabled>
                  Selecciona un equipo
                </option>
                {teams.map((t) => (
                  <option key={t.id} value={t.id} style={{ backgroundColor: "#2d3748", color: "#e2e8f0" }}>
                    {t.name} {t.city ? `(${t.city})` : ""}
                  </option>
                ))}
              </select>
            )}
          </div>

          <div style={{ marginBottom: "20px" }}>
            <label style={{ display: "block", marginBottom: "8px", fontWeight: 500, color: "#a0aec0" }}>
              Archivo de imagen:
            </label>
            <div>
              <input
                ref={fileInputRef}
                type="file"
                accept=".png,.jpg,.jpeg,.webp"
                onChange={handleFileChange}
                style={{ display: "none" }}
              />
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                style={{
                  width: "100%",
                  padding: "12px",
                  backgroundColor: "#2d3748",
                  color: "#e2e8f0",
                  border: "2px solid #4a5568",
                  borderRadius: "6px",
                  fontSize: "16px",
                  cursor: "pointer",
                  transition: "all 0.3s",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  gap: "8px"
                }}
                onMouseOver={(e) => (e.currentTarget.style.borderColor = "#63b3ed")}
                onMouseOut={(e) => (e.currentTarget.style.borderColor = "#4a5568")}
              >
                {file ? file.name : "Elegir archivo"}
              </button>
            </div>
            <div style={{
              marginTop: "12px",
              height: "160px",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              border: "2px dashed #4a5568",
              borderRadius: "6px",
              backgroundColor: "#1a202c"
            }}>
              {thumbnailPreview ? (
                <img src={thumbnailPreview} style={{ maxWidth: "100px", maxHeight: "100px", borderRadius: "4px" }} alt="Thumbnail Preview" />
              ) : (
                <span style={{ color: "#a0aec0" }}>Preview del thumbnail</span>
              )}
            </div>
          </div>

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
            {submitting ? "Creando…" : "Crear Jugador"}
          </button>
        </form>
      </div>
    </div>
  );
}
