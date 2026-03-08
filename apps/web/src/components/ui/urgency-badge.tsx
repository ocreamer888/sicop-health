import { hoursUntil } from "@/lib/gamification";

interface UrgencyBadgeProps {
  biddocEndDt: string | null;
}

export function UrgencyBadge({ biddocEndDt }: UrgencyBadgeProps) {
  if (!biddocEndDt) return null;
  const hours = hoursUntil(biddocEndDt);
  if (hours <= 0 || hours > 72) return null;

  if (hours <= 24) {
    return (
      <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-[60px] bg-[#a58484]/20 text-[#e09090] text-xs font-medium">
        ⏳ Cierra en {Math.round(hours)}h
      </span>
    );
  }

  return (
    <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-[60px] bg-[#84a584]/15 text-[#84a584] text-xs font-medium">
      🔥 Oportunidad Caliente
    </span>
  );
}
