import { NextResponse, type NextRequest } from "next/server";
import { createServerClient } from "@supabase/ssr";

// Get project ID from env or use a default pattern
const SUPABASE_PROJECT_ID = process.env.NEXT_PUBLIC_SUPABASE_URL?.match(/https:\/\/([^.]+)\./)?.[1] || '';
const SUPABASE_URL = process.env.NEXT_PUBLIC_SUPABASE_URL || '';
const SUPABASE_KEY = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || '';

export async function middleware(request: NextRequest) {
  // Check for Supabase auth cookie - specifically for THIS project
  // Supabase SSR uses format: sb-<project-ref>-auth-token
  const allCookies = request.cookies.getAll();
  const cookieNames = allCookies.map(c => c.name);
  
  // Only check for the current project's auth cookie
  const authCookieName = SUPABASE_PROJECT_ID 
    ? `sb-${SUPABASE_PROJECT_ID}-auth-token`
    : null;
  
  const hasAuthCookie = authCookieName 
    ? allCookies.some((cookie) => cookie.name.startsWith(authCookieName))
    : false;

  console.log("[Middleware] Path:", request.nextUrl.pathname, "Project:", SUPABASE_PROJECT_ID, "HasAuth:", hasAuthCookie);

  const isAuthPage = request.nextUrl.pathname.startsWith("/auth");
  const isPublicPage = request.nextUrl.pathname === "/";

  // Redirect to login if no auth cookie and trying to access protected page
  if (!hasAuthCookie && !isAuthPage && !isPublicPage) {
    console.log("[Middleware] Redirecting to login - no auth cookie");
    const url = request.nextUrl.clone();
    url.pathname = "/auth/login";
    return NextResponse.redirect(url);
  }

  // Redirect to dashboard if has auth cookie and accessing login
  if (hasAuthCookie && request.nextUrl.pathname === "/auth/login") {
    console.log("[Middleware] Redirecting to dashboard - has auth cookie");
    const url = request.nextUrl.clone();
    url.pathname = "/dashboard";
    return NextResponse.redirect(url);
  }

  // Onboarding check: if authenticated and NOT on onboarding page, check if onboarding is needed
  if (hasAuthCookie && !request.nextUrl.pathname.startsWith("/auth")) {
    const supabase = createServerClient(SUPABASE_URL, SUPABASE_KEY, {
      cookies: {
        getAll() {
          return request.cookies.getAll();
        },
        setAll(cookiesToSet) {
          cookiesToSet.forEach(({ name, value, options }) => {
            request.cookies.set(name, value);
          });
        },
      },
    });

    const { data: { user } } = await supabase.auth.getUser();
    if (user) {
      try {
        const { data: profile } = await supabase
          .from("user_profiles")
          .select("onboarding_completed")
          .eq("user_id", user.id)
          .single();

        if (!profile || !profile.onboarding_completed) {
          console.log("[Middleware] Redirecting to onboarding - incomplete profile");
          const url = request.nextUrl.clone();
          url.pathname = "/auth/onboarding";
          return NextResponse.redirect(url);
        }
      } catch (error) {
        // Table doesn't exist or other error - redirect to onboarding to create profile
        console.log("[Middleware] Redirecting to onboarding - profile check failed", error);
        const url = request.nextUrl.clone();
        url.pathname = "/auth/onboarding";
        return NextResponse.redirect(url);
      }
    }
  }

  return NextResponse.next({ request });
}

export const config = {
  matcher: [
    "/((?!_next/static|_next/image|favicon.ico|.*\.(?:svg|png|jpg|jpeg|gif|webp)$).*)",
  ],
};
