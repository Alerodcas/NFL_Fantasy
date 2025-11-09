-- Migration: Add fantasy_team_id to league_members and relax team_id
-- Date: 2025-10-31

BEGIN;

-- Add column if not exists (Postgres 9.6+ supports IF NOT EXISTS for add column via DO block)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='league_members' AND column_name='fantasy_team_id'
    ) THEN
        ALTER TABLE league_members
            ADD COLUMN fantasy_team_id INTEGER REFERENCES fantasy_teams(id) ON DELETE CASCADE;
    END IF;
END $$;

-- Make team_id nullable to allow new rows to rely only on fantasy_team_id
ALTER TABLE league_members ALTER COLUMN team_id DROP NOT NULL;

-- Add uniqueness for fantasy_team_id to prevent duplicate membership via same fantasy team
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'ux_league_members_fantasy_team'
    ) THEN
        ALTER TABLE league_members
            ADD CONSTRAINT ux_league_members_fantasy_team UNIQUE (fantasy_team_id);
    END IF;
END $$;

COMMIT;
