// apps/web/app/dashboard/page.tsx
export const dynamic = 'force-dynamic';

import { createClient } from "@/lib/supabase/server";
import { StatCard } from "@/components/ui/stat-card";
import { LicitacionesTable } from "@/components/licitaciones-table";
import { Badge } from "@/components/ui/badge";
import { IntelScore } from "@/components/ui/intel-score";
import { StreakCounter } from "@/components/ui/streak-counter";
import { BadgeShelf } from "@/components/ui/badge-shelf";
import { calcIntelScore, calcStreak, getIntelScoreNextAction } from "@/lib/gamification";
import {
  FileText,
  DollarSign,
  TrendingUp,
  Database,
  Pill,
  Stethoscope,
  Microscope,
  Briefcase,
  Clock,
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

  // Total médicas clasificadas
  const { count: totalCount, error: totalError } = await supabase
    .from("licitaciones_medicas")
    .select("*", { count: "exact", head: true })
    .eq("es_medica", true)
    .not("categoria", "is", null);
  if (totalError) throw new Error(`Total query failed: ${totalError.message}`);

  // Nuevas esta semana — query real
  const { count: nuevasCount, error: nuevasError } = await supabase
    .from("licitaciones_medicas")
    .select("*", { count: "exact", head: true })
    .eq("es_medica", true)
    .gte(
      "created_at",
      new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString()
    );
  if (nuevasError) throw new Error(`Nuevas query failed: ${nuevasError.message}`);

  // v2: instcartelno + cartelnm + instnm + tipo_procedimiento + biddoc_end_dt
  const { data: recentLicitaciones, error: recentError } = await supabase
    .from("licitaciones_medicas")
    .select(
      "id, instcartelno, cartelnm, instnm, categoria, tipo_procedimiento, monto_colones, currency_type, biddoc_start_dt, biddoc_end_dt, estado, es_medica"
    )
    .eq("es_medica", true)
    .not("categoria", "is", null)
    .order("created_at", { ascending: false })
    .limit(5);
  if (recentError) throw new Error(`Recent query failed: ${recentError.message}`);

  // resumen_por_categoria — vista filtrada por es_medica=true AND categoria IS NOT NULL
  const { data: resumenCategoria, error: resumenError } = await supabase
    .from("resumen_por_categoria")
    .select("categoria, total, publicadas, adjudicadas, monto_crc, monto_usd");
  if (resumenError) throw new Error(`Resumen query failed: ${resumenError.message}`);

  // Excluir fila categoria=null + castear números (la vista retorna strings)
  const byCategoria = (resumenCategoria ?? [])
    .filter((r) => r.categoria !== null)
    .map((r) => ({
      categoria:   r.categoria! as Categoria,
      total:       r.total        ?? 0,
      publicadas:  r.publicadas   ?? 0,
      adjudicadas: r.adjudicadas  ?? 0,
      monto_crc:   Number(r.monto_crc  ?? 0),
      monto_usd:   Number(r.monto_usd  ?? 0),
    }));

  // byEstado acumulado desde byCategoria (sin query extra)
  const byEstado = byCategoria.reduce(
    (acc, r) => {
      acc["Publicado"]  = (acc["Publicado"]  ?? 0) + r.publicadas;
      acc["Adjudicado"] = (acc["Adjudicado"] ?? 0) + r.adjudicadas;
      return acc;
    },
    {} as Record<string, number>
  );

  // Totales de monto desde la vista (sin query separado)
  const montoCRC = byCategoria.reduce((sum, r) => sum + r.monto_crc, 0);
  const montoUSD = byCategoria.reduce((sum, r) => sum + r.monto_usd, 0);

  // Gamification data
  const { data: { user } } = await supabase.auth.getUser();
  let gamificationData = null;

  if (user) {
    const { data: profile } = await supabase
      .from("user_profiles")
      .select("*")
      .eq("user_id", user.id)
      .single();

    const { data: activityRows } = await supabase
      .from("user_activity")
      .select("activity_date")
      .eq("user_id", user.id)
      .order("activity_date", { ascending: false });

    const { data: badgeRows } = await supabase
      .from("user_badges")
      .select("badge_id")
      .eq("user_id", user.id);

    // Urgency: tenders closing in next 48h
    const now = new Date().toISOString();
    const in48h = new Date(Date.now() + 48 * 3_600_000).toISOString();
    const { count: urgentCount } = await supabase
      .from("licitaciones_medicas")
      .select("*", { count: "exact", head: true })
      .eq("es_medica", true)
      .gte("biddoc_end_dt", now)
      .lte("biddoc_end_dt", in48h);

    gamificationData = {
      profile,
      activityCount: activityRows?.length ?? 0,
      activityDates: activityRows?.map(r => r.activity_date) ?? [],
      earnedBadgeIds: badgeRows?.map(b => b.badge_id) ?? [],
      urgentCount: urgentCount ?? 0,
    };
  }

  return {
    totalLicitaciones:  totalCount  ?? 0,
    nuevasEstaSemana:   nuevasCount ?? 0,
    recentLicitaciones: (recentLicitaciones ?? []) as LicitacionPreview[],
    porCategoria:       byCategoria,
    porEstado:          Object.entries(byEstado).map(([estado, count]) => ({ estado, count })),
    montoCRC,
    montoUSD,
    gamificationData,
  };
}

export default async function DashboardPage() {
  let data;
  let error: Error | null = null;
  
  try {
    data = await getDashboardData();
  } catch (e) {
    error = e instanceof Error ? e : new Error(String(e));
    console.error("Dashboard data fetch failed:", error);
  }
  
  if (error) {
    return (
      <div className="mx-auto max-w-[1393px] px-6 py-8">
        <div className="rounded-[24px] bg-[#a58484]/10 border border-[#a58484]/30 p-8">
          <h1 className="text-2xl font-semibold text-[#a58484] mb-4">Error cargando dashboard</h1>
          <p className="text-[#f2f5f9] font-mono text-sm">{error.message}</p>
          <p className="text-[var(--color-text-muted)] mt-4 text-sm">
            Verifica que las tablas y vistas de Supabase existen y tienen datos.
          </p>
        </div>
      </div>
    );
  }
  
  if (!data) {
    return (
      <div className="mx-auto max-w-[1393px] px-6 py-8">
        <div className="rounded-[24px] bg-[#2c3833] p-8">
          <p className="text-[var(--color-text-muted)]">Cargando...</p>
        </div>
      </div>
    );
  }

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
          value={`+${data.nuevasEstaSemana}`}
          icon={<TrendingUp size={24} />}
        />
        <StatCard
          title="Estados"
          value={data.porEstado.length.toString()}
          description="Publicado, Adjudicado, Desierto, Cancelado"
          icon={<Database size={24} />}
        />
      </div>

      {/* Gamification widgets */}
      {data.gamificationData && (
        <>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
            <IntelScore
              score={calcIntelScore(data.gamificationData.profile, data.gamificationData.activityCount)}
              nextAction={getIntelScoreNextAction(data.gamificationData.profile, data.gamificationData.activityCount)}
            />
            <StreakCounter streak={calcStreak(data.gamificationData.activityDates)} />
            {(data.gamificationData.urgentCount ?? 0) > 0 && (
              <Link href="/licitaciones?urgente=true">
                <div className="rounded-[24px] bg-[#2c3833] border border-[#3d4d45] p-5 hover:border-[#84a584]/50 transition-all cursor-pointer">
                  <div className="flex items-center gap-2 mb-1">
                    <Clock size={16} className="text-[#b5a88a]" />
                    <span className="text-xs font-medium text-[var(--color-text-muted)] uppercase tracking-wide">Urgente</span>
                  </div>
                  <p className="text-xl font-bold text-[#f9f5df] font-[family-name:var(--font-montserrat)]">
                    ⏳ {data.gamificationData.urgentCount}
                  </p>
                  <p className="text-xs text-[#5a6a62] mt-1 font-[family-name:var(--font-plus-jakarta)]">
                    licitaciones cierran en 48h
                  </p>
                </div>
              </Link>
            )}
          </div>

          {/* Badge shelf */}
          <div className="mb-8">
            <BadgeShelf earnedBadgeIds={data.gamificationData.earnedBadgeIds} />
          </div>
        </>
      )}

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

      {/* Licitaciones Recientes */}
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
