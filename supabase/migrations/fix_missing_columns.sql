-- Fix missing columns in licitaciones_medicas
-- Run this in Supabase SQL Editor if migrations weren't applied

-- Base columns that might be missing
ALTER TABLE licitaciones_medicas
  ADD COLUMN IF NOT EXISTS numero_procedimiento TEXT UNIQUE,
  ADD COLUMN IF NOT EXISTS descripcion TEXT,
  ADD COLUMN IF NOT EXISTS institucion TEXT,
  ADD COLUMN IF NOT EXISTS tipo_procedimiento TEXT,
  ADD COLUMN IF NOT EXISTS clasificacion_unspsc TEXT,
  ADD COLUMN IF NOT EXISTS categoria TEXT,
  ADD COLUMN IF NOT EXISTS monto_colones NUMERIC,
  ADD COLUMN IF NOT EXISTS adjudicatario TEXT,
  ADD COLUMN IF NOT EXISTS estado TEXT,
  ADD COLUMN IF NOT EXISTS fecha_tramite DATE,
  ADD COLUMN IF NOT EXISTS fecha_limite_oferta DATE,
  ADD COLUMN IF NOT EXISTS raw_data JSONB;

-- v2.1 columns
ALTER TABLE licitaciones_medicas
  ADD COLUMN IF NOT EXISTS unspsc_cd TEXT,
  ADD COLUMN IF NOT EXISTS supplier_cd TEXT,
  ADD COLUMN IF NOT EXISTS modalidad TEXT,
  ADD COLUMN IF NOT EXISTS excepcion_cd TEXT,
  ADD COLUMN IF NOT EXISTS biddoc_end_dt TIMESTAMPTZ,
  ADD COLUMN IF NOT EXISTS adj_firme_dt TIMESTAMPTZ,
  ADD COLUMN IF NOT EXISTS vigencia_contrato TEXT,
  ADD COLUMN IF NOT EXISTS unidad_vigencia TEXT,
  ADD COLUMN IF NOT EXISTS cartel_cate TEXT;

-- Drop and recreate the licitaciones_activas view to include new columns
DROP VIEW IF EXISTS licitaciones_activas;

CREATE VIEW licitaciones_activas AS
SELECT *
FROM licitaciones_medicas
WHERE estado NOT IN ('Desierto', 'Cancelado', 'Desistido')
   OR estado IS NULL
ORDER BY fecha_tramite DESC NULLS LAST;

-- Refresh PostgREST schema cache
NOTIFY pgrst, 'reload schema';
