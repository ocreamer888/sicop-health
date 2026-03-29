-- Tracks which licitaciones each user has viewed (one row per user+licitacion).
-- Used to evaluate the ccss_specialist badge (20+ CCSS tenders reviewed).
-- Separate from user_activity (which tracks active days for streak, not which tenders).

BEGIN;

CREATE TABLE IF NOT EXISTS licitaciones_vistas (
  user_id      UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  instcartelno TEXT NOT NULL,
  instnm       TEXT,
  viewed_at    TIMESTAMPTZ DEFAULT NOW(),
  PRIMARY KEY (user_id, instcartelno)
);

CREATE INDEX IF NOT EXISTS idx_licitaciones_vistas_user ON licitaciones_vistas(user_id);

ALTER TABLE licitaciones_vistas ENABLE ROW LEVEL SECURITY;

CREATE POLICY "licitaciones_vistas_self" ON licitaciones_vistas
  FOR ALL USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);

COMMIT;
