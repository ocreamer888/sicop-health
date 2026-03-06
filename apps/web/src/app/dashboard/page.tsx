import { createClient } from "@/lib/supabase/server";
import { StatCard } from "@/components/ui/stat-card";
import { LicitacionesTable } from "@/components/licitaciones-table";
import { Badge } from "@/components/ui/badge";
import {
  FileText,
  DollarSign,
  TrendingUp,
  Database,
  Pill,
  Stethoscope,
  Microscope,
  Briefcase,
} from "lucide-react";
import Link from "next/link";
import type { LicitacionPreview, Categoria } from "@/lib/types";

const categoriaIcons: Record<Categoria, React.ReactNode> = {
  MEDICAMENTO: <Pill size={24} />,
  EQUIPAMIENTO: <Stethoscope size={24} />,
  INSUMO: <Microscope size={24} />,
  SERVICIO: <Briefcase size={24} />,
};

const categoriaLabels: Record<Categoria, string> = {
  MEDICAMENTO: "Medicamentos",
  EQUIPAMIENTO: "Equipamiento",
  INSUMO: "Insumos",
  SERVICIO: "Servicios",
};

const estadoColors: Record<string, { label: string; color: string }> = {
  Publicado:  { label: "Publicado",  color: "bg-[#84a584]" },
  Adjudicado: { label: "Adjudicado", color: "bg-[#898a7d]" },
  Desierto:   { label: "Desierto",   color: "bg-[#5d6a85]" },
  Cancelado:  { label: "Cancelado",  color: "bg-[#a58484]" },
};

async function getDashboardData() {
  const supabase = await createClient();

  // Total médicas clasificadas (es_medica=true AND categoria NOT NULL)
  // Fix: excluye las 44 médicas sin categoría para consistencia con las cards
  const { count: totalCount } = await supabase
    .from("licitaciones_medicas")
    .select("*", { count: "exact", head: true })
    .eq("es_medica", true)
    .not("categoria", "is", null);

  // Recientes — médicas clasificadas, orden descendente
  const { data: recentLicitaciones } = await supabase
    .from("licitaciones_medicas")
    .select(
      "id, numero_procedimiento, descripcion, institucion, categoria, monto_colones, fecha_tramite, estado, es_medica, raw_data"
    )
    .eq("es_medica", true)
    .not("categoria", "is", null)
    .order("created_at", { ascending: false })
    .limit(5);

  // resumen_por_categoria — vista ya filtrada por es_medica=true AND categoria IS NOT NULL
  // (después de aplicar Fix 3 en SQL — CREATE OR REPLACE VIEW)
  // Si la vista todavía incluye categoria=null, el .filter() en byCategoria lo descarta
  const { data: resumenCategoria } = await supabase
    .from("resumen_por_categoria")
    .select("categoria, total, publicadas, adjudicadas, monto_crc, monto_usd");

  // currency_type desde columna DB — no desde raw_data (Gap 3)
  const { data: adjudicadasData } = await supabase
    .from("licitaciones_medicas")
    .select("monto_colones, currency_type")
    .eq("es_medica", true)
    .eq("estado", "Adjudicado")
    .not("monto_colones", "is", null);

  const montoCRC = (adjudicadasData ?? [])
    .filter(r => r.currency_type === "CRC" || r.currency_type === "₡" || !r.currency_type)
    .reduce((sum, r) => sum + (r.monto_colones ?? 0), 0);

  const montoUSD = (adjudicadasData ?? [])
    .filter(r => r.currency_type === "USD" || r.currency_type === "$")
    .reduce((sum, r) => sum + (r.monto_colones ?? 0), 0);

  // Excluir fila categoria=null de la vista (mientras no se aplique Fix 3 SQL)
  const byCategoria = (resumenCategoria ?? [])
    .filter(r => r.categoria !== null)
    .map(r => ({
      categoria:   r.categoria! as Categoria,
      total:       r.total       ?? 0,
      publicadas:  r.publicadas  ?? 0,
      adjudicadas: r.adjudicadas ?? 0,
      monto_crc:   Number(r.monto_crc  ?? 0),
      monto_usd:   Number(r.monto_usd  ?? 0),
    }));

  // byEstado solo desde rows con categoria — excluye la fila null de la vista
  const byEstado = byCategoria.reduce(
    (acc, r) => {
      acc["Publicado"]  = (acc["Publicado"]  ?? 0) + r.publicadas;
      acc["Adjudicado"] = (acc["Adjudicado"] ?? 0) + r.adjudicadas;
      return acc;
    },
    {} as Record<string, number>
  );

  // Totales de monto desde la vista (más eficiente que el query separado)
  const montoCRCVista = byCategoria.reduce((sum, r) => sum + r.monto_crc, 0);
  const montoUSDVista = byCategoria.reduce((sum, r) => sum + r.monto_usd, 0);

  return {
    totalLicitaciones:  totalCount ?? 0,
    recentLicitaciones: (recentLicitaciones ?? []) as LicitacionPreview[],
    porCategoria:       byCategoria,
    porEstado:          Object.entries(byEstado).map(([estado, count]) => ({ estado, count })),
    // Preferir datos de la vista (agrupados) sobre el query separado de adjudicadas
    montoCRC: montoCRCVista || montoCRC,
    montoUSD: montoUSDVista || montoUSD,
  };
}

export default async function DashboardPage() {
  const data = await getDashboardData();

  return (
    <div className="mx-auto max-w-[1393px] px-6 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-semibold text-[#f9f5df] font-[family-name:var(--font-montserrat)]">
          Dashboard
        </h1>
        <p className="mt-2 text-lg text-[var(--color-text-muted)] font-[family-name:var(--font-plus-jakarta)]">
          Resumen de licitaciones de salud
        </p>
      </div>

      {/* Stats Grid */}
      <div className="mb-8 grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Total Licitaciones"
          value={data.totalLicitaciones.toLocaleString()}
          description="Médicas clasificadas"
          icon={<FileText size={24} />}
        />
        <StatCard
          title="Monto Adjudicado"
          value={`₡${(data.montoCRC / 1_000_000).toFixed(1)}M`}
          description={
            data.montoUSD > 0
              ? `+ $${(data.montoUSD / 1_000).toFixed(0)}K USD`
              : "Solo licitaciones adjudicadas"
          }
          icon={<DollarSign size={24} />}
          variant="sage"
        />
        <StatCard
          title="Nuevas esta semana"
          value="+12"
          trend={{ value: 8, isPositive: true }}
          icon={<TrendingUp size={24} />}
        />
        <StatCard
          title="Estados"
          value={data.porEstado.length.toString()}
          description="Publicado, Adjudicado, Desierto, Cancelado"
          icon={<Database size={24} />}
        />
      </div>

      {/* Categorías */}
      <div className="mb-8">
        <h2 className="mb-4 text-xl font-semibold text-[#f9f5df] font-[family-name:var(--font-montserrat)]">
          Por Categoría
        </h2>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {data.porCategoria.map((item) => (
            <div
              key={item.categoria}
              className="flex items-center gap-4 rounded-[24px] bg-[#2c3833] p-4"
            >
              <div className="flex h-12 w-12 items-center justify-center rounded-[16px] bg-[#1a1f1a] text-[#f9f5df]">
                {categoriaIcons[item.categoria]}
              </div>
              <div>
                <p className="text-sm text-[#e4e4e4]">{categoriaLabels[item.categoria]}</p>
                <p className="text-2xl font-semibold text-[#f9f5df]">{item.total}</p>
                <p className="text-xs text-[var(--color-text-muted)] mt-0.5">
                  {item.publicadas} pub · {item.adjudicadas} adj
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Por Estado */}
      <div className="mb-8">
        <h2 className="mb-4 text-xl font-semibold text-[#f9f5df] font-[family-name:var(--font-montserrat)]">
          Por Estado
        </h2>
        <div className="flex flex-wrap gap-3">
          {data.porEstado.map((item) => {
            const config = estadoColors[item.estado] ?? { label: item.estado, color: "bg-[#666]" };
            return (
              <div
                key={item.estado}
                className="flex items-center gap-3 rounded-[24px] bg-[#1a1f1a] px-4 py-3"
              >
                <div className={`h-3 w-3 rounded-full ${config.color}`} />
                <span className="text-sm text-[#e4e4e4]">{config.label}</span>
                <Badge variant="secondary">{item.count}</Badge>
              </div>
            );
          })}
        </div>
      </div>

      {/* Recent Licitaciones */}
      <div className="mb-8">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-xl font-semibold text-[#f9f5df] font-[family-name:var(--font-montserrat)]">
            Licitaciones Recientes
          </h2>
          <Link
            href="/licitaciones"
            className="flex items-center gap-2 rounded-[60px] bg-[#eeeeee] px-5 py-2.5 text-sm font-semibold text-[#2c3833] transition-colors hover:bg-white"
          >
            Ver todas
          </Link>
        </div>
        <LicitacionesTable
          data={data.recentLicitaciones}
          showPagination={false}
          pageSize={5}
        />
      </div>
    </div>
  );
}
