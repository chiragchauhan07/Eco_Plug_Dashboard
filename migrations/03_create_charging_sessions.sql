-- 1. Add new columns to charging_sessions table if they do not exist
ALTER TABLE charging_sessions ADD COLUMN IF NOT EXISTS session_id TEXT;
ALTER TABLE charging_sessions ADD COLUMN IF NOT EXISTS user_phone TEXT;
ALTER TABLE charging_sessions ADD COLUMN IF NOT EXISTS charger_name TEXT;
ALTER TABLE charging_sessions ADD COLUMN IF NOT EXISTS connector_type TEXT;
ALTER TABLE charging_sessions ADD COLUMN IF NOT EXISTS status TEXT DEFAULT 'ACTIVE';
ALTER TABLE charging_sessions ADD COLUMN IF NOT EXISTS start_time TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now());
ALTER TABLE charging_sessions ADD COLUMN IF NOT EXISTS end_time TIMESTAMP WITH TIME ZONE;
ALTER TABLE charging_sessions ADD COLUMN IF NOT EXISTS wallet_deduction NUMERIC DEFAULT 0;
ALTER TABLE charging_sessions ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now());

-- 2. Backfill existing records from relative tables
UPDATE charging_sessions SET session_id = session_code WHERE session_id IS NULL AND session_code IS NOT NULL;
UPDATE charging_sessions cs SET user_phone = u.phone_number FROM users u WHERE cs.user_id = u.id AND cs.user_phone IS NULL;
UPDATE charging_sessions cs SET charger_name = cl.charger_name FROM charger_locations cl WHERE cs.charger_id = cl.id AND cs.charger_name IS NULL;

-- Populate default values for existing rows
UPDATE charging_sessions SET status = 'COMPLETED' WHERE status IS NULL;
UPDATE charging_sessions SET start_time = session_date WHERE start_time IS NULL AND session_date IS NOT NULL;
UPDATE charging_sessions SET created_at = session_date WHERE created_at IS NULL AND session_date IS NOT NULL;
UPDATE charging_sessions SET wallet_deduction = amount_paid WHERE wallet_deduction = 0 AND amount_paid IS NOT NULL;
UPDATE charging_sessions SET connector_type = 'TYPE-2' WHERE connector_type IS NULL;

-- 3. Enforce constraint to ensure session_id is UNIQUE and NOT NULL
-- (Generate unique session ids for rows that might still be null to prevent constraint violation)
UPDATE charging_sessions SET session_id = 'SES-HIST-' || SUBSTRING(id::text, 1, 8) WHERE session_id IS NULL;
UPDATE charging_sessions SET user_phone = '919999999999' WHERE user_phone IS NULL;
UPDATE charging_sessions SET charger_name = 'Unknown Charger' WHERE charger_name IS NULL;

ALTER TABLE charging_sessions ALTER COLUMN session_id SET NOT NULL;
ALTER TABLE charging_sessions ALTER COLUMN user_phone SET NOT NULL;
ALTER TABLE charging_sessions ALTER COLUMN charger_name SET NOT NULL;
ALTER TABLE charging_sessions ALTER COLUMN connector_type SET NOT NULL;

-- Drop NOT NULL constraints on legacy columns to prevent errors during inserts
ALTER TABLE charging_sessions ALTER COLUMN session_code DROP NOT NULL;
ALTER TABLE charging_sessions ALTER COLUMN user_id DROP NOT NULL;
ALTER TABLE charging_sessions ALTER COLUMN charger_id DROP NOT NULL;
ALTER TABLE charging_sessions ALTER COLUMN duration_minutes DROP NOT NULL;
ALTER TABLE charging_sessions ALTER COLUMN amount_paid DROP NOT NULL;
ALTER TABLE charging_sessions ALTER COLUMN payment_status DROP NOT NULL;
ALTER TABLE charging_sessions ALTER COLUMN session_date DROP NOT NULL;

-- Ensure UNIQUE constraint
ALTER TABLE charging_sessions DROP CONSTRAINT IF EXISTS charging_sessions_session_id_key;
ALTER TABLE charging_sessions ADD CONSTRAINT charging_sessions_session_id_key UNIQUE (session_id);
