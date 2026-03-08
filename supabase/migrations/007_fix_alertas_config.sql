-- Fix alertas_config schema to match app requirements
-- Adds missing columns: nombre, instituciones, monto_min, monto_max
-- Renames canal -> canales for consistency

BEGIN;

-- Add missing columns
ALTER TABLE alertas_config 
    ADD COLUMN IF NOT EXISTS nombre TEXT,
    ADD COLUMN IF NOT EXISTS instituciones TEXT[] DEFAULT '{}',
    ADD COLUMN IF NOT EXISTS monto_min NUMERIC,
    ADD COLUMN IF NOT EXISTS monto_max NUMERIC;

-- Rename canal to canales (if exists)
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'alertas_config' AND column_name = 'canal'
    ) THEN
        ALTER TABLE alertas_config RENAME COLUMN canal TO canales;
    END IF;
END $$;

-- Make nombre required for new rows (but keep nullable for existing)
-- We won't enforce NOT NULL here to avoid breaking existing data

-- Drop unspsc column if not used by app
-- ALTER TABLE alertas_config DROP COLUMN IF EXISTS unspsc;

COMMIT;
