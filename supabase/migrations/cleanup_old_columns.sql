-- Clean up old columns from licitaciones_medicas
-- Run this after adding the new columns

-- Drop old columns that are no longer used
-- (only if they exist and after confirming data is in new columns)

-- Make old columns nullable first (safer approach)
ALTER TABLE licitaciones_medicas
  ALTER COLUMN inst_cartel_no DROP NOT NULL,
  ALTER COLUMN inst_nm DROP NOT NULL,
  ALTER COLUMN cartel_nm DROP NOT NULL,
  ALTER COLUMN cartel_no DROP NOT NULL,
  ALTER COLUMN proce_type DROP NOT NULL,
  ALTER COLUMN openbid_dt DROP NOT NULL,
  ALTER COLUMN biddoc_start_dt DROP NOT NULL,
  ALTER COLUMN supplier_nm DROP NOT NULL,
  ALTER COLUMN currency_type DROP NOT NULL,
  ALTER COLUMN amt DROP NOT NULL,
  ALTER COLUMN detalle DROP NOT NULL,
  ALTER COLUMN type_key DROP NOT NULL;

-- If you want to completely remove old columns (after verifying migration):
-- ALTER TABLE licitaciones_medicas
--   DROP COLUMN IF EXISTS inst_cartel_no,
--   DROP COLUMN IF EXISTS inst_nm,
--   DROP COLUMN IF EXISTS cartel_nm,
--   DROP COLUMN IF EXISTS cartel_no,
--   DROP COLUMN IF EXISTS proce_type,
--   DROP COLUMN IF EXISTS openbid_dt,
--   DROP COLUMN IF EXISTS biddoc_start_dt,
--   DROP COLUMN IF EXISTS supplier_nm,
--   DROP COLUMN IF EXISTS currency_type,
--   DROP COLUMN IF EXISTS amt,
--   DROP COLUMN IF EXISTS detalle,
--   DROP COLUMN IF EXISTS type_key,
--   DROP COLUMN IF EXISTS es_medica;

-- Make sure new columns have proper constraints
ALTER TABLE licitaciones_medicas
  ALTER COLUMN numero_procedimiento SET NOT NULL,
  ADD CONSTRAINT IF NOT EXISTS unique_numero_procedimiento UNIQUE (numero_procedimiento);

-- Refresh schema cache
NOTIFY pgrst, 'reload schema';
