// apps/web/src/components/workflow/WorkflowProgress.tsx
import { cn } from "@/lib/utils"

interface WorkflowProgressProps {
  completedNodes: number   // count of active+partial among nodes 1–6
  totalNodes?: number      // defaults to 6
  blocked?: boolean        // true when Node 3 = pre-qualified and not eligible
}

export function WorkflowProgress({
  completedNodes,
  totalNodes = 6,
  blocked = false,
}: WorkflowProgressProps) {
  const pct = Math.round((completedNodes / totalNodes) * 100)

  return (
    <div className="rounded-[24px] bg-[#1a1f1a] px-6 py-4 mb-6">
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs font-medium text-[var(--color-text-muted)] uppercase tracking-wider">
          {blocked ? "Oportunidad descartada" : "Nodos con datos"}
        </span>
        <span className={cn(
          "text-sm font-semibold",
          blocked ? "text-[#a58484]" : "text-[#f9f5df]"
        )}>
          {blocked ? "⛔ Pre-calificado únicamente" : `${completedNodes} / ${totalNodes}`}
        </span>
      </div>
      <div className="h-2 rounded-full bg-[#2c3833] overflow-hidden">
        <div
          className={cn(
            "h-full rounded-full transition-all duration-500",
            blocked ? "bg-[#a58484]" : "bg-[#84a584]"
          )}
          style={{ width: `${blocked ? 100 : pct}%` }}
        />
      </div>
    </div>
  )
}
