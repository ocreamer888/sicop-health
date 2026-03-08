"use server";

import { createClient } from "@/lib/supabase/server";

export async function completeOnboarding(formData: {
  categorias: string[];
  instituciones: string[];
  monto_min: number | null;
}) {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) throw new Error("Not authenticated");

  const { error } = await supabase.from("user_profiles").upsert({
    user_id: user.id,
    categorias: formData.categorias,
    instituciones: formData.instituciones,
    monto_min: formData.monto_min,
    keywords: [],
    onboarding_completed: true,
    updated_at: new Date().toISOString(),
  });

  if (error) throw new Error(`Failed to save profile: ${error.message}`);

  return { success: true };
}
