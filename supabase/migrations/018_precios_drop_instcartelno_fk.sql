-- supabase/migrations/018_precios_drop_instcartelno_fk.sql
-- Drop the FK constraint on precios_historicos.instcartelno.
--
-- The C (Contratos) controller returns pricing rows for ALL procedures in SICOP,
-- not just the ones tracked in licitaciones_medicas. Enforcing referential integrity
-- here would silently discard valid price history for procedures we haven't ingested yet.
-- The instcartelno column remains indexed for lookups; integrity is handled at query time.

ALTER TABLE precios_historicos
  DROP CONSTRAINT IF EXISTS precios_historicos_instcartelno_fkey;
