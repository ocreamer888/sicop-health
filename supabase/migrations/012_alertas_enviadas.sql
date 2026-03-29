-- Deduplication table for personalized email/WhatsApp notifications.
-- Tracks which (alerta_id, instcartelno) pairs have already been notified,
-- preventing the ETL from re-sending the same licitacion on subsequent runs.

BEGIN;

CREATE TABLE IF NOT EXISTS alertas_enviadas (
  alerta_id    UUID NOT NULL REFERENCES alertas_config(id) ON DELETE CASCADE,
  instcartelno TEXT NOT NULL REFERENCES licitaciones_medicas(instcartelno) ON DELETE CASCADE,
  sent_at      TIMESTAMPTZ DEFAULT NOW(),
  PRIMARY KEY (alerta_id, instcartelno)
);

CREATE INDEX IF NOT EXISTS idx_alertas_enviadas_alerta ON alertas_enviadas(alerta_id);

-- Only the ETL service role writes to this table; no client access needed
ALTER TABLE alertas_enviadas ENABLE ROW LEVEL SECURITY;

COMMIT;
