-- Fix alertas_config RLS policies: remove TO authenticated clause
-- Matches the fix applied to other tables in 007_fix_rls_policies.sql
-- Without this, server actions that write to alertas_config may fail

-- Also adds role column to user_profiles for invite admin gating

BEGIN;

-- ─────────────────────────────────────────────
-- Add role column to user_profiles
-- ─────────────────────────────────────────────
ALTER TABLE user_profiles ADD COLUMN IF NOT EXISTS role TEXT DEFAULT 'user';

-- ─────────────────────────────────────────────
-- alertas_config: drop TO authenticated clause
-- ─────────────────────────────────────────────
DROP POLICY IF EXISTS "Users can view their own alerts" ON alertas_config;
DROP POLICY IF EXISTS "Users can create their own alerts" ON alertas_config;
DROP POLICY IF EXISTS "Users can update their own alerts" ON alertas_config;
DROP POLICY IF EXISTS "Users can delete their own alerts" ON alertas_config;

CREATE POLICY "Users can view their own alerts" ON alertas_config
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can create their own alerts" ON alertas_config
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own alerts" ON alertas_config
  FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own alerts" ON alertas_config
  FOR DELETE USING (auth.uid() = user_id);

COMMIT;
