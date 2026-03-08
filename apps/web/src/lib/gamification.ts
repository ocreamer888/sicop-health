import type { UserProfile } from "./types";

export function calcIntelScore(
  profile: UserProfile | null,
  activityCount: number,
): number {
  if (!profile) return 0;
  let score = 0;
  if (profile.onboarding_completed)       score += 30;
  if (profile.categorias.length > 0)      score += 20;
  if (profile.instituciones.length > 0)   score += 20;
  if (profile.monto_min !== null)         score += 15;
  if (activityCount >= 5)                 score += 15;
  return Math.min(score, 100);
}

export function calcStreak(activityDates: string[]): number {
  if (activityDates.length === 0) return 0;

  // activityDates: sorted DESC, format "YYYY-MM-DD"
  const sorted = [...activityDates].sort().reverse();
  const today = new Date().toISOString().split("T")[0];
  const yesterday = new Date(Date.now() - 86_400_000).toISOString().split("T")[0];

  // Streak must include today or yesterday to be "active"
  if (sorted[0] !== today && sorted[0] !== yesterday) return 0;

  let streak = 1;
  for (let i = 1; i < sorted.length; i++) {
    const expected = subtractDays(sorted[i - 1], 1);
    if (sorted[i] === expected) {
      streak++;
    } else {
      break;
    }
  }
  return streak;
}

function subtractDays(dateStr: string, days: number): string {
  const d = new Date(dateStr);
  d.setDate(d.getDate() - days);
  return d.toISOString().split("T")[0];
}

export function getIntelScoreNextAction(
  profile: UserProfile | null,
  activityCount: number,
): string | null {
  if (!profile || !profile.onboarding_completed) return "Completa tu perfil de monitoreo";
  if (profile.categorias.length === 0) return "Agrega las categorías que te interesan";
  if (profile.instituciones.length === 0) return "Selecciona las instituciones objetivo";
  if (profile.monto_min === null) return "Define el monto mínimo de oportunidades";
  if (activityCount < 5) return `Revisa ${5 - activityCount} licitaciones más para completar tu Intel Score`;
  return null;
}

export function getUrgencyLevel(biddocEndDt: string | null): "hot" | "urgent" | null {
  if (!biddocEndDt) return null;
  const ms = new Date(biddocEndDt).getTime() - Date.now();
  const hours = ms / 3_600_000;
  if (hours <= 0) return null;
  if (hours <= 24) return "urgent";
  if (hours <= 72) return "hot";
  return null;
}

export function hoursUntil(dt: string): number {
  return Math.max(0, (new Date(dt).getTime() - Date.now()) / 3_600_000);
}
