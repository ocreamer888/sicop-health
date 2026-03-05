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
import type { Licitacion, Categoria, TypeKey } from "@/lib/types";

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
  Publicado: { label: "Publicado", color: "bg-[#84a584]" },
  Adjudicado: { label: "Adjudicado", color: "bg-[#898a7d]" },
  Desierto: { label: "Desierto", color: "bg-[#5d6a85]" },
  Cancelado: { label: "Cancelado", color: "bg-[#a58484]" },
};

async function getDashboardData() {
  const supabase = await createClient();

  // Get total count
  const { count: totalCount } = await supabase
    .from("licitaciones_activas")
    .select("*", { count: "exact", head: true });

  // Get recent licitaciones
  const { data: recentLicitaciones } = await supabase
    .from("licitaciones_activas")
    .select("*")
    .order("created_at", { ascending: false })
    .limit(5);

  // Get all licitaciones for aggregation (we'll group in JS since Supabase doesn't support .group())
  const { data: allLicitaciones } = await supabase
    .from("licitaciones_activas")
    .select("categoria, estado, monto_colones");

  // Group by categoria
  const categoriaCounts = (allLicitaciones || []).reduce((acc, item) => {
    if (item.categoria) {
      acc[item.categoria] = (acc[item.categoria] || 0) + 1;
    }
    return acc;
  }, {} as Record<string, number>);

  const byCategoria = Object.entries(categoriaCounts).map(([categoria, count]) => ({
    categoria,
    count,
  }));

  // Group by estado
  const estadoCounts = (allLicitaciones || []).reduce((acc, item) => {
    if (item.estado) {
      acc[item.estado] = (acc[item.estado] || 0) + 1;
    }
    return acc;
  }, {} as Record<string, number>);

  const byEstado = Object.entries(estadoCounts).map(([estado, count]) => ({
    estado,
    count,
  }));

  // Calculate monto total
  const montoTotal = (allLicitaciones || []).reduce(
    (sum, item) => sum + (item.monto_colones || 0),
    0
  );

  return {
    totalLicitaciones: totalCount || 0,
    recentLicitaciones: recentLicitaciones || [],
    porCategoria: byCategoria,
    porEstado: byEstado,
    montoTotal,
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
          description="En la base de datos"
          icon={<FileText size={24} />}
        />
        <StatCard
          title="Monto Total"
          value={`$${(data.montoTotal / 1000000).toFixed(1)}M`}
          description="En licitaciones médicas"
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

      {/* Categorias */}
      <div className="mb-8">
        <h2 className="mb-4 text-xl font-semibold text-[#f9f5df] font-[family-name:var(--font-montserrat)]">
          Por Categoría
        </h2>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {data.porCategoria.map((item) => {
            const categoria = item.categoria as Categoria;
            return (
              <div
                key={categoria}
                className="flex items-center gap-4 rounded-[24px] bg-[#2c3833] p-4"
              >
                <div className="flex h-12 w-12 items-center justify-center rounded-[16px] bg-[#1a1f1a] text-[#f9f5df]">
                  {categoriaIcons[categoria]}
                </div>
                <div>
                  <p className="text-sm text-[#e4e4e4]">{categoriaLabels[categoria]}</p>
                  <p className="text-2xl font-semibold text-[#f9f5df]">
                    {item.count}
                  </p>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Por Estado */}
      <div className="mb-8">
        <h2 className="mb-4 text-xl font-semibold text-[#f9f5df] font-[family-name:var(--font-montserrat)]">
          Por Estado
        </h2>
        <div className="flex flex-wrap gap-3">
          {data.porEstado.map((item) => {
            const config = estadoColors[item.estado] || { label: item.estado, color: "bg-[#666]" };
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
          data={data.recentLicitaciones as Licitacion[]}
          showPagination={false}
          pageSize={5}
        />
      </div>
    </div>
  );
}
