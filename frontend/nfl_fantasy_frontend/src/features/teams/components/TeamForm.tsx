import { useState, useRef } from "react";
import { useNavigate, Link } from "react-router-dom";
import { createTeamUpload } from "../../../services/teams";

const generateThumbnail = (file: File): Promise<string> => {
  return new Promise((resolve) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      const img = new Image();
      img.onload = () => {
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
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

export default function CreateTeam() {
  const nav = useNavigate();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [name, setName] = useState("");
  const [city, setCity] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [thumbnailPreview, setThumbnailPreview] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

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

    if (name.trim().length < 2 || city.trim().length < 2) {
      setError("El nombre y la ciudad deben tener al menos 2 caracteres.");
      return;
    }
    if (!file) {
      setError("Selecciona un archivo de imagen.");
      return;
    }

    try {
      setSubmitting(true);
      const team = await createTeamUpload({
        name: name.trim(),
        city: city.trim(),
        file: file as File,
      });

      setSuccess("Equipo creado exitosamente. Redirigiendo al perfil…");
      setTimeout(() => nav("/profile"), 1300);
    } catch (e: any) {
      const status = e?.response?.status;
      if (status === 409) setError("Ya existe un equipo con ese nombre.");
      else if (status === 422) setError("Revisa los campos requeridos.");
      else setError(e?.message || "No se pudo crear el equipo.");
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
        maxWidth: "600px"
      }}>
        <form onSubmit={onSubmit}>
          <h2 style={{
            textAlign: "center",
            marginBottom: "30px",
            color: "#e2e8f0",
            fontSize: "28px",
            fontWeight: 600
          }}>
            Crear Equipo
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
            <label style={{
              display: "block",
              marginBottom: "8px",
              fontWeight: 500,
              color: "#a0aec0"
            }}>
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
            <label style={{
              display: "block",
              marginBottom: "8px",
              fontWeight: 500,
              color: "#a0aec0"
            }}>
              Ciudad:
            </label>
            <input
              value={city}
              onChange={(e) => setCity(e.target.value)}
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
            <label style={{
              display: "block",
              marginBottom: "8px",
              fontWeight: 500,
              color: "#a0aec0"
            }}>
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
            {submitting ? "Creando…" : "Crear Equipo"}
          </button>
        </form>
      </div>
    </div>
  );
}
