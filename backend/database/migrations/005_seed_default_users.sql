-- Seed default users: admin, manager, and normal user
-- Date: 2025-10-31
-- Safe to run multiple times (idempotent)

BEGIN;

-- Ensure pgcrypto is available for bcrypt hashing
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Admin user
INSERT INTO users (name, email, alias, hashed_password, profile_image_url, language, role, account_status, created_at)
VALUES (
  'Admin User',
  'admin@nflfantasy.local',
  'admin',
  crypt('Admin1234', gen_salt('bf')),
  'default_profile.png',
  'en',
  'admin',
  'active',
  NOW()
)
ON CONFLICT (email) DO NOTHING;

-- Manager user
INSERT INTO users (name, email, alias, hashed_password, profile_image_url, language, role, account_status, created_at)
VALUES (
  'Manager User',
  'manager@nflfantasy.local',
  'manager',
  crypt('Manager1234', gen_salt('bf')),
  'default_profile.png',
  'en',
  'manager',
  'active',
  NOW()
)
ON CONFLICT (email) DO NOTHING;

-- Normal user
INSERT INTO users (name, email, alias, hashed_password, profile_image_url, language, role, account_status, created_at)
VALUES (
  'Normal User',
  'user@nflfantasy.local',
  'user',
  crypt('User1234', gen_salt('bf')),
  'default_profile.png',
  'en',
  'user',
  'active',
  NOW()
)
ON CONFLICT (email) DO NOTHING;

COMMIT;
