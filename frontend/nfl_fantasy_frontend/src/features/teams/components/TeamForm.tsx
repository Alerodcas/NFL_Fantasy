// src/features/teams/CreateTeam.tsx
import { useState, useRef } from "react";
import { useNavigate, Link } from "react-router-dom";
import { createTeamJson, createTeamUpload } from "../../../services/teams";

type Mode = "url" | "upload";

export default function CreateTeam() {
  const nav = useNavigate();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [mode, setMode] = useState<Mode>("url");
  const [name, setName] = useState("");
  const [city, setCity] = useState("");
  const [imageUrl, setImageUrl] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const handleFileButtonClick = () => {
    fileInputRef.current?.click();
  };

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);

    if (name.trim().length < 2 || city.trim().length < 2) {
      setError("Name and city must be at least 2 characters.");
      return;
    }
    if (mode === "upload" && !file) {
      setError("Please select an image file.");
      return;
    }

    try {
      setSubmitting(true);
      const team =
        mode === "url"
          ? await createTeamJson({
              name: name.trim(),
              city: city.trim(),
              image_url: imageUrl.trim() || undefined,
            })
          : await createTeamUpload({
              name: name.trim(),
              city: city.trim(),
              file: file as File,
            });

      // show success and redirect to profile after a short delay
      setSuccess('Equipo creado exitosamente. Redirigiendo al perfil...');
      setTimeout(() => {
        nav('/profile');
      }, 1300);
    } catch (e: any) {
      if (e?.response?.status === 409) setError("A team with that name already exists.");
      else if (e?.response?.status === 422) setError("Please check required fields.");
      else setError(e?.message || "Failed to create team.");
    } finally {
      setSubmitting(false);
    }
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
        maxWidth: '600px'
      }}>
        <form onSubmit={onSubmit}>
          <h2 style={{
            textAlign: 'center',
            marginBottom: '30px',
            color: '#e2e8f0',
            fontSize: '28px',
            fontWeight: '600'
          }}>
            Create Team
          </h2>

		<div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '20px'
        }}>
          <Link
            to="/profile"
            style={{
              padding: '8px 16px',
              backgroundColor: '#2d3748',
              color: '#e2e8f0',
              border: '2px solid #4a5568',
              borderRadius: '6px',
              textDecoration: 'none',
              fontSize: '16px',
              transition: 'all 0.3s',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}
            onMouseOver={(e) => e.currentTarget.style.borderColor = '#63b3ed'}
            onMouseOut={(e) => e.currentTarget.style.borderColor = '#4a5568'}
          >
            ← Back to Profile
          </Link>
        </div>

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
              Mode:
            </label>
            <div style={{
              display: 'flex',
              gap: '20px',
              color: '#e2e8f0'
            }}>
              <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
                <input
                  type="radio"
                  checked={mode === "url"}
                  onChange={() => setMode("url")}
                  style={{ accentColor: '#63b3ed' }}
                />
                URL
              </label>
              <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
                <input
                  type="radio"
                  checked={mode === "upload"}
                  onChange={() => setMode("upload")}
                  style={{ accentColor: '#63b3ed' }}
                />
                Upload
              </label>
            </div>
          </div>

          <div style={{ marginBottom: '20px' }}>
            <label style={{
              display: 'block',
              marginBottom: '8px',
              fontWeight: '500',
              color: '#a0aec0'
            }}>
              Name:
            </label>
            <input
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              minLength={2}
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

          <div style={{ marginBottom: '20px' }}>
            <label style={{
              display: 'block',
              marginBottom: '8px',
              fontWeight: '500',
              color: '#a0aec0'
            }}>
              City:
            </label>
            <input
              value={city}
              onChange={(e) => setCity(e.target.value)}
              required
              minLength={2}
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

          {mode === "url" ? (
            <div style={{ marginBottom: '20px' }}>
              <label style={{
                display: 'block',
                marginBottom: '8px',
                fontWeight: '500',
                color: '#a0aec0'
              }}>
                Image URL (optional):
              </label>
              <input
                value={imageUrl}
                onChange={(e) => setImageUrl(e.target.value)}
                placeholder="https://..."
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
              <div style={{
                marginTop: '12px',
                height: '160px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                border: '2px dashed #4a5568',
                borderRadius: '6px',
                backgroundColor: '#1a202c'
              }}>
                {imageUrl ? (
                  <img src={imageUrl} style={{ maxHeight: '150px', borderRadius: '4px' }} alt="Preview" />
                ) : (
                  <span style={{ color: '#a0aec0' }}>Preview</span>
                )}
              </div>
            </div>
          ) : (
            <div style={{ marginBottom: '20px' }}>
              <label style={{
                display: 'block',
                marginBottom: '8px',
                fontWeight: '500',
                color: '#a0aec0'
              }}>
                Image file:
              </label>
              <div>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".png,.jpg,.jpeg,.webp"
                  onChange={(e) => setFile(e.target.files?.[0] || null)}
                  style={{
                    display: 'none'
                  }}
                />
                <button
                  type="button"
                  onClick={handleFileButtonClick}
                  style={{
                    width: '100%',
                    padding: '12px',
                    backgroundColor: '#2d3748',
                    color: '#e2e8f0',
                    border: '2px solid #4a5568',
                    borderRadius: '6px',
                    fontSize: '16px',
                    cursor: 'pointer',
                    transition: 'all 0.3s',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '8px'
                  }}
                  onMouseOver={(e) => e.currentTarget.style.borderColor = '#63b3ed'}
                  onMouseOut={(e) => e.currentTarget.style.borderColor = '#4a5568'}
                >
                  {file ? file.name : 'Choose File'}
                </button>
              </div>
              <div style={{
                marginTop: '12px',
                height: '160px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                border: '2px dashed #4a5568',
                borderRadius: '6px',
                backgroundColor: '#1a202c'
              }}>
                {file ? (
                  <img src={URL.createObjectURL(file)} style={{ maxHeight: '150px', borderRadius: '4px' }} alt="Preview" />
                ) : (
                  <span style={{ color: '#a0aec0' }}>Preview</span>
                )}
              </div>
            </div>
          )}

          <button
            type="submit"
            disabled={submitting}
            style={{
              width: '100%',
              padding: '14px',
              backgroundColor: submitting ? '#4a5568' : '#63b3ed',
              color: submitting ? '#a0aec0' : '#1a202c',
              border: 'none',
              borderRadius: '6px',
              fontSize: '16px',
              fontWeight: '600',
              cursor: submitting ? 'not-allowed' : 'pointer',
              transition: 'background-color 0.3s'
            }}
          >
            {submitting ? "Creating…" : "Create Team"}
          </button>

        </form>
      </div>
    </div>
  );
}
