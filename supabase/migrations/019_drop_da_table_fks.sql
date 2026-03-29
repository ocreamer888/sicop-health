-- supabase/migrations/019_drop_da_table_fks.sql
-- Drop FK constraints on da_recursos and da_aclaraciones instcartelno columns.
--
-- The R (Recursos) and A (Aclaraciones) controllers return data for ALL SICOP
-- procedures, not just those tracked in licitaciones_medicas. The FK prevents
-- inserting valid records for non-medical or out-of-range procedures.

ALTER TABLE da_recursos
  DROP CONSTRAINT IF EXISTS da_recursos_instcartelno_fkey;

ALTER TABLE da_aclaraciones
  DROP CONSTRAINT IF EXISTS da_aclaraciones_instcartelno_fkey;
