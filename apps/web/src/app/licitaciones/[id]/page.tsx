// apps/web/app/licitaciones/[id]/page.tsx
import { createClient } from "@/lib/supabase/server";
import { notFound } from "next/navigation";
import Link from "next/link";
import { Badge } from "@/components/ui/badge";
import { UrgencyBadge } from "@/components/ui/urgency-badge";
import { ActivityRecorder } from "./activity-recorder";
import {
  ArrowLeft, Calendar, DollarSign, Building2,
  FileText, AlertCircle,
} from "lucide-react";
import { TIPO_LABELS } from "@/lib/types";
import type { Licitacion, Categoria } from "@/lib/types";

interface PageProps {
  params: Promise<{ id: string }>;
}

const categoriaLabels: Record<Categoria, string> = {
  MEDICAMENTO: "Medicamento",
  EQUIPAMIENTO: "Equipamiento",
  INSUMO: "Insumo",
  SERVICIO: "Servicio",
};

function formatCurrency(amount: number | null, currency?: string | null): string {
  if (amount === null || amount === undefined) return "N/A";
  const symbol = currency === "USD" || currency === "$" ? "$" : "₡";
  return `${symbol}${amount.toLocaleString("es-CR")}`;
}

function formatDate(dateStr: string | null): string {
  if (!dateStr) return "N/A";
  return new Date(dateStr).toLocaleDateString("es-CR", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
}

async function getLicitacion(id: string): Promise<Licitacion | null> {
  const supabase = await createClient();
  const { data, error } = await supabase
    .from("licitaciones_medicas")
    .select("*")
    .eq("instcartelno", id)
    .single();
  if (error || !data) return null;
  return data as Licitacion;
}

export default async function LicitacionDetailPage({ params }: PageProps) {
  const { id } = await params;
  const licitacion = await getLicitacion(id);

  if (!licitacion) notFound();

  const isPublicado  = licitacion.estado === "Publicado";
  const isAdjudicado = licitacion.estado === "Adjudicado";

  const tipoLabel =
    TIPO_LABELS[licitacion.tipo_procedimiento ?? ""] ??
    licitacion.tipo_procedimiento ??
    "N/A";

  return (
    <div className="mx-auto max-w-[1393px] px-6 py-8">
      {/* Record activity for gamification */}
      <ActivityRecorder
        instcartelno={licitacion.instcartelno}
        instCode={licitacion.inst_code}
        biddocStartDt={licitacion.biddoc_start_dt}
      />
      {/* Back */}
      <Link
        href="/licitaciones"
        className="mb-6 inline-flex items-center gap-2 rounded-[60px] bg-[#2c3833] px-4 py-2 text-sm text-[var(--color-text-cream)] transition-colors hover:bg-[#3d4d45]"
      >
        <ArrowLeft size={18} />
        Volver a Licitaciones
      </Link>

      {/* Banner — solo para publicadas */}
      {isPublicado && (
        <div className="mb-6 flex items-start gap-3 rounded-[16px] border border-yellow-500/20 bg-yellow-500/5 px-4 py-3 text-sm text-yellow-200">
          <AlertCircle size={18} className="mt-0.5 shrink-0 text-yellow-400" />
          <span>
            Esta licitación está <strong>abierta para ofertas</strong>. El adjudicatario,
            monto contratado y términos de contrato se publicarán una vez sea adjudicada.
          </span>
        </div>
      )}

      {/* Header */}
      <div className="mb-8 overflow-hidden">
        <div className="flex flex-wrap items-center gap-3 mb-4">
          <span className="font-mono text-sm text-[#84a584]">
            {licitacion.instcartelno}
          </span>
          {licitacion.categoria && (
            <Badge variant="sage">{categoriaLabels[licitacion.categoria]}</Badge>
          )}
          <Badge variant="secondary">{licitacion.estado || "N/A"}</Badge>
          <UrgencyBadge biddocEndDt={licitacion.biddoc_end_dt} />
        </div>
        <h1 className="text-3xl font-semibold text-[#f9f5df] overflow-hidden text-ellipsis whitespace-nowrap font-[family-name:var(--font-montserrat)]">
          {licitacion.cartelnm || "Sin título"}
        </h1>
      </div>

      {/* Main Grid */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Left — Main Info */}
        <div className="lg:col-span-2 space-y-6">

          {/* Details Card */}
          <div className="rounded-[24px] bg-[#1a1f1a] p-6">
            <h2 className="mb-4 text-lg font-semibold text-[#f9f5df] font-[family-name:var(--font-montserrat)]">
              Detalles de la Licitación
            </h2>
            <div className="grid gap-4 sm:grid-cols-2">

              <div className="rounded-[16px] bg-[#2c3833] p-4">
                <p className="text-xs text-[var(--color-text-muted)] uppercase tracking-wider">Tipo de Proceso</p>
                <p className="mt-1 text-[#f2f5f9]">{tipoLabel}</p>
                {TIPO_LABELS[licitacion.tipo_procedimiento ?? ""] && licitacion.tipo_procedimiento && (
                  <p className="mt-0.5 font-mono text-xs text-[var(--color-text-muted)]">
                    {licitacion.tipo_procedimiento}
                  </p>
                )}
              </div>

              <div className="rounded-[16px] bg-[#2c3833] p-4">
                <p className="text-xs text-[var(--color-text-muted)] uppercase tracking-wider">UNSPSC</p>
                <p className="mt-1 text-[#f2f5f9]">{licitacion.unspsc_cd || "N/A"}</p>
              </div>

              <div className="rounded-[16px] bg-[#2c3833] p-4">
                <p className="text-xs text-[var(--color-text-muted)] uppercase tracking-wider">Modalidad</p>
                <p className="mt-1 text-[#f2f5f9]">{licitacion.modalidad || "N/A"}</p>
              </div>

              <div className="rounded-[16px] bg-[#2c3833] p-4">
                <p className="text-xs text-[var(--color-text-muted)] uppercase tracking-wider">Proveedor</p>
                <p className="mt-1 text-[#f2f5f9]">
                  {isAdjudicado
                    ? (licitacion.supplier_nm || "N/A")
                    : isPublicado
                    ? <span className="italic text-[var(--color-text-muted)]">Pendiente de adjudicación</span>
                    : (licitacion.supplier_nm || "N/A")
                  }
                </p>
              </div>

              {licitacion.excepcion_cd && (
                <div className="rounded-[16px] bg-[#2c3833] p-4">
                  <p className="text-xs text-[var(--color-text-muted)] uppercase tracking-wider">Excepción Legal</p>
                  <p className="mt-1 text-[#f2f5f9]">{licitacion.excepcion_cd}</p>
                </div>
              )}

              {licitacion.vigencia_contrato && (
                <div className="rounded-[16px] bg-[#2c3833] p-4">
                  <p className="text-xs text-[var(--color-text-muted)] uppercase tracking-wider">Vigencia</p>
                  <p className="mt-1 text-[#f2f5f9]">
                    {licitacion.vigencia_contrato} {licitacion.unidad_vigencia}
                  </p>
                </div>
              )}

              {licitacion.detalle && (
                <div className="rounded-[16px] bg-[#2c3833] p-4 sm:col-span-2">
                  <p className="text-xs text-[var(--color-text-muted)] uppercase tracking-wider">Detalle</p>
                  <p className="mt-1 text-[#f2f5f9] text-sm leading-relaxed">{licitacion.detalle}</p>
                </div>
              )}

              {licitacion.mod_reason && (
                <div className="rounded-[16px] bg-[#2c3833] p-4 sm:col-span-2">
                  <p className="text-xs text-[var(--color-text-muted)] uppercase tracking-wider">Motivo Modificación</p>
                  <p className="mt-1 text-[#f2f5f9] text-sm leading-relaxed">{licitacion.mod_reason}</p>
                </div>
              )}
            </div>
          </div>

          {/* Raw Data */}
          <div className="rounded-[24px] bg-[#1a1f1a] p-6">
            <h2 className="mb-4 text-lg font-semibold text-[#f9f5df] font-[family-name:var(--font-montserrat)]">
              Datos Raw
            </h2>
            <pre className="overflow-x-auto rounded-[16px] bg-[#2c3833] p-4 text-xs text-[#e4e4e4]">
              {JSON.stringify(licitacion.raw_data, null, 2)}
            </pre>
          </div>
        </div>

        {/* Right — Sidebar */}
        <div className="space-y-6">

          {/* Entity */}
          <div className="rounded-[24px] bg-[#84a584] p-6 text-[#1c1a1f]">
            <div className="flex items-center gap-3 mb-4">
              <Building2 size={24} />
              <h2 className="text-lg font-semibold font-[family-name:var(--font-montserrat)]">Entidad</h2>
            </div>
            <p className="text-xl font-medium">{licitacion.instnm || "N/A"}</p>
            {licitacion.inst_code && (
              <p className="mt-1 font-mono text-xs opacity-60">{licitacion.inst_code}</p>
            )}
          </div>

          {/* Amount */}
          {licitacion.monto_colones ? (
            <div className="rounded-[24px] bg-[#2c3833] p-6">
              <div className="flex items-center gap-3 mb-4">
                <DollarSign size={24} className="text-[#f9f5df]" />
                <h2 className="text-lg font-semibold text-[#f9f5df] font-[family-name:var(--font-montserrat)]">Monto</h2>
              </div>
              <p className="text-3xl font-semibold text-[#f9f5df]">
                {formatCurrency(licitacion.monto_colones, licitacion.currency_type)}
              </p>
            </div>
          ) : isPublicado ? (
            <div className="rounded-[24px] border border-dashed border-[#3d4d45] bg-[#1a1f1a] p-6">
              <div className="flex items-center gap-3 mb-2">
                <DollarSign size={24} className="text-[var(--color-text-muted)]" />
                <h2 className="text-lg font-semibold text-[#f9f5df] font-[family-name:var(--font-montserrat)]">Monto</h2>
              </div>
              <p className="text-sm italic text-[var(--color-text-muted)]">
                Disponible al adjudicarse
              </p>
            </div>
          ) : null}

          {/* Dates */}
          <div className="rounded-[24px] bg-[#1a1f1a] p-6">
            <div className="flex items-center gap-3 mb-4">
              <Calendar size={24} className="text-[#84a584]" />
              <h2 className="text-lg font-semibold text-[#f9f5df] font-[family-name:var(--font-montserrat)]">Fechas</h2>
            </div>
            <div className="space-y-3">
              <div>
                <p className="text-xs text-[var(--color-text-muted)]">Publicación</p>
                <p className="text-[#f2f5f9]">{formatDate(licitacion.biddoc_start_dt)}</p>
              </div>
              <div>
                <p className="text-xs text-[var(--color-text-muted)]">Apertura Ofertas</p>
                <p className="text-[#f2f5f9]">{formatDate(licitacion.openbid_dt)}</p>
              </div>
              {licitacion.biddoc_end_dt && (
                <div>
                  <p className="text-xs text-[var(--color-text-muted)]">Fin Documentos</p>
                  <p className="text-[#f2f5f9]">{formatDate(licitacion.biddoc_end_dt)}</p>
                </div>
              )}
              {licitacion.adj_firme_dt && (
                <div>
                  <p className="text-xs text-[var(--color-text-muted)]">Firmeza Adjudicación</p>
                  <p className="text-[#f2f5f9]">{formatDate(licitacion.adj_firme_dt)}</p>
                </div>
              )}
            </div>
          </div>

          {/* Classification */}
          <div className="rounded-[24px] bg-[#1a1f1a] p-6">
            <div className="flex items-center gap-3 mb-4">
              <FileText size={24} className="text-[#84a584]" />
              <h2 className="text-lg font-semibold text-[#f9f5df] font-[family-name:var(--font-montserrat)]">
                Clasificación
              </h2>
            </div>
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm text-[var(--color-text-muted)]">Es Médica</span>
                <Badge variant={licitacion.es_medica ? "sage" : "secondary"}>
                  {licitacion.es_medica ? "Sí" : "No"}
                </Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-[var(--color-text-muted)]">Categorizada</span>
                <Badge variant={licitacion.categoria ? "sage" : "secondary"}>
                  {licitacion.categoria ? "Sí" : "No"}
                </Badge>
              </div>
              {licitacion.cartel_cate && (
                <div className="flex items-center justify-between">
                  <span className="text-sm text-[var(--color-text-muted)]">Cat. Cartel</span>
                  <span className="text-xs text-[#e4e4e4]">{licitacion.cartel_cate}</span>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
