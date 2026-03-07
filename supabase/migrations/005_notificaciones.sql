-- supabase/migrations/005_notificaciones.sql
-- Notification inbox: one row per new licitacion detected by the webhook.
-- Written only by the edge function (service_role). Read by all authenticated users.

BEGIN;

CREATE TABLE IF NOT EXISTS notificaciones (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  instcartelno  TEXT NOT NULL REFERENCES licitaciones_medicas(instcartelno) ON DELETE CASCADE,
  created_at    TIMESTAMPTZ DEFAULT NOW()
);

-- Prevent duplicate notifications for the same licitacion
CREATE UNIQUE INDEX IF NOT EXISTS idx_notificaciones_instcartelno
  ON notificaciones(instcartelno);

CREATE INDEX IF NOT EXISTS idx_notificaciones_created_at
  ON notificaciones(created_at DESC);

-- RLS: all authenticated users can read, no one can write via client (service_role only)
ALTER TABLE notificaciones ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Authenticated users can view notificaciones"
  ON notificaciones
  FOR SELECT
  TO authenticated
  USING (true);

COMMIT;
