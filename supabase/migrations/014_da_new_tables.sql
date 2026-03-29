-- supabase/migrations/014_da_new_tables.sql
-- Adds fuente column to precios_historicos and creates 3 new Datos Abiertos tables:
-- da_recursos (appeals/protests), da_aclaraciones (clarifications), da_ordenes_pedido (purchase orders)

-- ─── precios_historicos: add fuente column ────────────────────────────────────
-- Distinguishes price records by source: AF (adjudicated), C (contracted)
ALTER TABLE precios_historicos
  ADD COLUMN IF NOT EXISTS fuente TEXT;

-- ─── da_recursos — Appeals / protests per tender (Report 4 / G6) ─────────────
CREATE TABLE IF NOT EXISTS da_recursos (
  id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  instcartelno     TEXT NOT NULL REFERENCES licitaciones_medicas(instcartelno) ON DELETE CASCADE,
  asunto           TEXT,
  cedula_proveedor TEXT,
  tipo_recurso     TEXT,
  fecha_solicitud  TIMESTAMPTZ,
  rawdata          JSONB,
  created_at       TIMESTAMPTZ DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_da_recursos_dedup
  ON da_recursos (instcartelno, cedula_proveedor, fecha_solicitud)
  WHERE cedula_proveedor IS NOT NULL AND fecha_solicitud IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_da_recursos_instcartelno
  ON da_recursos (instcartelno);

-- ─── da_aclaraciones — Clarifications per tender (Report 3 / G5) ─────────────
CREATE TABLE IF NOT EXISTS da_aclaraciones (
  id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  instcartelno     TEXT NOT NULL REFERENCES licitaciones_medicas(instcartelno) ON DELETE CASCADE,
  titulo           TEXT,
  fecha_solicitud  TIMESTAMPTZ,
  solicitante      TEXT,
  rawdata          JSONB,
  created_at       TIMESTAMPTZ DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_da_aclaraciones_dedup
  ON da_aclaraciones (instcartelno, fecha_solicitud, solicitante)
  WHERE fecha_solicitud IS NOT NULL AND solicitante IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_da_aclaraciones_instcartelno
  ON da_aclaraciones (instcartelno);

-- ─── da_ordenes_pedido — Purchase orders (Report 8 / G11) ─────────────────────
CREATE TABLE IF NOT EXISTS da_ordenes_pedido (
  id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  instcartelno     TEXT REFERENCES licitaciones_medicas(instcartelno) ON DELETE SET NULL,
  numero_orden     TEXT NOT NULL,
  cedula_proveedor TEXT,
  precio_unitario  NUMERIC,
  cantidad         NUMERIC,
  unidad           TEXT,
  monto_total      NUMERIC,
  currencytype     TEXT,
  fecha_orden      TIMESTAMPTZ,
  rawdata          JSONB,
  created_at       TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE (numero_orden)
);

CREATE INDEX IF NOT EXISTS idx_da_ordenes_instcartelno
  ON da_ordenes_pedido (instcartelno);
CREATE INDEX IF NOT EXISTS idx_da_ordenes_cedula
  ON da_ordenes_pedido (cedula_proveedor);
