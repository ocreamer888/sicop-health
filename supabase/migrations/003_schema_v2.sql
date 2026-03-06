-- supabase/migrations/003_schema_v2_full.sql
-- Migration definitiva: elimina schema v1, consolida en v2
-- Safe to run: todas las operaciones son IF EXISTS / IF NOT EXISTS

BEGIN;

-- ─────────────────────────────────────────────
-- STEP 1: Ver qué hace licitaciones_activas
-- (correr esto primero por separado, confirmar antes de continuar)
-- ─────────────────────────────────────────────
-- SELECT pg_get_viewdef('licitaciones_activas', true);


-- ─────────────────────────────────────────────
-- STEP 2: Dropear view dependiente
-- ─────────────────────────────────────────────
DROP VIEW IF EXISTS licitaciones_activas;


-- ─────────────────────────────────────────────
-- STEP 3: Limpiar columnas v1 legacy de licitaciones_medicas
-- ─────────────────────────────────────────────
ALTER TABLE licitaciones_medicas
  -- Identidad legacy → reemplazada por instcartelno
  DROP COLUMN IF EXISTS numero_procedimiento,
  -- Aliases redundantes → ya existen como cartelnm, instnm, supplier_nm, unspsc_cd
  DROP COLUMN IF EXISTS descripcion,
  DROP COLUMN IF EXISTS institucion,
  DROP COLUMN IF EXISTS adjudicatario,
  DROP COLUMN IF EXISTS clasificacion_unspsc,
  -- Aliases de fechas → ya existen como biddoc_start_dt, biddoc_end_dt
  DROP COLUMN IF EXISTS fecha_tramite,
  DROP COLUMN IF EXISTS fecha_limite_oferta;


-- ─────────────────────────────────────────────
-- STEP 4: instcartelno → NOT NULL (ahora es la identidad real)
-- ─────────────────────────────────────────────
UPDATE licitaciones_medicas
  SET instcartelno = id::text
  WHERE instcartelno IS NULL;  -- fix de rows huérfanas si las hubiera

ALTER TABLE licitaciones_medicas
  ALTER COLUMN instcartelno SET NOT NULL;


-- ─────────────────────────────────────────────
-- STEP 5: Limpiar precios_historicos
-- ─────────────────────────────────────────────
-- numero_procedimiento ya no tiene FK (fue migrada a instcartelno)
-- Dejarla como columna nullable para referencia histórica está OK,
-- pero limpiar el nombre de la FK vieja si quedó colgada
ALTER TABLE precios_historicos
  DROP COLUMN IF EXISTS numero_procedimiento;


-- ─────────────────────────────────────────────
-- STEP 6: Recrear licitaciones_activas sobre schema v2
-- ─────────────────────────────────────────────
CREATE OR REPLACE VIEW licitaciones_activas AS
SELECT
  instcartelno,
  cartelno,
  instnm,
  cartelnm,
  procetype,
  tipo_procedimiento,
  typekey,
  estado,
  es_medica,
  categoria,
  unspsc_cd,
  supplier_nm,
  supplier_cd,
  monto_colones,
  currency_type,
  detalle,
  biddoc_start_dt,
  biddoc_end_dt,
  openbid_dt,
  adj_firme_dt,
  vigencia_contrato,
  unidad_vigencia,
  modalidad,
  excepcion_cd,
  cartel_cate,
  inst_code,
  raw_data,
  created_at,
  updated_at
FROM licitaciones_medicas
WHERE estado = 'Publicado';


-- ─────────────────────────────────────────────
-- STEP 7: Índices para performance del frontend
-- ─────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_licitaciones_estado
  ON licitaciones_medicas (estado);

CREATE INDEX IF NOT EXISTS idx_licitaciones_es_medica
  ON licitaciones_medicas (es_medica);

CREATE INDEX IF NOT EXISTS idx_licitaciones_categoria
  ON licitaciones_medicas (categoria)
  WHERE es_medica = true;

CREATE INDEX IF NOT EXISTS idx_licitaciones_instnm
  ON licitaciones_medicas (instnm);

CREATE INDEX IF NOT EXISTS idx_licitaciones_biddoc_end
  ON licitaciones_medicas (biddoc_end_dt)
  WHERE es_medica = true;

CREATE INDEX IF NOT EXISTS idx_licitaciones_biddoc_start
  ON licitaciones_medicas (biddoc_start_dt DESC);

CREATE INDEX IF NOT EXISTS idx_precios_instcartelno
  ON precios_historicos (instcartelno);


COMMIT;
