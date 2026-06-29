-- Migration: Add support agent fields to feedback and complaints tables
ALTER TABLE feedback ADD COLUMN IF NOT EXISTS support_agent_contacted BOOLEAN DEFAULT FALSE;
ALTER TABLE feedback ADD COLUMN IF NOT EXISTS support_agent_phone TEXT;
ALTER TABLE feedback ADD COLUMN IF NOT EXISTS support_agent_name TEXT;

ALTER TABLE complaints ADD COLUMN IF NOT EXISTS support_agent_contacted BOOLEAN DEFAULT FALSE;
ALTER TABLE complaints ADD COLUMN IF NOT EXISTS support_agent_phone TEXT;
ALTER TABLE complaints ADD COLUMN IF NOT EXISTS support_agent_name TEXT;
