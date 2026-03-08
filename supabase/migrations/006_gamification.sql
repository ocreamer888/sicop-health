-- supabase/migrations/006_gamification.sql
-- Gamification tables: user_profiles, notificaciones_leidas, user_activity, user_badges

BEGIN;

-- ============================================
-- 1. user_profiles
-- ============================================
CREATE TABLE IF NOT EXISTS user_profiles (
  user_id               UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  categorias            TEXT[] DEFAULT '{}',
  instituciones         TEXT[] DEFAULT '{}',
  monto_min             NUMERIC,
  keywords              TEXT[] DEFAULT '{}',
  onboarding_completed  BOOLEAN DEFAULT FALSE,
  created_at            TIMESTAMPTZ DEFAULT NOW(),
  updated_at            TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "user_profiles_select_self" ON user_profiles
  FOR SELECT TO authenticated USING (auth.uid() = user_id);

CREATE POLICY "user_profiles_insert_self" ON user_profiles
  FOR INSERT TO authenticated WITH CHECK (auth.uid() = user_id);

CREATE POLICY "user_profiles_update_self" ON user_profiles
  FOR UPDATE TO authenticated USING (auth.uid() = user_id);

-- ============================================
-- 2. notificaciones_leidas
-- ============================================
CREATE TABLE IF NOT EXISTS notificaciones_leidas (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id         UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  notificacion_id UUID NOT NULL REFERENCES notificaciones(id) ON DELETE CASCADE,
  leido_at        TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(user_id, notificacion_id)
);

CREATE INDEX IF NOT EXISTS idx_nleidas_user ON notificaciones_leidas(user_id);
CREATE INDEX IF NOT EXISTS idx_nleidas_notif ON notificaciones_leidas(notificacion_id);

ALTER TABLE notificaciones_leidas ENABLE ROW LEVEL SECURITY;

CREATE POLICY "nleidas_self" ON notificaciones_leidas
  FOR ALL TO authenticated USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);

-- ============================================
-- 3. user_activity
-- ============================================
CREATE TABLE IF NOT EXISTS user_activity (
  user_id        UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  activity_date  DATE NOT NULL DEFAULT CURRENT_DATE,
  PRIMARY KEY (user_id, activity_date)
);

ALTER TABLE user_activity ENABLE ROW LEVEL SECURITY;

CREATE POLICY "activity_self" ON user_activity
  FOR ALL TO authenticated USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);

-- ============================================
-- 4. user_badges
-- ============================================
CREATE TABLE IF NOT EXISTS user_badges (
  user_id    UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  badge_id   TEXT NOT NULL,
  earned_at  TIMESTAMPTZ DEFAULT NOW(),
  PRIMARY KEY (user_id, badge_id)
);

ALTER TABLE user_badges ENABLE ROW LEVEL SECURITY;

CREATE POLICY "badges_self" ON user_badges
  FOR ALL TO authenticated USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);

COMMIT;
