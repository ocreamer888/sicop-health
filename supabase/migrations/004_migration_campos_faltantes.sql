-- ============================================================
-- Migration 004: Schema v2.1 — campos ETL faltantes
-- Archivo: supabase/migrations/004_schema_v2_1.sql
-- ============================================================


-- ============================================
-- 0. Drop vistas existentes (orden inverso de dependencias)
-- ============================================
DROP VIEW IF EXISTS catalogo_instituciones CASCADE;
DROP VIEW IF EXISTS resumen_por_institucion CASCADE;
DROP VIEW IF EXISTS licitaciones_por_vencer CASCADE;
DROP VIEW IF EXISTS resumen_por_categoria CASCADE;
DROP VIEW IF EXISTS licitaciones_activas CASCADE;


-- ============================================
-- 1. Columnas nuevas en licitaciones_medicas
-- ============================================
ALTER TABLE licitaciones_medicas
  ADD COLUMN IF NOT EXISTS currency_type      TEXT,
  ADD COLUMN IF NOT EXISTS instcartelno       TEXT UNIQUE,
  ADD COLUMN IF NOT EXISTS cartelno           TEXT,
  ADD COLUMN IF NOT EXISTS instnm             TEXT,
  ADD COLUMN IF NOT EXISTS cartelnm           TEXT,
  ADD COLUMN IF NOT EXISTS procetype          TEXT,
  ADD COLUMN IF NOT EXISTS tipo_procedimiento TEXT,
  ADD COLUMN IF NOT EXISTS typekey            TEXT,
  ADD COLUMN IF NOT EXISTS inst_code          TEXT,
  ADD COLUMN IF NOT EXISTS unspsc_cd          TEXT,
  ADD COLUMN IF NOT EXISTS supplier_nm        TEXT,
  ADD COLUMN IF NOT EXISTS supplier_cd        TEXT,
  ADD COLUMN IF NOT EXISTS modalidad          TEXT,
  ADD COLUMN IF NOT EXISTS excepcion_cd       TEXT,
  ADD COLUMN IF NOT EXISTS biddoc_start_dt    TIMESTAMPTZ,
  ADD COLUMN IF NOT EXISTS biddoc_end_dt      TIMESTAMPTZ,
  ADD COLUMN IF NOT EXISTS openbid_dt         TIMESTAMPTZ,
  ADD COLUMN IF NOT EXISTS adj_firme_dt       TIMESTAMPTZ,
  ADD COLUMN IF NOT EXISTS vigencia_contrato  TEXT,
  ADD COLUMN IF NOT EXISTS unidad_vigencia    TEXT,
  ADD COLUMN IF NOT EXISTS detalle            TEXT,
  ADD COLUMN IF NOT EXISTS mod_reason         TEXT;


-- ============================================
-- 2. Backfills desde raw_data
-- ============================================
UPDATE licitaciones_medicas
SET instcartelno = raw_data->>'instCartelNo'
WHERE instcartelno IS NULL
  AND raw_data->>'instCartelNo' IS NOT NULL;

UPDATE licitaciones_medicas
SET inst_code = substring(instcartelno FROM '\d+[A-Z]{2}-\d+-(\d+)')
WHERE inst_code IS NULL
  AND instcartelno IS NOT NULL;

UPDATE licitaciones_medicas
SET instnm   = raw_data->>'instNm',
    cartelnm = raw_data->>'cartelNm'
WHERE (instnm IS NULL OR cartelnm IS NULL)
  AND raw_data IS NOT NULL;

UPDATE licitaciones_medicas
SET supplier_nm = raw_data->>'supplierNm',
    supplier_cd = raw_data->>'supplierCd'
WHERE supplier_nm IS NULL
  AND raw_data IS NOT NULL;

UPDATE licitaciones_medicas
SET procetype = raw_data->>'proceType'
WHERE procetype IS NULL
  AND raw_data->>'proceType' IS NOT NULL;

UPDATE licitaciones_medicas
SET tipo_procedimiento = substring(instcartelno FROM '^\d+([A-Z]{2})-')
WHERE tipo_procedimiento IS NULL
  AND instcartelno IS NOT NULL;

UPDATE licitaciones_medicas
SET unspsc_cd = raw_data->>'unspscCd'
WHERE unspsc_cd IS NULL
  AND raw_data->>'unspscCd' IS NOT NULL;

UPDATE licitaciones_medicas
SET unspsc_cd = clasificacion_unspsc
WHERE unspsc_cd IS NULL
  AND clasificacion_unspsc IS NOT NULL;

UPDATE licitaciones_medicas
SET currency_type = raw_data->>'currency_type'
WHERE currency_type IS NULL
  AND raw_data->>'currency_type' IS NOT NULL;

UPDATE licitaciones_medicas
SET currency_type = 'CRC'
WHERE currency_type IS NULL;


-- ============================================
-- 3. Índices nuevos
-- ============================================
CREATE INDEX IF NOT EXISTS idx_licitaciones_instcartelno
  ON licitaciones_medicas(instcartelno);

CREATE INDEX IF NOT EXISTS idx_licitaciones_instnm
  ON licitaciones_medicas(instnm);

CREATE INDEX IF NOT EXISTS idx_licitaciones_inst_code
  ON licitaciones_medicas(inst_code);

CREATE INDEX IF NOT EXISTS idx_licitaciones_procetype
  ON licitaciones_medicas(procetype);

CREATE INDEX IF NOT EXISTS idx_licitaciones_tipo_proc
  ON licitaciones_medicas(tipo_procedimiento);

CREATE INDEX IF NOT EXISTS idx_licitaciones_supplier_cd
  ON licitaciones_medicas(supplier_cd);

CREATE INDEX IF NOT EXISTS idx_licitaciones_biddoc_end
  ON licitaciones_medicas(biddoc_end_dt)
  WHERE biddoc_end_dt IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_licitaciones_openbid
  ON licitaciones_medicas(openbid_dt DESC);

CREATE INDEX IF NOT EXISTS idx_licitaciones_typekey
  ON licitaciones_medicas(typekey);

CREATE INDEX IF NOT EXISTS idx_licitaciones_currency
  ON licitaciones_medicas(currency_type);


-- ============================================
-- 4. Columnas nuevas en licitaciones_modificaciones
-- ============================================
ALTER TABLE licitaciones_modificaciones
  ADD COLUMN IF NOT EXISTS inst_code  TEXT,
  ADD COLUMN IF NOT EXISTS es_medica  BOOLEAN DEFAULT FALSE,
  ADD COLUMN IF NOT EXISTS categoria  TEXT;

UPDATE licitaciones_modificaciones
SET inst_code = substring(inst_cartel_no FROM '\d+[A-Z]{2}-\d+-(\d+)')
WHERE inst_code IS NULL
  AND inst_cartel_no IS NOT NULL;


-- ============================================
-- 5. Recrear vistas
-- ============================================

-- Vista: licitaciones activas
CREATE OR REPLACE VIEW licitaciones_activas AS
SELECT *
FROM licitaciones_medicas
WHERE estado NOT IN ('Desierto', 'Cancelado', 'Desistido')
   OR estado IS NULL
ORDER BY
  COALESCE(biddoc_start_dt, fecha_tramite::TIMESTAMPTZ) DESC NULLS LAST;

COMMENT ON VIEW licitaciones_activas IS
  'Licitaciones no desiertas ni canceladas, ordenadas por fecha de publicación';


-- Vista: resumen por categoría
CREATE OR REPLACE VIEW resumen_por_categoria AS
SELECT
  categoria,
  COUNT(*)                                              AS total,
  COUNT(*) FILTER (WHERE typekey = 'RPT_PUB')           AS publicadas,
  COUNT(*) FILTER (WHERE typekey = 'RPT_ADJ')           AS adjudicadas,
  SUM(monto_colones) FILTER (WHERE currency_type = 'CRC') AS monto_crc,
  SUM(monto_colones) FILTER (WHERE currency_type = 'USD') AS monto_usd
FROM licitaciones_medicas
GROUP BY categoria
ORDER BY total DESC;

COMMENT ON VIEW resumen_por_categoria IS
  'Resumen de licitaciones por categoría médica con montos separados por moneda';


-- Vista: licitaciones por vencer (próximos 7 días)
CREATE OR REPLACE VIEW licitaciones_por_vencer AS
SELECT
  instcartelno,
  cartelnm,
  instnm,
  inst_code,
  categoria,
  tipo_procedimiento,
  unspsc_cd,
  currency_type,
  monto_colones       AS amt,
  biddoc_end_dt       AS deadline,
  openbid_dt,
  biddoc_start_dt     AS publicado_dt,
  es_medica
FROM licitaciones_medicas
WHERE biddoc_end_dt BETWEEN NOW() AND (NOW() + INTERVAL '7 days')
  AND es_medica = true
ORDER BY biddoc_end_dt ASC;

COMMENT ON VIEW licitaciones_por_vencer IS
  'Licitaciones médicas con deadline en los próximos 7 días';


-- Vista: resumen por institución
CREATE OR REPLACE VIEW resumen_por_institucion AS
SELECT
  instnm,
  inst_code,
  COUNT(*)                                              AS total,
  COUNT(*) FILTER (WHERE es_medica = true)              AS medicas,
  COUNT(*) FILTER (WHERE typekey = 'RPT_PUB')           AS publicadas,
  COUNT(*) FILTER (WHERE typekey = 'RPT_ADJ')           AS adjudicadas,
  SUM(monto_colones) FILTER (WHERE currency_type = 'CRC') AS monto_crc,
  SUM(monto_colones) FILTER (WHERE currency_type = 'USD') AS monto_usd
FROM licitaciones_medicas
WHERE instnm IS NOT NULL
GROUP BY instnm, inst_code
ORDER BY medicas DESC;

COMMENT ON VIEW resumen_por_institucion IS
  'Resumen por unidad de compra — útil para dashboard institucional';


-- Vista: catálogo de instituciones (dropdown frontend)
CREATE OR REPLACE VIEW catalogo_instituciones AS
SELECT
  inst_code,
  instnm                                              AS nombre,
  COUNT(*) OVER (PARTITION BY inst_code)              AS total_licitaciones
FROM licitaciones_medicas
WHERE inst_code IS NOT NULL
  AND instnm IS NOT NULL
GROUP BY inst_code, instnm
ORDER BY nombre;

COMMENT ON VIEW catalogo_instituciones IS
  'Catálogo auto-generado de instituciones activas en SICOP — se puebla con el ETL';


-- ============================================
-- 6. Refresh schema cache
-- ============================================
NOTIFY pgrst, 'reload schema';
