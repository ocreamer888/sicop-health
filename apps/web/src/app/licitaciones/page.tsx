export const dynamic = 'force-dynamic';

import { createClient } from "@/lib/supabase/server";
import { LicitacionesFilter } from "./licitaciones-filter"
import type { LicitacionPreview } from "@/lib/types";

async function getLicitaciones(): Promise<LicitacionPreview[]> {
  const supabase = await createClient();

  const { data, error } = await supabase
    .from("licitaciones_medicas")
    .select(
      "id, instcartelno, cartelnm, instnm, categoria, tipo_procedimiento, monto_colones, currency_type, biddoc_start_dt, biddoc_end_dt, estado, es_medica"
    )
    .eq("es_medica", true)
    .not("categoria", "is", null)
    .order("biddoc_start_dt", { ascending: false });

  if (error) {
    throw new Error(`Supabase error: ${error.message} (code: ${error.code})`);
  }

  return (data as LicitacionPreview[]) || [];
}

export default async function LicitacionesPage() {
  let licitaciones: LicitacionPreview[] = [];
  let error: Error | null = null;

  try {
    licitaciones = await getLicitaciones();
  } catch (e) {
    error = e instanceof Error ? e : new Error(String(e));
    console.error("Licitaciones fetch failed:", error);
  }

  if (error) {
    return (
      <div className="mx-auto max-w-[1393px] px-6 py-8">
        <div className="rounded-[24px] bg-[#a58484]/10 border border-[#a58484]/30 p-8">
          <h1 className="text-2xl font-semibold text-[#a58484] mb-4">Error cargando licitaciones</h1>
          <p className="text-[#f2f5f9] font-mono text-sm">{error.message}</p>
        </div>
      </div>
    );
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
  );
}
