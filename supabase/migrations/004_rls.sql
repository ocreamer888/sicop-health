-- supabase/migrations/004_rls.sql
-- Row Level Security: authenticated users can read all data.
-- ETL uses service_role key and bypasses RLS entirely — no changes needed there.

BEGIN;

-- ─────────────────────────────────────────────
-- licitaciones_medicas — authenticated READ only
-- ─────────────────────────────────────────────
ALTER TABLE licitaciones_medicas ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Authenticated users can view licitaciones"
  ON licitaciones_medicas
  FOR SELECT
  TO authenticated
  USING (true);


-- ─────────────────────────────────────────────
-- licitaciones_modificaciones — authenticated READ only
-- ─────────────────────────────────────────────
ALTER TABLE licitaciones_modificaciones ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Authenticated users can view modificaciones"
  ON licitaciones_modificaciones
  FOR SELECT
  TO authenticated
  USING (true);


-- ─────────────────────────────────────────────
-- precios_historicos — authenticated READ only
-- ─────────────────────────────────────────────
ALTER TABLE precios_historicos ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Authenticated users can view precios"
  ON precios_historicos
  FOR SELECT
  TO authenticated
  USING (true);


-- ─────────────────────────────────────────────
-- instituciones_salud — authenticated READ only
-- ─────────────────────────────────────────────
ALTER TABLE instituciones_salud ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Authenticated users can view instituciones"
  ON instituciones_salud
  FOR SELECT
  TO authenticated
  USING (true);


-- ─────────────────────────────────────────────
-- alertas_config — users manage ONLY their own rows
-- ─────────────────────────────────────────────
ALTER TABLE alertas_config ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own alerts"
  ON alertas_config
  FOR SELECT
  TO authenticated
  USING (auth.uid() = user_id);

CREATE POLICY "Users can create their own alerts"
  ON alertas_config
  FOR INSERT
  TO authenticated
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own alerts"
  ON alertas_config
  FOR UPDATE
  TO authenticated
  USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own alerts"
  ON alertas_config
  FOR DELETE
  TO authenticated
  USING (auth.uid() = user_id);

COMMIT;
