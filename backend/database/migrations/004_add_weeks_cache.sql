-- Migración: Agregar campo cached_weeks a seasons
-- Fecha: 2025-10-31
-- Descripción: Agrega campo para almacenar las semanas calculadas

BEGIN;

-- Agregar columna cached_weeks a seasons
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='seasons' AND column_name='cached_weeks') THEN
        ALTER TABLE seasons ADD COLUMN cached_weeks JSONB;
    END IF;
END $$;

-- Actualizar los datos existentes
UPDATE seasons s
SET cached_weeks = (
    SELECT json_agg(
        json_build_object(
            'week_number', w.week_number,
            'start_date', w.start_date,
            'end_date', w.end_date
        )
        ORDER BY w.week_number
    )
    FROM weeks w
    WHERE w.season_id = s.id
);

-- Establecer el valor por defecto primero
ALTER TABLE seasons ALTER COLUMN cached_weeks SET DEFAULT '[]'::jsonb;

-- Actualizar cualquier valor NULL existente al valor por defecto
UPDATE seasons SET cached_weeks = '[]'::jsonb WHERE cached_weeks IS NULL;

-- Ahora hacer la columna NOT NULL
ALTER TABLE seasons ALTER COLUMN cached_weeks SET NOT NULL;

-- Agregar índice GIN para búsquedas en el JSONB
CREATE INDEX IF NOT EXISTS idx_seasons_cached_weeks ON seasons USING GIN (cached_weeks);

COMMIT;