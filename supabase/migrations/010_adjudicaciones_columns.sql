-- supabase/migrations/010_adjudicaciones_columns.sql
-- Adjudication enrichment columns on licitaciones_medicas (AF report / G2 task)
ALTER TABLE licitaciones_medicas
  ADD COLUMN IF NOT EXISTS fecha_adj_firme  TIMESTAMPTZ,
  ADD COLUMN IF NOT EXISTS desierto         BOOLEAN DEFAULT false;

-- fecha_adj_firme: date the adjudication became firm (FECHA_ADJ_FIRME from AF report)
-- desierto: true when the procedure was declared desert ("N" = false, anything else = true)
