-- Migration: Add issue_category column to feedback table
ALTER TABLE feedback ADD COLUMN IF NOT EXISTS issue_category TEXT;
