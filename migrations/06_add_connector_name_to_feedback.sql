-- Migration: Add connector_name column to feedback table
ALTER TABLE feedback ADD COLUMN IF NOT EXISTS connector_name TEXT;
