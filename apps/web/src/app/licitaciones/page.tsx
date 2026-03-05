import { createClient } from "@/lib/supabase/server";
import { LicitacionesTable } from "@/components/licitaciones-table";
import type { Licitacion } from "@/lib/types";

async function getLicitaciones() {
  const supabase = await createClient();

  const { data, error } = await supabase
    .from("licitaciones_activas")
    .select("*")
    .order("created_at", { ascending: false });

  if (error) {
    console.error("Error fetching licitaciones:", {
      message: error.message,
      code: error.code,
      details: error.details,
      hint: error.hint,
    });
    return [];
  }

  return data || [];
}

export default async function LicitacionesPage() {
  const licitaciones = await getLicitaciones();

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

      {/* Table */}
      <div className="rounded-[32px] bg-[#1a1f1a] p-6">
        <LicitacionesTable data={licitaciones as Licitacion[]} />
      </div>
    </div>
  );
}
