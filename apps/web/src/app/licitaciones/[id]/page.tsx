import { createClient } from "@/lib/supabase/server";
import { notFound } from "next/navigation";
import Link from "next/link";
import { Badge } from "@/components/ui/badge";
import { ArrowLeft, Calendar, DollarSign, Building2, FileText, ExternalLink } from "lucide-react";
import type { Licitacion, Categoria, TypeKey } from "@/lib/types";

interface PageProps {
  params: Promise<{ id: string }>;
}

const categoriaLabels: Record<Categoria, string> = {
  MEDICAMENTO: "Medicamento",
  EQUIPAMIENTO: "Equipamiento",
  INSUMO: "Insumo",
  SERVICIO: "Servicio",
};

function formatCurrency(amount: number | null): string {
  if (amount === null || amount === undefined) return "N/A";
  return `₡${amount.toLocaleString()}`;
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
    .from("licitaciones_activas")
    .select("*")
    .eq("id", id)
    .single();

  if (error || !data) {
    return null;
  }

  return data as Licitacion;
}

export default async function LicitacionDetailPage({ params }: PageProps) {
  const { id } = await params;
  const licitacion = await getLicitacion(id);

  if (!licitacion) {
    notFound();
  }

  return (
    <div className="mx-auto max-w-[1393px] px-6 py-8">
      {/* Back Button */}
      <Link
        href="/licitaciones"
        className="mb-6 inline-flex items-center gap-2 rounded-[60px] bg-[#2c3833] px-4 py-2 text-sm text-[var(--color-text-cream)] transition-colors hover:bg-[#3d4d45]"
      >
        <ArrowLeft size={18} />
        Volver a Licitaciones
      </Link>

      {/* Header */}
      <div className="mb-8">
        <div className="flex flex-wrap items-center gap-3 mb-4">
          <span className="font-mono text-sm text-[#84a584]">
            {licitacion.numero_procedimiento}
          </span>
          {licitacion.categoria && (
            <Badge variant="sage">
              {categoriaLabels[licitacion.categoria]}
            </Badge>
          )}
          <Badge variant="secondary">
            {licitacion.estado || "N/A"}
          </Badge>
        </div>
        <h1 className="text-3xl font-semibold text-[#f9f5df] font-[family-name:var(--font-montserrat)]">
          {licitacion.descripcion || "Sin título"}
        </h1>
      </div>

      {/* Main Content Grid */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Left Column - Main Info */}
        <div className="lg:col-span-2 space-y-6">
          {/* Details Card */}
          <div className="rounded-[24px] bg-[#1a1f1a] p-6">
            <h2 className="mb-4 text-lg font-semibold text-[#f9f5df] font-[family-name:var(--font-montserrat)]">
              Detalles de la Licitación
            </h2>
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="rounded-[16px] bg-[#2c3833] p-4">
                <p className="text-xs text-[var(--color-text-muted)] uppercase tracking-wider">Tipo de Proceso</p>
                <p className="mt-1 text-[#f2f5f9]">{licitacion.tipo_procedimiento || "N/A"}</p>
              </div>
              <div className="rounded-[16px] bg-[#2c3833] p-4">
                <p className="text-xs text-[var(--color-text-muted)] uppercase tracking-wider">UNSPSC</p>
                <p className="mt-1 text-[#f2f5f9]">{licitacion.unspsc_cd || licitacion.clasificacion_unspsc || "N/A"}</p>
              </div>
              <div className="rounded-[16px] bg-[#2c3833] p-4">
                <p className="text-xs text-[var(--color-text-muted)] uppercase tracking-wider">Modalidad</p>
                <p className="mt-1 text-[#f2f5f9]">{licitacion.modalidad || "N/A"}</p>
              </div>
              <div className="rounded-[16px] bg-[#2c3833] p-4">
                <p className="text-xs text-[var(--color-text-muted)] uppercase tracking-wider">Adjudicatario</p>
                <p className="mt-1 text-[#f2f5f9]">{licitacion.adjudicatario || "N/A"}</p>
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
                  <p className="mt-1 text-[#f2f5f9]">{licitacion.vigencia_contrato} {licitacion.unidad_vigencia}</p>
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

        {/* Right Column - Sidebar */}
        <div className="space-y-6">
          {/* Entity Info */}
          <div className="rounded-[24px] bg-[#84a584] p-6 text-[#1c1a1f]">
            <div className="flex items-center gap-3 mb-4">
              <Building2 size={24} />
              <h2 className="text-lg font-semibold font-[family-name:var(--font-montserrat)]">
                Entidad
              </h2>
            </div>
            <p className="text-xl font-medium">
              {licitacion.institucion || "N/A"}
            </p>
          </div>

          {/* Amount Card */}
          {licitacion.monto_colones && (
            <div className="rounded-[24px] bg-[#2c3833] p-6">
              <div className="flex items-center gap-3 mb-4">
                <DollarSign size={24} className="text-[#f9f5df]" />
                <h2 className="text-lg font-semibold text-[#f9f5df] font-[family-name:var(--font-montserrat)]">
                  Monto
                </h2>
              </div>
              <p className="text-3xl font-semibold text-[#f9f5df]">
                {formatCurrency(licitacion.monto_colones)}
              </p>
            </div>
          )}

          {/* Dates Card */}
          <div className="rounded-[24px] bg-[#1a1f1a] p-6">
            <div className="flex items-center gap-3 mb-4">
              <Calendar size={24} className="text-[#84a584]" />
              <h2 className="text-lg font-semibold text-[#f9f5df] font-[family-name:var(--font-montserrat)]">
                Fechas
              </h2>
            </div>
            <div className="space-y-3">
              <div>
                <p className="text-xs text-[var(--color-text-muted)]">Fecha Trámite</p>
                <p className="text-[#f2f5f9]">{formatDate(licitacion.fecha_tramite)}</p>
              </div>
              <div>
                <p className="text-xs text-[var(--color-text-muted)]">Límite Ofertas</p>
                <p className="text-[#f2f5f9]">{formatDate(licitacion.fecha_limite_oferta)}</p>
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

          {/* Classification Card */}
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
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
