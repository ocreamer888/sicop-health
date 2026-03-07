"use server";

import { createClient } from "@/lib/supabase/server";
import { redirect } from "next/navigation";
import { revalidatePath } from "next/cache";

export async function signIn(formData: FormData) {
  const email = formData.get("email") as string;
  const password = formData.get("password") as string;

  const supabase = await createClient();
  const { error } = await supabase.auth.signInWithPassword({ email, password });

  if (error) {
    redirect("/auth/login?error=" + encodeURIComponent(error.message));
  }

  redirect("/dashboard");
}

export async function signOut() {
  const supabase = await createClient();
  
  // Sign out from Supabase (clears the auth cookie)
  const { error } = await supabase.auth.signOut();
  
  if (error) {
    console.error("[signOut] Error:", error.message);
  }
  
  // The cookie is cleared by supabase.auth.signOut() via the setAll callback
  // Redirect to login - middleware will see no auth cookie
  redirect("/auth/login");
}

/**
 * Invite a new user by email (admin only)
 * Requires service role key or admin privileges
 */
export async function inviteUser(formData: FormData) {
  const email = formData.get("email") as string;
  const supabase = await createClient();

  // Get current user to verify admin status
  const { data: { user } } = await supabase.auth.getUser();

  if (!user) {
    return { error: "No autorizado" };
  }

  // Check if user is admin (you'll need to set up admin role in your DB)
  const { data: profile } = await supabase
    .from("profiles")
    .select("role")
    .eq("id", user.id)
    .single();

  if (profile?.role !== "admin") {
    return { error: "Solo administradores pueden invitar usuarios" };
  }

  // Send invite
  const { error } = await supabase.auth.admin.inviteUserByEmail(email, {
    redirectTo: `${process.env.NEXT_PUBLIC_SITE_URL}/auth/invite`,
  });

  if (error) {
    return { error: error.message };
  }

  revalidatePath("/admin/users");
  return { success: true };
}
