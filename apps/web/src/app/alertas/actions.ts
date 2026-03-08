"use server";

import { createClient } from "@/lib/supabase/server";
import { revalidatePath } from "next/cache";
import type { AlertaFormData } from "@/lib/types";

export async function getAlertas() {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return [];

  const { data, error } = await supabase
    .from("alertas_config")
    .select("*")
    .eq("user_id", user.id)
    .order("created_at", { ascending: false });

  if (error) {
    console.error("[getAlertas]", error.message);
    return [];
  }
  return data ?? [];
}

export async function createAlerta(formData: AlertaFormData) {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return { error: "No autorizado" };

  console.log("[createAlerta] Form data:", formData);

  const insertData = {
    ...formData,
    user_id: user.id,
  };

  console.log("[createAlerta] Insert data:", insertData);

  const { error } = await supabase.from("alertas_config").insert(insertData);

  if (error) {
    console.error("[createAlerta] Error:", error.message, error.details);
    return { error: error.message };
  }
  revalidatePath("/alertas");
  return { success: true };
}

export async function updateAlerta(id: string, formData: AlertaFormData) {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return { error: "No autorizado" };

  const { error } = await supabase
    .from("alertas_config")
    .update({ ...formData, updated_at: new Date().toISOString() })
    .eq("id", id)
    .eq("user_id", user.id);

  if (error) return { error: error.message };
  revalidatePath("/alertas");
  return { success: true };
}

export async function deleteAlerta(id: string) {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return { error: "No autorizado" };

  const { error } = await supabase
    .from("alertas_config")
    .delete()
    .eq("id", id)
    .eq("user_id", user.id);

  if (error) return { error: error.message };
  revalidatePath("/alertas");
  return { success: true };
}

export async function toggleAlerta(id: string, activo: boolean) {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return { error: "No autorizado" };

  const { error } = await supabase
    .from("alertas_config")
    .update({ activo, updated_at: new Date().toISOString() })
    .eq("id", id)
    .eq("user_id", user.id);

  if (error) return { error: error.message };
  revalidatePath("/alertas");
  return { success: true };
}
