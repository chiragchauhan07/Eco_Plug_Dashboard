-- database/migrations/04_add_auth_fields_to_users.sql

-- Add new columns for persistent user authentication
ALTER TABLE users ADD COLUMN IF NOT EXISTS phone_verified BOOLEAN DEFAULT FALSE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS language VARCHAR(50);
