-- Add canales column to alertas_config if missing
-- The app expects this column for notification channels

DO $$
BEGIN
    -- Add canales column if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'alertas_config' AND column_name = 'canales'
    ) THEN
        ALTER TABLE alertas_config ADD COLUMN canales TEXT[] DEFAULT ARRAY['email'];
    END IF;
END $$;

-- Also ensure canal is removed if it exists (we prefer canales)
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'alertas_config' AND column_name = 'canal'
    ) THEN
        ALTER TABLE alertas_config DROP COLUMN IF EXISTS canal;
    END IF;
END $$;
