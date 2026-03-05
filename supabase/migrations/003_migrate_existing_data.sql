-- Migration: Clean up existing database and align with new schema
-- Run this ONCE after 002_complete_schema.sql is applied

-- ============================================
-- Step 1: Make old columns nullable (if they exist)
-- ============================================
DO $$
BEGIN
    -- These columns might exist from the original schema but are no longer used
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
        ALTER COLUMN type_key DROP NOT NULL,
        ALTER COLUMN es_medica DROP NOT NULL;
EXCEPTION
    WHEN undefined_column THEN NULL;
END $$;

-- ============================================
-- Step 2: Migrate data from old columns to new columns (if needed)
-- ============================================
-- If there's existing data in old columns, copy it to new columns
UPDATE licitaciones_medicas
SET
    numero_procedimiento = COALESCE(numero_procedimiento, inst_cartel_no),
    descripcion = COALESCE(descripcion, cartel_nm),
    institucion = COALESCE(institucion, inst_nm),
    tipo_procedimiento = COALESCE(tipo_procedimiento, proce_type),
    clasificacion_unspsc = COALESCE(clasificacion_unspsc, unspsc_cd),
    monto_colones = COALESCE(monto_colones, amt),
    adjudicatario = COALESCE(adjudicatario, supplier_nm),
    estado = COALESCE(estado, CASE
        WHEN type_key = 'RPT_PUB' THEN 'Publicado'
        WHEN type_key = 'RPT_ADJ' THEN 'Adjudicado'
        ELSE NULL
    END),
    fecha_tramite = COALESCE(fecha_tramite, biddoc_start_dt::DATE),
    fecha_limite_oferta = COALESCE(fecha_limite_oferta, biddoc_end_dt::DATE)
WHERE numero_procedimiento IS NULL
   OR descripcion IS NULL
   OR institucion IS NULL;

-- ============================================
-- Step 3: Ensure new columns have proper constraints
-- ============================================
ALTER TABLE licitaciones_medicas
    ALTER COLUMN numero_procedimiento SET NOT NULL;

-- Add unique constraint if not exists
DO $$
BEGIN
    ALTER TABLE licitaciones_medicas
        ADD CONSTRAINT unique_numero_procedimiento UNIQUE (numero_procedimiento);
EXCEPTION
    WHEN duplicate_table THEN NULL;
END $$;

-- ============================================
-- Step 4: (Optional) Drop old columns after verifying migration
-- Uncomment only after confirming data is correct!
-- ============================================
/*
ALTER TABLE licitaciones_medicas
    DROP COLUMN IF EXISTS inst_cartel_no,
    DROP COLUMN IF EXISTS inst_nm,
    DROP COLUMN IF EXISTS cartel_nm,
    DROP COLUMN IF EXISTS cartel_no,
    DROP COLUMN IF EXISTS proce_type,
    DROP COLUMN IF EXISTS openbid_dt,
    DROP COLUMN IF EXISTS biddoc_start_dt,
    DROP COLUMN IF EXISTS supplier_nm,
    DROP COLUMN IF EXISTS currency_type,
    DROP COLUMN IF EXISTS amt,
    DROP COLUMN IF EXISTS detalle,
    DROP COLUMN IF EXISTS type_key,
    DROP COLUMN IF EXISTS es_medica;
*/

-- ============================================
-- Step 5: Refresh schema cache
-- ============================================
NOTIFY pgrst, 'reload schema';
