"use server";

import { createClient } from "@/lib/supabase/server";
import { redirect } from "next/navigation";

export async function completeOnboarding(formData: {
  categorias: string[];
  instituciones: string[];
  monto_min: number | null;
}) {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) redirect("/auth/login");

  await supabase.from("user_profiles").upsert({
    user_id: user.id,
    categorias: formData.categorias,
    instituciones: formData.instituciones,
    monto_min: formData.monto_min,
    keywords: [],
    onboarding_completed: true,
    updated_at: new Date().toISOString(),
  });

  redirect("/dashboard");
}
