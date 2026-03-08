-- Fix RLS policies to work with server actions
-- Remove TO authenticated clause - rely on auth.uid() check only

BEGIN;

-- Drop existing policies
DROP POLICY IF EXISTS "user_profiles_select_self" ON user_profiles;
DROP POLICY IF EXISTS "user_profiles_insert_self" ON user_profiles;
DROP POLICY IF EXISTS "user_profiles_update_self" ON user_profiles;
DROP POLICY IF EXISTS "nleidas_self" ON notificaciones_leidas;
DROP POLICY IF EXISTS "activity_self" ON user_activity;
DROP POLICY IF EXISTS "badges_self" ON user_badges;

-- Recreate without TO authenticated - works with any connection that has valid JWT
CREATE POLICY "user_profiles_select_self" ON user_profiles
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "user_profiles_insert_self" ON user_profiles
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "user_profiles_update_self" ON user_profiles
  FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "nleidas_self" ON notificaciones_leidas
  FOR ALL USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);

CREATE POLICY "activity_self" ON user_activity
  FOR ALL USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);

CREATE POLICY "badges_self" ON user_badges
  FOR ALL USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);

COMMIT;
