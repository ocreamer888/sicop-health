-- supabase/migrations/009_datos_abiertos.sql
-- Scalar enrichment columns on licitaciones_medicas (Nodes 2 and 3)
ALTER TABLE licitaciones_medicas
  ADD COLUMN IF NOT EXISTS presupuesto_estimado    NUMERIC,
  ADD COLUMN IF NOT EXISTS moneda_presupuesto      TEXT DEFAULT 'CRC',
  ADD COLUMN IF NOT EXISTS modalidad_participacion TEXT;
-- modalidad_participacion: 'Precalificación' | 'Cantidad definida' |
-- 'Según demanda' | 'Servicios' | NULL (~85% unknown)

-- Relational: offer history per procedure (Node 12)
CREATE TABLE IF NOT EXISTS da_ofertas (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  instcartelno    TEXT NOT NULL
                    REFERENCES licitaciones_medicas(instcartelno)
                    ON DELETE CASCADE,
  suppliernm      TEXT,
  suppliercd      TEXT,
  monto_oferta    NUMERIC,
  currencytype    TEXT,
  elegible        BOOLEAN,
  orden_merito    INTEGER,
  fecha_apertura  TIMESTAMPTZ,
  rawdata         JSONB,
  created_at      TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE (instcartelno, suppliercd)
);

CREATE INDEX IF NOT EXISTS idx_da_ofertas_instcartelno
  ON da_ofertas(instcartelno);
CREATE INDEX IF NOT EXISTS idx_da_ofertas_suppliercd
  ON da_ofertas(suppliercd);
CREATE INDEX IF NOT EXISTS idx_da_ofertas_elegible
  ON da_ofertas(elegible);

ALTER TABLE da_ofertas ENABLE ROW LEVEL SECURITY;
CREATE POLICY da_ofertas_select_public
  ON da_ofertas FOR SELECT USING (true);
