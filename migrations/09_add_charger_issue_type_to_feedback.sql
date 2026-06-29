-- Migration: Add charger_issue_type column to feedback table
ALTER TABLE feedback ADD COLUMN IF NOT EXISTS charger_issue_type TEXT;
