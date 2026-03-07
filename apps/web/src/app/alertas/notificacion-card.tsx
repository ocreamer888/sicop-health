import Link from "next/link";
import { Building2, Tag, CalendarClock, ArrowUpRight } from "lucide-react";

interface NotificacionCardProps {
  instcartelno: string;
  cartelnm: string | null;
  instnm: string | null;
  categoria: string | null;
  monto_colones: number | null;
  currency_type: string | null;
  biddoc_end_dt: string | null;
  estado: string | null;
  created_at: string;
}

function formatMonto(monto: number | null, currency: string | null) {
  if (!monto) return null;
  const sym = currency === "USD" ? "$" : "₡";
  return `${sym}${monto.toLocaleString("es-CR")}`;
}

function formatDate(dt: string | null) {
  if (!dt) return null;
  return new Date(dt).toLocaleDateString("es-CR", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}

function timeAgo(iso: string) {
  const diff = Date.now() - new Date(iso).getTime();
  const h = Math.floor(diff / 3_600_000);
  const d = Math.floor(diff / 86_400_000);
  if (h < 1) return "Hace menos de 1h";
  if (h < 24) return `Hace ${h}h`;
  if (d === 1) return "Ayer";
  return `Hace ${d} días`;
}

const CATEGORIA_COLORS: Record<string, string> = {
  MEDICAMENTO: "bg-[#84a584]/15 text-[#84a584]",
  EQUIPAMIENTO: "bg-[#8a9bb5]/15 text-[#8a9bb5]",
  INSUMO: "bg-[#b5a88a]/15 text-[#b5a88a]",
  SERVICIO: "bg-[#898a7d]/15 text-[#898a7d]",
};

export function NotificacionCard({
  instcartelno,
  cartelnm,
  instnm,
  categoria,
  monto_colones,
  currency_type,
  biddoc_end_dt,
  estado,
  created_at,
}: NotificacionCardProps) {
  const monto = formatMonto(monto_colones, currency_type);
  const cierre = formatDate(biddoc_end_dt);
  const catColor = categoria ? (CATEGORIA_COLORS[categoria] ?? "bg-[#898a7d]/15 text-[#898a7d]") : null;

  return (
    <div className="rounded-[24px] bg-[#2c3833] border border-[#3d4d45] p-5 hover:border-[#84a584]/40 transition-all">
      {/* Top row: time + estado */}
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs text-[#5a6a62]">{timeAgo(created_at)}</span>
        {estado && (
          <span className="text-xs px-2.5 py-0.5 rounded-[60px] bg-[#1a1f1a] text-[#5a6a62] border border-[#3d4d45]">
            {estado}
          </span>
        )}
      </div>

      {/* Title */}
      <p className="text-[#f9f5df] font-medium text-sm leading-snug mb-3 font-[family-name:var(--font-montserrat)] line-clamp-2">
        {cartelnm ?? instcartelno}
      </p>

      {/* Meta */}
      <div className="space-y-1.5 mb-4">
        {instnm && (
          <div className="flex items-center gap-1.5 text-xs text-[#5a6a62]">
            <Building2 size={12} />
            <span className="truncate">{instnm}</span>
          </div>
        )}
        {categoria && (
          <div className="flex items-center gap-1.5">
            <Tag size={12} className="text-[#5a6a62]" />
            <span className={`text-xs px-2 py-0.5 rounded-[60px] ${catColor}`}>
              {categoria}
            </span>
          </div>
        )}
        {cierre && (
          <div className="flex items-center gap-1.5 text-xs text-[#5a6a62]">
            <CalendarClock size={12} />
            <span>Cierre: {cierre}</span>
          </div>
        )}
        {monto && (
          <p className="text-xs text-[#f2f5f9] font-medium pl-0.5">{monto}</p>
        )}
      </div>

      {/* CTA */}
      <Link
        href={`/licitaciones/${instcartelno}`}
        className="flex items-center gap-1.5 text-xs font-medium text-[#84a584] hover:text-[#a5c4a5] transition-colors"
      >
        Ver licitación
        <ArrowUpRight size={13} />
      </Link>
    </div>
  );
}
