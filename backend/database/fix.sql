-- 0) Safety: required extensions
CREATE EXTENSION IF NOT EXISTS citext;
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- 1) Add league_id to teams (nullable to keep current behavior)
ALTER TABLE teams
  ADD COLUMN IF NOT EXISTS league_id INTEGER REFERENCES leagues(id) ON DELETE CASCADE;

-- 2) Drop previous global unique on name (added in current_db.sql)
--    (Name might be teams_name_unique or generated; handle both)
DO $$
DECLARE
  constr_name text;
BEGIN
  SELECT constraint_name INTO constr_name
  FROM information_schema.table_constraints
  WHERE table_name = 'teams'
    AND constraint_type = 'UNIQUE';

  IF constr_name IS NOT NULL THEN
    EXECUTE format('ALTER TABLE teams DROP CONSTRAINT IF EXISTS %I', constr_name);
  END IF;
END$$;

-- 3) Recreate uniqueness in two parts:

-- Unicidad global, case-insensitive, por nombre de equipo
DROP INDEX IF EXISTS ux_teams_name_when_no_league;
DROP INDEX IF EXISTS ux_teams_league_name;

CREATE UNIQUE INDEX IF NOT EXISTS ux_teams_name_global
  ON teams (LOWER(name::text));

CREATE INDEX IF NOT EXISTS ix_teams_league_id ON teams (league_id);
CREATE INDEX IF NOT EXISTS ix_teams_created_by ON teams (created_by);

-- Eliminar columna last_login si existe
ALTER TABLE users DROP COLUMN IF EXISTS last_login;

-- Agregar columna last_activity
ALTER TABLE users ADD COLUMN IF NOT EXISTS last_activity TIMESTAMP WITH TIME ZONE;

-- Agregar columna failed_login_attempts si no existe
ALTER TABLE users ADD COLUMN IF NOT EXISTS failed_login_attempts INTEGER DEFAULT 0;

-- Actualizar failed_login_attempts a 0 donde sea NULL
UPDATE users SET failed_login_attempts = 0 WHERE failed_login_attempts IS NULL;

-- Verificar cambios
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'users' 
ORDER BY ordinal_position;





