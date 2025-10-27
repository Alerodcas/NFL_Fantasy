-- Migración: Crear tabla league_members para relación usuarios-ligas
-- Fecha: 2025-10-24
-- Descripción: Tabla para registrar la membresía de usuarios en ligas con alias único

CREATE TABLE IF NOT EXISTS league_members (
    id SERIAL PRIMARY KEY,
    league_id INTEGER NOT NULL REFERENCES leagues(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    team_id INTEGER NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    user_alias VARCHAR(50) NOT NULL,
    joined_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints de unicidad
    CONSTRAINT ux_league_members_user_league UNIQUE (league_id, user_id),
    CONSTRAINT ux_league_members_team UNIQUE (team_id),
    CONSTRAINT ux_league_members_alias_league UNIQUE (league_id, user_alias),
    
    -- Validación de alias
    CONSTRAINT league_members_alias_chk CHECK (char_length(btrim(user_alias)) >= 1)
);

-- Índices para mejorar consultas
CREATE INDEX IF NOT EXISTS ix_league_members_league_id ON league_members(league_id);
CREATE INDEX IF NOT EXISTS ix_league_members_user_id ON league_members(user_id);
CREATE INDEX IF NOT EXISTS ix_league_members_team_id ON league_members(team_id);

-- Comentarios
COMMENT ON TABLE league_members IS 'Registro de membresía de usuarios en ligas con alias';
COMMENT ON COLUMN league_members.user_alias IS 'Alias único del usuario dentro de la liga';
COMMENT ON COLUMN league_members.joined_at IS 'Fecha y hora en que el usuario se unió a la liga';
