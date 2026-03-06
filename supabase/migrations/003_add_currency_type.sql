-- Add currency_type column to licitaciones_medicas
-- This fixes the design issue where USD amounts were stored in monto_colones

-- 1. Add the column
ALTER TABLE licitaciones_medicas
  ADD COLUMN IF NOT EXISTS currency_type TEXT;

-- 2. Backfill from raw_data JSONB
UPDATE licitaciones_medicas
SET currency_type = raw_data->>'currency_type'
WHERE currency_type IS NULL
  AND raw_data->>'currency_type' IS NOT NULL;

-- 3. Set default for rows without currency info (assume CRC based on column name)
UPDATE licitaciones_medicas
SET currency_type = 'CRC'
WHERE currency_type IS NULL;

-- 4. Create index for filtering by currency
CREATE INDEX IF NOT EXISTS idx_licitaciones_currency
  ON licitaciones_medicas(currency_type);

-- 5. Refresh schema cache
NOTIFY pgrst, 'reload schema';
