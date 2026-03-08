"use server";

import { createClient } from "@/lib/supabase/server";
import { calcStreak } from "@/lib/gamification";

export async function recordLicitacionView(instcartelno: string, instCode: string | null, biddocStartDt: string | null) {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return null;

  const today = new Date().toISOString().split("T")[0];

  // 1. Record activity (upsert — ignore duplicate)
  await supabase.from("user_activity").upsert(
    { user_id: user.id, activity_date: today },
    { onConflict: "user_id,activity_date" }
  );

  // 2. Fetch data needed for badge evaluation
  const [
    { data: existingBadges },
    { data: activityRows },
    { count: totalViews },
    { data: profile },
  ] = await Promise.all([
    supabase.from("user_badges").select("badge_id").eq("user_id", user.id),
    supabase.from("user_activity").select("activity_date").eq("user_id", user.id).order("activity_date", { ascending: false }),
    supabase.from("user_activity").select("*", { count: "exact", head: true }).eq("user_id", user.id),
    supabase.from("user_profiles").select("*").eq("user_id", user.id).single(),
  ]);

  const earnedIds = new Set(existingBadges?.map(b => b.badge_id) ?? []);
  const newBadges: string[] = [];

  // first_look
  if (!earnedIds.has("first_look") && (totalViews ?? 0) >= 1) {
    newBadges.push("first_look");
  }

  // fast_responder: licitacion published < 1h ago
  if (!earnedIds.has("fast_responder") && biddocStartDt) {
    const age = (Date.now() - new Date(biddocStartDt).getTime()) / 3_600_000;
    if (age <= 1) newBadges.push("fast_responder");
  }

  // streak_7 and streak_30
  const streak = calcStreak(activityRows?.map(r => r.activity_date) ?? []);
  if (!earnedIds.has("streak_7") && streak >= 7) newBadges.push("streak_7");
  if (!earnedIds.has("streak_30") && streak >= 30) newBadges.push("streak_30");

  // intel_pro: check if score is 100
  if (!earnedIds.has("intel_pro") && profile) {
    const { calcIntelScore } = await import("@/lib/gamification");
    const score = calcIntelScore(profile, totalViews ?? 0);
    if (score >= 100) newBadges.push("intel_pro");
  }

  // Insert new badges
  if (newBadges.length > 0) {
    await supabase.from("user_badges").insert(
      newBadges.map(badge_id => ({ user_id: user.id, badge_id }))
    );
  }

  return newBadges[0] ?? null; // return first new badge for toast display
}
