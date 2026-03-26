// apps/web/src/components/workflow/WorkflowNode.tsx
import { Lock } from "lucide-react"
import { cn } from "@/lib/utils"
import type { WorkflowNodeStatus } from "@/lib/types"

const STATUS_CIRCLE: Record<WorkflowNodeStatus, string> = {
  active:    "bg-[#84a584]",
  partial:   "bg-[#b5a88a]",
  blocked:   "bg-[#a58484]",
  pendiente: "bg-[#3d4d45]",
}

interface WorkflowNodeProps {
  nodeNumber: number | string
  label: string
  status: WorkflowNodeStatus
  children?: React.ReactNode
  className?: string
}

export function WorkflowNode({ nodeNumber, label, status, children, className }: WorkflowNodeProps) {
  return (
    <div className={cn("relative rounded-[24px] bg-[#1a1f1a] p-6", className)}>
      {/* Status circle — top right */}
      <div
        className={cn(
          "absolute top-4 right-4 w-2.5 h-2.5 rounded-full",
          STATUS_CIRCLE[status]
        )}
        aria-label={status}
      />

      {/* Node header */}
      <div className="mb-3 pr-6">
        <span className="text-xs font-mono text-[var(--color-text-muted)] uppercase tracking-wider">
          Nodo {nodeNumber}
        </span>
        <h3 className="text-sm font-semibold text-[#f9f5df] mt-0.5 font-[family-name:var(--font-montserrat)]">
          {label}
        </h3>
      </div>

      {/* Content */}
      {status === "pendiente" ? (
        <div className="flex items-center gap-2 text-[var(--color-text-muted)]">
          <Lock size={14} className="shrink-0" />
          <p className="text-sm italic">{children ?? "Pendiente: dato no disponible"}</p>
        </div>
      ) : status === "blocked" ? (
        <div className="rounded-[16px] bg-[#a58484]/10 border border-[#a58484]/30 p-3">
          <p className="text-sm text-[#e09090]">{children}</p>
        </div>
      ) : (
        <div className="text-[#f2f5f9]">{children}</div>
      )}
    </div>
  )
}
