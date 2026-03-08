"use server";

import { createClient } from "@/lib/supabase/server";

export async function getNotificaciones() {
  const supabase = await createClient();

  const { data, error } = await supabase
    .from("notificaciones")
    .select(`
      id,
      created_at,
      licitaciones_medicas!inner (
        instcartelno,
        cartelnm,
        instnm,
        categoria,
        monto_colones,
        currency_type,
        biddoc_end_dt,
        estado
      )
    `)
    .order("created_at", { ascending: false })
    .limit(100);

  if (error) {
    console.error("[getNotificaciones]", error.message);
    return [];
  }

  return (data ?? []).map((row) => ({
    id: row.id,
    created_at: row.created_at,
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    ...(row.licitaciones_medicas as any),
  }));
}

export async function markNotificacionRead(notificacionId: string) {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return;

  await supabase.from("notificaciones_leidas").upsert(
    { user_id: user.id, notificacion_id: notificacionId },
    { onConflict: "user_id,notificacion_id" }
  );
}

export async function getReadIds(): Promise<string[]> {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return [];

  const { data } = await supabase
    .from("notificaciones_leidas")
    .select("notificacion_id")
    .eq("user_id", user.id);

  return data?.map(r => r.notificacion_id) ?? [];
}
