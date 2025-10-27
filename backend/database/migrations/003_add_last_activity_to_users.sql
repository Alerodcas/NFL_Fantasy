-- Migración: Agregar columna last_activity a tabla users
-- Fecha: 2025-10-25
-- Descripción: Agrega columna para rastrear la última actividad del usuario

ALTER TABLE users ADD COLUMN IF NOT EXISTS last_activity TIMESTAMPTZ;

-- Comentarios
COMMENT ON COLUMN users.last_activity IS 'Fecha y hora de la última actividad del usuario';