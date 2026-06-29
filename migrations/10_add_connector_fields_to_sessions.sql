-- Migration: Add connector_number and charging_amount columns to charging_sessions table
ALTER TABLE charging_sessions ADD COLUMN IF NOT EXISTS connector_number INTEGER;
ALTER TABLE charging_sessions ADD COLUMN IF NOT EXISTS charging_amount INTEGER;

-- Add wallet_balance column to users table
ALTER TABLE users ADD COLUMN IF NOT EXISTS wallet_balance INTEGER DEFAULT 150;
