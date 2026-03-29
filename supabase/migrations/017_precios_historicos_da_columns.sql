-- supabase/migrations/017_precios_historicos_da_columns.sql
-- Add instcartelno and rawdata columns to precios_historicos.
-- The ETL (AF + C controllers) inserts these fields but they were
-- missing from the original table definition.

ALTER TABLE precios_historicos
  ADD COLUMN IF NOT EXISTS instcartelno TEXT,
  ADD COLUMN IF NOT EXISTS rawdata      JSONB;

-- Allow descripcion_item to be NULL (ETL may produce empty descriptions)
ALTER TABLE precios_historicos
  ALTER COLUMN descripcion_item DROP NOT NULL;

CREATE INDEX IF NOT EXISTS idx_precios_historicos_instcartelno
  ON precios_historicos (instcartelno)
  WHERE instcartelno IS NOT NULL;
