-- supabase/migrations/016_catalogo_bienes.sql
-- Product code catalog from Datos Abiertos Report 10 (CE_DA_CB_CONTROLLER_JSON)
-- 3-level UNSPSC-based hierarchy:
--   codigo_clasificacion (8 digits) → familia UNSPSC
--   codigo_identificacion (16 digits) → first 8 = clasificacion + 8 consecutive
--   codigo_producto (24 digits, nullable) → first 16 = identificacion + additional

CREATE TABLE IF NOT EXISTS catalogo_bienes (
  codigo_clasificacion      TEXT,
  codigo_identificacion     TEXT PRIMARY KEY,
  codigo_producto           TEXT,
  descripcion_clasificacion TEXT,
  descripcion_identificacion TEXT,
  descripcion_producto      TEXT,
  rawdata                   JSONB,
  updated_at                TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_catalogo_clasificacion
  ON catalogo_bienes (codigo_clasificacion);
CREATE INDEX IF NOT EXISTS idx_catalogo_producto
  ON catalogo_bienes (codigo_producto)
  WHERE codigo_producto IS NOT NULL;
