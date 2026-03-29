-- supabase/migrations/020_drop_ordenes_pedido_fk.sql
-- Drop FK constraint on da_ordenes_pedido.instcartelno.
-- Same pattern as 018/019: the OP controller returns data for all SICOP
-- procedures, not just those tracked in licitaciones_medicas.

ALTER TABLE da_ordenes_pedido
  DROP CONSTRAINT IF EXISTS da_ordenes_pedido_instcartelno_fkey;
