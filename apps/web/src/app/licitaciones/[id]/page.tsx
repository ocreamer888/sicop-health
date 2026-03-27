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

interface DaOferta {
  suppliernm: string | null
  suppliercd: string | null
  elegible: boolean | null
  orden_merito: number | null
  fecha_apertura: string | null
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

async function getOfertas(instcartelno: string): Promise<DaOferta[]> {
  const supabase = await createClient()
  const { data } = await supabase
    .from("da_ofertas")
    .select("suppliernm, suppliercd, elegible, orden_merito, fecha_apertura")
    .eq("instcartelno", instcartelno)
    .order("orden_merito", { ascending: true, nullsFirst: false })
  return (data ?? []) as DaOferta[]
}

export default async function LicitacionDetailPage({ params }: PageProps) {
  const { id } = await params
  const [l, ofertas] = await Promise.all([getLicitacion(id), getOfertas(id)])
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
  // Nodes 1–6 with data: 1 always, 2 if budget, 3 if modalidad known, 5 if deadline
  const completedNodes = 1
    + (l.presupuesto_estimado ? 1 : 0)
    + (l.modalidad_participacion ? 1 : 0)
    + (l.biddoc_end_dt ? 1 : 0)

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
          <WorkflowNode
            nodeNumber={2}
            label="Presupuesto Estimado"
            status={l.presupuesto_estimado ? "active" : "pendiente"}
          >
            {l.presupuesto_estimado ? (
              <div className="rounded-[16px] bg-[#2c3833] p-4">
                <p className="text-xs text-[var(--color-text-muted)] uppercase tracking-wider mb-1">
                  Presupuesto estimado
                </p>
                <p className="text-2xl font-semibold text-[#f9f5df]">
                  {formatCurrency(l.presupuesto_estimado, l.moneda_presupuesto)}
                </p>
                <p className="text-xs text-[var(--color-text-muted)] mt-1">
                  Solicitud de contratación (Datos Abiertos)
                </p>
              </div>
            ) : (
              "Pendiente: sin datos de presupuesto disponibles aún"
            )}
          </WorkflowNode>

          {/* Node 3 — Tipo de participación */}
          {(() => {
            const m = l.modalidad_participacion
            const status = m === "Precalificación" ? "blocked"
                         : m ? "active"
                         : "pendiente"
            return (
              <WorkflowNode nodeNumber={3} label="Tipo de Participación" status={status}>
                {m === "Precalificación" ? (
                  "Pre-calificación requerida — participación restringida a proveedores registrados"
                ) : m ? (
                  <div className="rounded-[16px] bg-[#2c3833] p-4">
                    <p className="text-xs text-[var(--color-text-muted)] uppercase tracking-wider mb-1">
                      Modalidad
                    </p>
                    <p className="text-[#f2f5f9] font-medium">{m}</p>
                    <p className="text-xs text-[var(--color-text-muted)] mt-1">
                      Participación abierta
                    </p>
                  </div>
                ) : (
                  "Pendiente: modalidad no disponible en Datos Abiertos aún"
                )}
              </WorkflowNode>
            )
          })()}

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
                presupuestoEstimado={l.presupuesto_estimado}
                monedaPresupuesto={l.moneda_presupuesto}
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

          {/* Node 12 — Participación y Adjudicación */}
          {(() => {
            const node12Status = l.desierto
              ? "blocked"
              : l.fecha_adj_firme || ofertas.length > 0
                ? "active"
                : "pendiente"
            return (
              <WorkflowNode nodeNumber={12} label="Historial de Participación y Precios" status={node12Status}>
                {l.desierto ? (
                  <div className="rounded-[16px] border border-yellow-500/30 bg-yellow-500/10 px-4 py-3">
                    <p className="text-sm font-semibold text-yellow-300">⚠️ Licitación declarada desierta</p>
                    <p className="text-xs text-yellow-200/70 mt-0.5">
                      No se adjudicó ningún proveedor — proceso sin efecto.
                    </p>
                  </div>
                ) : node12Status === "pendiente" ? (
                  <p className="text-sm text-[var(--color-text-muted)]">
                    Sin datos de participación disponibles
                  </p>
                ) : (
                  <div className="space-y-3">
                    {l.fecha_adj_firme && (
                      <div className="rounded-[16px] bg-[#2c3833] px-4 py-3 flex items-center gap-3">
                        <span className="text-xs text-[var(--color-text-muted)] uppercase tracking-wider shrink-0">Adj. firme</span>
                        <span className="text-[#f2f5f9] font-medium">{formatDate(l.fecha_adj_firme)}</span>
                      </div>
                    )}
                    {ofertas.length > 0 && (
                      <div className="overflow-hidden rounded-[16px] border border-[#3d4d45]">
                        {/* Table header */}
                        <div className="grid grid-cols-[1fr_auto_auto_auto_auto] gap-x-4 bg-[#1a1f1a] px-4 py-2">
                          <span className="text-xs text-[var(--color-text-muted)] uppercase tracking-wider">Proveedor</span>
                          <span className="text-xs text-[var(--color-text-muted)] uppercase tracking-wider text-right">Cédula</span>
                          <span className="text-xs text-[var(--color-text-muted)] uppercase tracking-wider text-center">Elegible</span>
                          <span className="text-xs text-[var(--color-text-muted)] uppercase tracking-wider text-center">Mérito</span>
                          <span className="text-xs text-[var(--color-text-muted)] uppercase tracking-wider text-right">Apertura</span>
                        </div>
                        {/* Table rows */}
                        {ofertas.map((o, i) => (
                          <div
                            key={i}
                            className="grid grid-cols-[1fr_auto_auto_auto_auto] gap-x-4 bg-[#2c3833] px-4 py-3 border-t border-[#3d4d45] items-center"
                          >
                            <div className="min-w-0">
                              <p className="text-sm text-[#f2f5f9] truncate">{o.suppliernm ?? "–"}</p>
                            </div>
                            <p className="font-mono text-xs text-[var(--color-text-muted)] text-right whitespace-nowrap">
                              {o.suppliercd ?? "–"}
                            </p>
                            <div className="flex justify-center">
                              {o.elegible === true ? (
                                <span className="rounded-full bg-[#84a584]/20 px-2 py-0.5 text-xs font-medium text-[#84a584]">Sí</span>
                              ) : o.elegible === false ? (
                                <span className="rounded-full bg-amber-500/10 px-2 py-0.5 text-xs font-medium text-amber-400/80">No</span>
                              ) : (
                                <span className="text-xs text-[var(--color-text-muted)]">–</span>
                              )}
                            </div>
                            <p className="text-sm text-[#f2f5f9] text-center">
                              {o.orden_merito ?? "–"}
                            </p>
                            <p className="text-xs text-[var(--color-text-muted)] text-right whitespace-nowrap">
                              {o.fecha_apertura ? formatDate(o.fecha_apertura) : "–"}
                            </p>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </WorkflowNode>
            )
          })()}

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
