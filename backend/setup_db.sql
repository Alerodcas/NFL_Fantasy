CREATE TABLE users (
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