CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    email VARCHAR(50) UNIQUE NOT NULL,
    alias VARCHAR(50) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    profile_image_url VARCHAR(255) DEFAULT 'default_profile.png',
    language VARCHAR(10) DEFAULT 'en',
    role VARCHAR(20) DEFAULT 'manager',
    account_status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    failed_login_attempts INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS leagues (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100) UNIQUE NOT NULL,
  created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS teams (
  id SERIAL PRIMARY KEY,
  league_id INTEGER NOT NULL REFERENCES leagues(id) ON DELETE CASCADE,
  owner_user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  name VARCHAR(128) NOT NULL,
  description VARCHAR(512),
  logo_url VARCHAR(512),
  created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
  UNIQUE (league_id, name)
);

SELECT id, name, league_id FROM teams;


