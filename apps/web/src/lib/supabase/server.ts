import { createServerClient } from "@supabase/ssr";
import { cookies } from "next/headers";

export async function createClient() {
  const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

  // Debug logging - will appear in Vercel function logs
  console.log("[Supabase Server Client] Env vars check:", {
    hasUrl: !!supabaseUrl,
    hasKey: !!supabaseKey,
    urlValue: supabaseUrl ? `${supabaseUrl.substring(0, 20)}...` : "MISSING",
    keyValue: supabaseKey ? `${supabaseKey.substring(0, 20)}...` : "MISSING",
    allEnvKeys: Object.keys(process.env).filter(k => k.includes("SUPABASE")),
  });

  if (!supabaseUrl || !supabaseKey) {
    throw new Error(
      `Missing Supabase environment variables. ` +
      `NEXT_PUBLIC_SUPABASE_URL=${supabaseUrl ? "set" : "MISSING"}, ` +
      `NEXT_PUBLIC_SUPABASE_ANON_KEY=${supabaseKey ? "set" : "MISSING"}. ` +
      `Please check your Vercel environment variables.`
    );
  }

  const cookieStore = await cookies();

  return createServerClient(
    supabaseUrl,
    supabaseKey,
    {
      cookies: {
        getAll() {
          return cookieStore.getAll();
        },
        setAll(cookiesToSet) {
          try {
            cookiesToSet.forEach(({ name, value, options }) =>
              cookieStore.set(name, value, options)
            );
          } catch {
            // The `setAll` method was called from a Server Component.
            // This can be ignored if you have middleware refreshing
            // user sessions.
          }
        },
      },
    }
  );
}
