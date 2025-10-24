-- Migración: Actualizar tabla seasons y crear tabla weeks
-- Fecha: 2024
-- Descripción: Agrega campos de nombre, fechas y week_count a seasons, crea tabla weeks

BEGIN;

-- Agregar columnas faltantes a seasons (si no existen)
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='seasons' AND column_name='name') THEN
        ALTER TABLE seasons ADD COLUMN name VARCHAR(100);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='seasons' AND column_name='start_date') THEN
        ALTER TABLE seasons ADD COLUMN start_date DATE;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='seasons' AND column_name='end_date') THEN
        ALTER TABLE seasons ADD COLUMN end_date DATE;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='seasons' AND column_name='week_count') THEN
        ALTER TABLE seasons ADD COLUMN week_count INTEGER;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='seasons' AND column_name='created_by') THEN
        ALTER TABLE seasons ADD COLUMN created_by INTEGER REFERENCES users(id) ON DELETE RESTRICT;
    END IF;
END $$;

-- Actualizar datos existentes si hay registros
UPDATE seasons 
SET name = 'Season ' || year::text,
    start_date = (year::text || '-09-01')::date,
    end_date = ((year + 1)::text || '-02-28')::date,
    week_count = 18
WHERE name IS NULL;

-- Hacer columnas NOT NULL
ALTER TABLE seasons ALTER COLUMN name SET NOT NULL;
ALTER TABLE seasons ALTER COLUMN start_date SET NOT NULL;
ALTER TABLE seasons ALTER COLUMN end_date SET NOT NULL;
ALTER TABLE seasons ALTER COLUMN week_count SET NOT NULL;

-- Agregar constraints
ALTER TABLE seasons ADD CONSTRAINT unique_season_name UNIQUE (name);
ALTER TABLE seasons ADD CONSTRAINT check_week_count CHECK (week_count > 0);
ALTER TABLE seasons ADD CONSTRAINT check_end_after_start CHECK (end_date > start_date);

-- Crear tabla weeks si no existe
CREATE TABLE IF NOT EXISTS weeks (
    id SERIAL PRIMARY KEY,
    season_id INTEGER NOT NULL REFERENCES seasons(id) ON DELETE CASCADE,
    week_number INTEGER NOT NULL CHECK (week_number > 0),
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    CONSTRAINT week_end_after_start CHECK (end_date > start_date),
    CONSTRAINT unique_week_per_season UNIQUE (season_id, week_number)
);

-- Crear índices
CREATE INDEX IF NOT EXISTS idx_weeks_season_id ON weeks(season_id);
CREATE INDEX IF NOT EXISTS idx_seasons_is_current ON seasons(is_current) WHERE is_current = TRUE;
CREATE INDEX IF NOT EXISTS idx_seasons_dates ON seasons(start_date, end_date);

COMMIT;
