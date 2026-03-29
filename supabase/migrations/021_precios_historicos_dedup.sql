-- supabase/migrations/021_precios_historicos_dedup.sql
-- Add dedup index and fuente index to precios_historicos so the ETL can
-- use upsert(ignore_duplicates=True) safely on repeated runs.
--
-- The unique key is (instcartelno, proveedor, fuente, precio_unitario, cantidad)
-- — close enough to a natural key for AF/C pricing records.
-- Only applied when instcartelno and fuente are present (DA rows).
--
-- Also clean up duplicate AF/C rows accumulated from multiple ETL runs before
-- this index was in place.

-- Step 1: remove duplicates, keeping the row with the lowest id (or ctid)
DELETE FROM precios_historicos
WHERE fuente IN ('AF', 'C')
  AND id NOT IN (
    SELECT DISTINCT ON (instcartelno, proveedor, fuente, precio_unitario, cantidad) id
    FROM precios_historicos
    WHERE fuente IN ('AF', 'C')
    ORDER BY instcartelno, proveedor, fuente, precio_unitario, cantidad, id
  );

-- Step 2: add the unique index (partial — only DA rows)
CREATE UNIQUE INDEX IF NOT EXISTS idx_precios_historicos_dedup
  ON precios_historicos (instcartelno, proveedor, fuente, precio_unitario, cantidad)
  WHERE instcartelno IS NOT NULL AND fuente IS NOT NULL;

-- Step 3: add index on fuente for fast deletes / filters
CREATE INDEX IF NOT EXISTS idx_precios_historicos_fuente
  ON precios_historicos (fuente)
  WHERE fuente IS NOT NULL;
