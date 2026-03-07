"use server";

import { createClient } from "@/lib/supabase/server";

export async function getNotificaciones() {
  const supabase = await createClient();

  const since = new Date();
  since.setDate(since.getDate() - 30);

  const { data, error } = await supabase
    .from("licitaciones_medicas")
    .select(
      "id, instcartelno, cartelnm, instnm, categoria, monto_colones, currency_type, biddoc_end_dt, estado, created_at"
    )
    .eq("es_medica", true)
    .in("estado", ["Publicado", "Modificado"])
    .gte("created_at", since.toISOString())
    .order("created_at", { ascending: false })
    .limit(100);

  if (error) {
    console.error("[getNotificaciones]", error.message);
    return [];
  }
  return data ?? [];
}
