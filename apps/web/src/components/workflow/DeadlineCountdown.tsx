// apps/web/src/components/workflow/DeadlineCountdown.tsx
import { hoursUntil } from "@/lib/gamification"

interface DeadlineCountdownProps {
  biddocEndDt: string | null
  showRiskLabel?: boolean  // true for Node 10 (dossier risk), false for Node 5
}

export function DeadlineCountdown({ biddocEndDt, showRiskLabel = false }: DeadlineCountdownProps) {
  if (!biddocEndDt) {
    return <p className="text-sm text-[var(--color-text-muted)] italic">Sin fecha límite</p>
  }

  const hours = hoursUntil(biddocEndDt)
  const days = Math.ceil(hours / 24)

  if (hours <= 0) {
    return (
      <div>
        <p className="text-lg font-semibold text-[#a58484]">Vencida</p>
        <p className="text-xs text-[var(--color-text-muted)] mt-0.5">
          {new Date(biddocEndDt).toLocaleDateString("es-CR", { year: "numeric", month: "long", day: "numeric" })}
        </p>
      </div>
    )
  }

  const isRed    = days < 8
  const isAmber  = days >= 8 && days <= 22
  const isGreen  = days > 22

  const color = isRed ? "#a58484" : isAmber ? "#b5a88a" : "#84a584"

  const riskLabel = showRiskLabel
    ? isRed
      ? "crítico"
      : isAmber
      ? "riesgo dossier"
      : undefined
    : undefined

  return (
    <div>
      <p className="text-2xl font-semibold" style={{ color }}>
        {days} días
        {riskLabel && <span className="ml-2 text-sm font-normal">{isRed ? "🔴" : "⚠️"} {riskLabel}</span>}
      </p>
      <p className="text-xs text-[var(--color-text-muted)] mt-0.5">
        {new Date(biddocEndDt).toLocaleDateString("es-CR", { year: "numeric", month: "long", day: "numeric" })}
      </p>
    </div>
  )
}
