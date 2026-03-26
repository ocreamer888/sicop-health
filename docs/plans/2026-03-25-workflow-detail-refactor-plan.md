# Workflow Detail Page Refactor — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Rebuild the tender detail page around the 12-node decision-making workflow and add a filter bar to the list page.

**Architecture:** Four new reusable components under `src/components/workflow/` are built first, then the detail page is rebuilt to use them, then the list page gets a client-side filter bar. The `LicitacionesTable` component and all existing pages other than these two are untouched.

**Tech Stack:** Next.js 16 (App Router), TypeScript, Tailwind CSS, Lucide icons, Supabase (no new queries), `hoursUntil` from `@/lib/gamification`.

**Design reference:** `docs/plans/2026-03-25-workflow-detail-refactor-design.md`

---

## Palette & patterns (memorize these — do not invent new ones)

```
bg cards:       #1a1f1a  (outer)   #2c3833  (inner)
text primary:   #f9f5df
text secondary: #f2f5f9
text muted:     var(--color-text-muted)
green:          #84a584
amber:          #b5a88a
red:            #a58484
dim:            #3d4d45
border radius:  rounded-[24px] cards   rounded-[16px] inner   rounded-[60px] pills
```

---

## Task 1: Add WorkflowNodeStatus type to types.ts

**Files:**
- Modify: `apps/web/src/lib/types.ts`

**Step 1: Add the type after the existing `Estado` type**

Find the block ending at line ~16 (after `Estado` type) and add:

```typescript
export type WorkflowNodeStatus = "active" | "partial" | "pendiente" | "blocked"
```

**Step 2: Verify TypeScript compiles**

```bash
cd apps/web && npx tsc --noEmit
```
Expected: no errors.

**Step 3: Commit**

```bash
git add apps/web/src/lib/types.ts
git commit -m "feat(workflow): add WorkflowNodeStatus type"
```

---

## Task 2: Build DeadlineCountdown component

This is a pure display component — no client state needed. Used in WorkflowNode (nodes 5 and 10).

**Files:**
- Create: `apps/web/src/components/workflow/DeadlineCountdown.tsx`

**Step 1: Create the component**

```typescript
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
```

**Step 2: Verify build**

```bash
cd apps/web && npx tsc --noEmit
```
Expected: no errors.

**Step 3: Commit**

```bash
git add apps/web/src/components/workflow/DeadlineCountdown.tsx
git commit -m "feat(workflow): add DeadlineCountdown component"
```

---

## Task 3: Build WorkflowNode component

**Files:**
- Create: `apps/web/src/components/workflow/WorkflowNode.tsx`

**Step 1: Create the component**

```typescript
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
```

**Step 2: Verify build**

```bash
cd apps/web && npx tsc --noEmit
```
Expected: no errors.

**Step 3: Commit**

```bash
git add apps/web/src/components/workflow/WorkflowNode.tsx
git commit -m "feat(workflow): add WorkflowNode component"
```

---

## Task 4: Build WorkflowProgress component

**Files:**
- Create: `apps/web/src/components/workflow/WorkflowProgress.tsx`

**Step 1: Create the component**

```typescript
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
```

**Step 2: Verify build**

```bash
cd apps/web && npx tsc --noEmit
```
Expected: no errors.

**Step 3: Commit**

```bash
git add apps/web/src/components/workflow/WorkflowProgress.tsx
git commit -m "feat(workflow): add WorkflowProgress component"
```

---

## Task 5: Build WhatsAppButton component

**Files:**
- Create: `apps/web/src/components/workflow/WhatsAppButton.tsx`

**Step 1: Create the component**

```typescript
// apps/web/src/components/workflow/WhatsAppButton.tsx
import { MessageCircle } from "lucide-react"

interface WhatsAppButtonProps {
  instcartelno: string
  cartelnm: string | null
  instnm: string | null
  biddocEndDt: string | null
  montoColones: number | null
  currencyType: string | null
}

function formatDate(dateStr: string | null): string {
  if (!dateStr) return "N/A"
  return new Date(dateStr).toLocaleDateString("es-CR", {
    year: "numeric", month: "long", day: "numeric",
  })
}

export function WhatsAppButton({
  instcartelno,
  cartelnm,
  instnm,
  biddocEndDt,
  montoColones,
  currencyType,
}: WhatsAppButtonProps) {
  const lines = [
    `*Licitación SICOP*`,
    ``,
    `📋 *Descripción:* ${cartelnm ?? "N/A"}`,
    `🏛️ *Institución:* ${instnm ?? "N/A"}`,
    `🔑 *Código:* ${instcartelno}`,
    `📅 *Deadline:* ${formatDate(biddocEndDt)}`,
  ]

  if (montoColones) {
    const symbol = currencyType === "USD" ? "$" : "₡"
    lines.push(`💰 *Monto estimado:* ${symbol}${montoColones.toLocaleString("es-CR")}`)
  }

  lines.push(``, `¿Pueden cumplir con estas especificaciones?`)

  const text = encodeURIComponent(lines.join("\n"))
  const href = `https://wa.me/?text=${text}`

  return (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      className="inline-flex items-center gap-2 rounded-[60px] bg-[#84a584] px-5 py-2.5 text-sm font-semibold text-[#1c1a1f] transition-colors hover:bg-[#9ab89a]"
    >
      <MessageCircle size={16} />
      Contactar fabricante
    </a>
  )
}
```

**Step 2: Verify build**

```bash
cd apps/web && npx tsc --noEmit
```
Expected: no errors.

**Step 3: Commit**

```bash
git add apps/web/src/components/workflow/WhatsAppButton.tsx
git commit -m "feat(workflow): add WhatsAppButton component"
```

---

## Task 6: Rebuild the detail page

**Files:**
- Modify (full rewrite): `apps/web/src/app/licitaciones/[id]/page.tsx`
- Keep untouched: `apps/web/src/app/licitaciones/[id]/activity-recorder.tsx`
- Keep untouched: `apps/web/src/app/licitaciones/[id]/record-activity.ts`

**Step 1: Replace the full file content**

```typescript
// apps/web/src/app/licitaciones/[id]/page.tsx
import { createClient } from "@/lib/supabase/server"
import { notFound } from "next/navigation"
import Link from "next/link"
import { ArrowLeft } from "lucide-react"
import { Badge } from "@/components/ui/badge"
import { UrgencyBadge } from "@/components/ui/urgency-badge"
import { ActivityRecorder } from "./activity-recorder"
import { WorkflowNode } from "@/components/workflow/WorkflowNode"
import { WorkflowProgress } from "@/components/workflow/WorkflowProgress"
import { DeadlineCountdown } from "@/components/workflow/DeadlineCountdown"
import { WhatsAppButton } from "@/components/workflow/WhatsAppButton"
import { TIPO_LABELS } from "@/lib/types"
import type { Licitacion, Categoria } from "@/lib/types"

interface PageProps {
  params: Promise<{ id: string }>
}

const categoriaLabels: Record<Categoria, string> = {
  MEDICAMENTO: "Medicamento",
  EQUIPAMIENTO: "Equipamiento",
  INSUMO: "Insumo",
  SERVICIO: "Servicio",
}

function formatDate(dateStr: string | null): string {
  if (!dateStr) return "N/A"
  return new Date(dateStr).toLocaleDateString("es-CR", {
    year: "numeric", month: "long", day: "numeric",
  })
}

function formatCurrency(amount: number | null, currency?: string | null): string {
  if (amount === null || amount === undefined) return "N/A"
  const symbol = currency === "USD" || currency === "$" ? "$" : "₡"
  return `${symbol}${amount.toLocaleString("es-CR")}`
}

async function getLicitacion(id: string): Promise<Licitacion | null> {
  const supabase = await createClient()
  const { data, error } = await supabase
    .from("licitaciones_medicas")
    .select("*")
    .eq("instcartelno", id)
    .single()
  if (error || !data) return null
  return data as Licitacion
}

export default async function LicitacionDetailPage({ params }: PageProps) {
  const { id } = await params
  const l = await getLicitacion(id)
  if (!l) notFound()

  const isPublicado = l.estado === "Publicado"
  const tipoLabel = TIPO_LABELS[l.tipo_procedimiento ?? ""] ?? l.tipo_procedimiento ?? "N/A"

  // WorkflowProgress: count active/partial nodes among 1–6
  // Node 1 always active (instnm always present)
  // Node 2 always pendiente (gap)
  // Node 3 always pendiente (gap)
  // Node 4 always pendiente (depends on node 3)
  // Node 5 partial if biddoc_end_dt present
  // Node 6 always pendiente (gap)
  const completedNodes = 1 + (l.biddoc_end_dt ? 1 : 0) // nodes 1 and 5

  return (
    <div className="mx-auto max-w-[1393px] px-6 py-8">
      <ActivityRecorder
        instcartelno={l.instcartelno}
        instCode={l.inst_code}
        biddocStartDt={l.biddoc_start_dt}
      />

      {/* Back */}
      <Link
        href="/licitaciones"
        className="mb-6 inline-flex items-center gap-2 rounded-[60px] bg-[#2c3833] px-4 py-2 text-sm text-[var(--color-text-cream)] transition-colors hover:bg-[#3d4d45]"
      >
        <ArrowLeft size={18} />
        Volver a Licitaciones
      </Link>

      {/* Header */}
      <div className="mb-4">
        <div className="flex flex-wrap items-center gap-3 mb-3">
          <span className="font-mono text-sm text-[#84a584]">{l.instcartelno}</span>
          {l.categoria && (
            <Badge variant="sage">{categoriaLabels[l.categoria]}</Badge>
          )}
          <Badge variant="secondary">{l.estado || "N/A"}</Badge>
          <UrgencyBadge biddocEndDt={l.biddoc_end_dt} />
        </div>
        <h1 className="text-3xl font-semibold text-[#f9f5df] overflow-hidden text-ellipsis whitespace-nowrap font-[family-name:var(--font-montserrat)]">
          {l.cartelnm || "Sin título"}
        </h1>
      </div>

      {/* Progress bar */}
      <WorkflowProgress completedNodes={completedNodes} />

      {/* Main grid */}
      <div className="grid gap-6 lg:grid-cols-3">

        {/* LEFT — workflow nodes */}
        <div className="lg:col-span-2 space-y-4">

          {/* Node 1 — Institución + Fecha */}
          <WorkflowNode nodeNumber={1} label="Institución y Fecha de Publicación" status="active">
            <div className="grid gap-3 sm:grid-cols-2">
              <div className="rounded-[16px] bg-[#2c3833] p-4">
                <p className="text-xs text-[var(--color-text-muted)] uppercase tracking-wider mb-1">Institución</p>
                <p className="text-[#f2f5f9] font-medium">{l.instnm || "N/A"}</p>
                {l.inst_code && (
                  <p className="font-mono text-xs text-[var(--color-text-muted)] mt-0.5">{l.inst_code}</p>
                )}
              </div>
              <div className="rounded-[16px] bg-[#2c3833] p-4">
                <p className="text-xs text-[var(--color-text-muted)] uppercase tracking-wider mb-1">Publicación</p>
                <p className="text-[#f2f5f9]">{formatDate(l.biddoc_start_dt)}</p>
              </div>
              <div className="rounded-[16px] bg-[#2c3833] p-4">
                <p className="text-xs text-[var(--color-text-muted)] uppercase tracking-wider mb-1">Tipo de Proceso</p>
                <p className="text-[#f2f5f9]">{tipoLabel}</p>
                {l.tipo_procedimiento && (
                  <p className="font-mono text-xs text-[var(--color-text-muted)] mt-0.5">{l.tipo_procedimiento}</p>
                )}
              </div>
              <div className="rounded-[16px] bg-[#2c3833] p-4">
                <p className="text-xs text-[var(--color-text-muted)] uppercase tracking-wider mb-1">Modalidad</p>
                <p className="text-[#f2f5f9]">{l.modalidad || "N/A"}</p>
              </div>
            </div>
          </WorkflowNode>

          {/* Node 2 — Presupuesto estimado */}
          <WorkflowNode nodeNumber={2} label="Presupuesto Estimado" status="pendiente">
            Pendiente: dato no disponible en API REST — requiere módulo Datos Abiertos (JSP)
          </WorkflowNode>

          {/* Node 3 — Tipo de participación */}
          <WorkflowNode nodeNumber={3} label="Tipo de Participación" status="pendiente">
            Pendiente: requiere Datos Abiertos (RE_DatosAbiertosConcursosView.jsp)
          </WorkflowNode>

          {/* Node 4 — Elegibilidad */}
          <WorkflowNode nodeNumber={4} label="Elegibilidad del Proveedor" status="pendiente">
            Pendiente: depende del Nodo 3 — se habilitará cuando se conozca el tipo de participación
          </WorkflowNode>

          {/* Node 5 — Tiempo para fabricar */}
          <WorkflowNode
            nodeNumber={5}
            label="Tiempo para Fabricar"
            status={l.biddoc_end_dt ? "partial" : "pendiente"}
          >
            {l.biddoc_end_dt ? (
              <div className="grid gap-3 sm:grid-cols-2">
                <div className="rounded-[16px] bg-[#2c3833] p-4">
                  <p className="text-xs text-[var(--color-text-muted)] uppercase tracking-wider mb-2">
                    Días hasta deadline
                  </p>
                  <DeadlineCountdown biddocEndDt={l.biddoc_end_dt} showRiskLabel={false} />
                </div>
                <div className="rounded-[16px] bg-[#2c3833] p-4">
                  <p className="text-xs text-[var(--color-text-muted)] uppercase tracking-wider mb-1">
                    Apertura de Ofertas
                  </p>
                  <p className="text-[#f2f5f9]">{formatDate(l.openbid_dt)}</p>
                </div>
              </div>
            ) : (
              "Sin fecha límite de oferta disponible"
            )}
          </WorkflowNode>

          {/* Node 6 — Cantidades y precios */}
          <WorkflowNode nodeNumber={6} label="Cantidades y Precios por Línea" status="pendiente">
            Pendiente: requiere líneas de cartel (CE_MOD_DATOSABIERTOSVIEW.jsp, Reportes 1.1 / 2.1)
          </WorkflowNode>

          {/* Node 7 — Contactar fabricante */}
          <WorkflowNode nodeNumber={7} label="Contactar Fabricante" status="partial">
            <div className="space-y-3">
              <p className="text-sm text-[var(--color-text-muted)]">
                Envía la especificación disponible a un fabricante vía WhatsApp.
                {!l.monto_colones && (
                  <span className="block mt-1 text-xs italic">
                    ⚠️ Monto no disponible aún — se incluirá al adjudicarse.
                  </span>
                )}
              </p>
              <WhatsAppButton
                instcartelno={l.instcartelno}
                cartelnm={l.cartelnm}
                instnm={l.instnm}
                biddocEndDt={l.biddoc_end_dt}
                montoColones={l.monto_colones}
                currencyType={l.currency_type}
              />
            </div>
          </WorkflowNode>

          {/* Node 8-9 — Margen y Dossier */}
          <WorkflowNode nodeNumber="8–9" label="Margen de Negocio y Solicitud de Dossier" status="pendiente">
            Proceso externo — el fabricante provee dossier completo (bioequivalencia, estabilidad, certificaciones). Tiempo típico: 15–22 días.
          </WorkflowNode>

          {/* Node 10 — Riesgo dossier */}
          <WorkflowNode
            nodeNumber={10}
            label="Riesgo de Timeline del Dossier"
            status={l.biddoc_end_dt ? "partial" : "pendiente"}
          >
            {l.biddoc_end_dt ? (
              <div className="rounded-[16px] bg-[#2c3833] p-4">
                <p className="text-xs text-[var(--color-text-muted)] uppercase tracking-wider mb-2">
                  Tiempo vs. 15–22 días del dossier
                </p>
                <DeadlineCountdown biddocEndDt={l.biddoc_end_dt} showRiskLabel={true} />
              </div>
            ) : (
              "Sin fecha límite disponible para calcular riesgo"
            )}
          </WorkflowNode>

          {/* Node 11 — Registro */}
          <WorkflowNode nodeNumber={11} label="Presentación a Registro" status="pendiente">
            Proceso externo ante el Ministerio de Salud. Una vez recibido el dossier del fabricante.
          </WorkflowNode>

          {/* Node 12 — Historial de precios */}
          <WorkflowNode nodeNumber={12} label="Historial de Participación y Precios" status="pendiente">
            Pendiente: tabla precioshistoricos vacía — requiere importación de Datos Abiertos (Reportes 5, 6)
          </WorkflowNode>

          {/* Adjudication info — only when awarded */}
          {!isPublicado && l.supplier_nm && (
            <div className="rounded-[24px] bg-[#2c3833] p-6">
              <h2 className="mb-4 text-lg font-semibold text-[#f9f5df] font-[family-name:var(--font-montserrat)]">
                Adjudicación
              </h2>
              <div className="grid gap-3 sm:grid-cols-2">
                <div className="rounded-[16px] bg-[#1a1f1a] p-4">
                  <p className="text-xs text-[var(--color-text-muted)] uppercase tracking-wider mb-1">Proveedor</p>
                  <p className="text-[#f2f5f9]">{l.supplier_nm}</p>
                  {l.supplier_cd && (
                    <p className="font-mono text-xs text-[var(--color-text-muted)] mt-0.5">{l.supplier_cd}</p>
                  )}
                </div>
                <div className="rounded-[16px] bg-[#1a1f1a] p-4">
                  <p className="text-xs text-[var(--color-text-muted)] uppercase tracking-wider mb-1">Monto Adjudicado</p>
                  <p className="text-[#f2f5f9] text-xl font-semibold">
                    {formatCurrency(l.monto_colones, l.currency_type)}
                  </p>
                </div>
                {l.adj_firme_dt && (
                  <div className="rounded-[16px] bg-[#1a1f1a] p-4">
                    <p className="text-xs text-[var(--color-text-muted)] uppercase tracking-wider mb-1">Firmeza</p>
                    <p className="text-[#f2f5f9]">{formatDate(l.adj_firme_dt)}</p>
                  </div>
                )}
                {l.vigencia_contrato && (
                  <div className="rounded-[16px] bg-[#1a1f1a] p-4">
                    <p className="text-xs text-[var(--color-text-muted)] uppercase tracking-wider mb-1">Vigencia</p>
                    <p className="text-[#f2f5f9]">{l.vigencia_contrato} {l.unidad_vigencia}</p>
                  </div>
                )}
                {l.detalle && (
                  <div className="rounded-[16px] bg-[#1a1f1a] p-4 sm:col-span-2">
                    <p className="text-xs text-[var(--color-text-muted)] uppercase tracking-wider mb-1">Detalle</p>
                    <p className="text-[#f2f5f9] text-sm leading-relaxed">{l.detalle}</p>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        {/* RIGHT — sidebar */}
        <div className="space-y-6">

          {/* Institution card */}
          <div className="rounded-[24px] bg-[#84a584] p-6 text-[#1c1a1f]">
            <h2 className="text-lg font-semibold mb-2 font-[family-name:var(--font-montserrat)]">
              {l.instnm || "N/A"}
            </h2>
            {l.inst_code && (
              <p className="font-mono text-xs opacity-60">{l.inst_code}</p>
            )}
            {l.unspsc_cd && (
              <p className="mt-2 text-xs opacity-70">UNSPSC: {l.unspsc_cd}</p>
            )}
          </div>

          {/* Deadline countdown sidebar */}
          {l.biddoc_end_dt && (
            <div className="rounded-[24px] bg-[#1a1f1a] p-6">
              <h2 className="text-sm font-semibold text-[#f9f5df] mb-3 font-[family-name:var(--font-montserrat)] uppercase tracking-wider">
                Deadline
              </h2>
              <DeadlineCountdown biddocEndDt={l.biddoc_end_dt} showRiskLabel={true} />
            </div>
          )}

          {/* Publication banner for open tenders */}
          {isPublicado && (
            <div className="rounded-[24px] border border-yellow-500/20 bg-yellow-500/5 px-5 py-4 text-sm text-yellow-200">
              <p className="font-medium mb-1">Licitación abierta</p>
              <p className="text-xs opacity-80">
                Monto contratado y proveedor disponibles al adjudicarse.
              </p>
            </div>
          )}

          {/* Classification */}
          <div className="rounded-[24px] bg-[#1a1f1a] p-6">
            <h2 className="text-sm font-semibold text-[#f9f5df] mb-3 font-[family-name:var(--font-montserrat)] uppercase tracking-wider">
              Clasificación
            </h2>
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm text-[var(--color-text-muted)]">Categoría</span>
                {l.categoria ? (
                  <Badge variant="sage">{categoriaLabels[l.categoria]}</Badge>
                ) : (
                  <Badge variant="secondary">N/A</Badge>
                )}
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-[var(--color-text-muted)]">Estado</span>
                <Badge variant="secondary">{l.estado || "N/A"}</Badge>
              </div>
              {l.excepcion_cd && (
                <div className="flex items-center justify-between">
                  <span className="text-sm text-[var(--color-text-muted)]">Excepción</span>
                  <span className="text-xs text-[#e4e4e4] font-mono">{l.excepcion_cd}</span>
                </div>
              )}
            </div>
          </div>

          {/* Modification reason */}
          {l.mod_reason && (
            <div className="rounded-[24px] bg-[#1a1f1a] p-6">
              <h2 className="text-sm font-semibold text-[#f9f5df] mb-2 font-[family-name:var(--font-montserrat)] uppercase tracking-wider">
                Motivo Modificación
              </h2>
              <p className="text-sm text-[#f2f5f9] leading-relaxed">{l.mod_reason}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
```

**Step 2: Run type check**

```bash
cd apps/web && npx tsc --noEmit
```
Expected: no errors.

**Step 3: Start dev server and verify visually**

```bash
cd apps/web && npm run dev
```

Navigate to any licitacion detail page (e.g. `/licitaciones/2026LD-000001-0031700001`) and verify:
- Progress bar shows at top
- 12 workflow node cards render in order
- Nodes 1 and 5 (if deadline exists) show data
- All other nodes show lock icon + grey circle
- Sidebar shows institution card (green), deadline countdown, classification
- WhatsApp button opens wa.me link in new tab

**Step 4: Commit**

```bash
git add apps/web/src/app/licitaciones/\[id\]/page.tsx
git commit -m "feat(workflow): rebuild licitacion detail page around 12-node workflow"
```

---

## Task 7: Add filter bar to list page

The `LicitacionesTable` component already handles its own internal search via `@tanstack/react-table`. The filter bar adds **server-fetched data pre-filtering** using component state — no new DB queries.

**Files:**
- Modify: `apps/web/src/app/licitaciones/page.tsx`

**Step 1: Convert page to use a client wrapper for filters**

Create the filter wrapper first:

Create `apps/web/src/app/licitaciones/licitaciones-filter.tsx`:

```typescript
// apps/web/src/app/licitaciones/licitaciones-filter.tsx
"use client"

import { useState, useMemo } from "react"
import { LicitacionesTable } from "@/components/licitaciones-table"
import { X } from "lucide-react"
import type { LicitacionPreview, Categoria } from "@/lib/types"

const CATEGORIAS: Categoria[] = ["MEDICAMENTO", "EQUIPAMIENTO", "INSUMO", "SERVICIO"]
const CATEGORIA_LABELS: Record<Categoria, string> = {
  MEDICAMENTO: "Medicamento",
  EQUIPAMIENTO: "Equipamiento",
  INSUMO: "Insumo",
  SERVICIO: "Servicio",
}

interface LicitacionesFilterProps {
  data: LicitacionPreview[]
}

export function LicitacionesFilter({ data }: LicitacionesFilterProps) {
  const [instFilter, setInstFilter] = useState("")
  const [fechaDesde, setFechaDesde] = useState("")
  const [fechaHasta, setFechaHasta] = useState("")
  const [catFilter, setCatFilter] = useState("")

  const instituciones = useMemo(() => {
    const set = new Set(data.map(l => l.instnm).filter(Boolean) as string[])
    return Array.from(set).sort()
  }, [data])

  const filtered = useMemo(() => {
    return data.filter(l => {
      if (instFilter && l.instnm !== instFilter) return false
      if (catFilter && l.categoria !== catFilter) return false
      if (fechaDesde && l.biddoc_start_dt && l.biddoc_start_dt < fechaDesde) return false
      if (fechaHasta && l.biddoc_start_dt && l.biddoc_start_dt > fechaHasta + "T23:59:59") return false
      return true
    })
  }, [data, instFilter, catFilter, fechaDesde, fechaHasta])

  const hasFilters = instFilter || catFilter || fechaDesde || fechaHasta

  function clear() {
    setInstFilter("")
    setCatFilter("")
    setFechaDesde("")
    setFechaHasta("")
  }

  return (
    <>
      {/* Filter bar */}
      <div className="mb-6 flex flex-wrap items-center gap-3">
        <select
          value={instFilter}
          onChange={e => setInstFilter(e.target.value)}
          className="rounded-[60px] bg-[#2c3833] px-4 py-2 text-sm text-[#f2f5f9] border-none outline-none focus:ring-1 focus:ring-[#84a584] cursor-pointer"
        >
          <option value="">Todas las instituciones</option>
          {instituciones.map(inst => (
            <option key={inst} value={inst}>{inst}</option>
          ))}
        </select>

        <select
          value={catFilter}
          onChange={e => setCatFilter(e.target.value)}
          className="rounded-[60px] bg-[#2c3833] px-4 py-2 text-sm text-[#f2f5f9] border-none outline-none focus:ring-1 focus:ring-[#84a584] cursor-pointer"
        >
          <option value="">Todas las categorías</option>
          {CATEGORIAS.map(cat => (
            <option key={cat} value={cat}>{CATEGORIA_LABELS[cat]}</option>
          ))}
        </select>

        <input
          type="date"
          value={fechaDesde}
          onChange={e => setFechaDesde(e.target.value)}
          placeholder="Desde"
          className="rounded-[60px] bg-[#2c3833] px-4 py-2 text-sm text-[#f2f5f9] border-none outline-none focus:ring-1 focus:ring-[#84a584]"
        />

        <input
          type="date"
          value={fechaHasta}
          onChange={e => setFechaHasta(e.target.value)}
          placeholder="Hasta"
          className="rounded-[60px] bg-[#2c3833] px-4 py-2 text-sm text-[#f2f5f9] border-none outline-none focus:ring-1 focus:ring-[#84a584]"
        />

        {hasFilters && (
          <button
            onClick={clear}
            className="inline-flex items-center gap-1.5 rounded-[60px] bg-[#3d4d45] px-4 py-2 text-sm text-[var(--color-text-muted)] hover:text-[#f2f5f9] transition-colors"
          >
            <X size={14} />
            Limpiar
          </button>
        )}

        {hasFilters && (
          <span className="text-xs text-[var(--color-text-muted)]">
            {filtered.length} de {data.length}
          </span>
        )}
      </div>

      {/* Table — visually unchanged */}
      <div className="rounded-[32px] bg-[#1a1f1a] p-6">
        <LicitacionesTable data={filtered} />
      </div>
    </>
  )
}
```

**Step 2: Update the list page to use the filter wrapper**

Replace the bottom of `apps/web/src/app/licitaciones/page.tsx` — only the `return` block changes. The `getLicitaciones` function stays identical.

Replace the return statement:

```typescript
// Replace this block in apps/web/src/app/licitaciones/page.tsx
// (everything inside export default async function LicitacionesPage)

import { LicitacionesFilter } from "./licitaciones-filter"

// ... getLicitaciones() stays exactly the same ...

export default async function LicitacionesPage() {
  let licitaciones: LicitacionPreview[] = []
  let error: Error | null = null

  try {
    licitaciones = await getLicitaciones()
  } catch (e) {
    error = e instanceof Error ? e : new Error(String(e))
    console.error("Licitaciones fetch failed:", error)
  }

  if (error) {
    return (
      <div className="mx-auto max-w-[1393px] px-6 py-8">
        <div className="rounded-[24px] bg-[#a58484]/10 border border-[#a58484]/30 p-8">
          <h1 className="text-2xl font-semibold text-[#a58484] mb-4">Error cargando licitaciones</h1>
          <p className="text-[#f2f5f9] font-mono text-sm">{error.message}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-[1393px] px-6 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-semibold text-[#f9f5df] font-[family-name:var(--font-montserrat)]">
          Licitaciones
        </h1>
        <p className="mt-2 text-lg text-[var(--color-text-muted)] font-[family-name:var(--font-plus-jakarta)]">
          Explora todas las licitaciones de salud
        </p>
      </div>

      {/* Stats Summary */}
      <div className="mb-8 grid gap-4 sm:grid-cols-3">
        <div className="rounded-[24px] bg-[#1a1f1a] p-6">
          <p className="text-sm text-[var(--color-text-muted)]">Total</p>
          <p className="mt-2 text-3xl font-semibold text-[#f9f5df]">
            {licitaciones.length.toLocaleString()}
          </p>
        </div>
        <div className="rounded-[24px] bg-[#1a1f1a] p-6">
          <p className="text-sm text-[var(--color-text-muted)]">Con Categoría</p>
          <p className="mt-2 text-3xl font-semibold text-[#f9f5df]">
            {licitaciones.filter((l) => l.categoria).length.toLocaleString()}
          </p>
        </div>
        <div className="rounded-[24px] bg-[#1a1f1a] p-6">
          <p className="text-sm text-[var(--color-text-muted)]">Con Monto</p>
          <p className="mt-2 text-3xl font-semibold text-[#f9f5df]">
            {licitaciones.filter((l) => l.monto_colones).length.toLocaleString()}
          </p>
        </div>
      </div>

      {/* Filter bar + Table */}
      <LicitacionesFilter data={licitaciones} />
    </div>
  )
}
```

**Step 3: Run type check**

```bash
cd apps/web && npx tsc --noEmit
```
Expected: no errors.

**Step 4: Verify visually**

Navigate to `/licitaciones` and verify:
- Filter dropdowns appear above the table
- Institution dropdown is populated with real institution names
- Filtering by institution updates the table immediately
- Clearing filters restores all rows
- Table visual style is pixel-identical to before

**Step 5: Commit**

```bash
git add apps/web/src/app/licitaciones/licitaciones-filter.tsx apps/web/src/app/licitaciones/page.tsx
git commit -m "feat(workflow): add institution/category/date filter bar to licitaciones list"
```

---

## Final verification

```bash
cd apps/web && npm run build
```
Expected: build completes with no errors or type errors. Warnings about `any` types in existing code are acceptable — do not fix unless they are in files you modified.
