import { NextResponse, type NextRequest } from "next/server";

export async function middleware(request: NextRequest) {
  // Check for Supabase auth cookie
  // Supabase SSR uses format: sb-<project-ref>-auth-token
  const allCookies = request.cookies.getAll();
  const cookieNames = allCookies.map(c => c.name);
  const hasAuthCookie = allCookies.some(
    (cookie) => cookie.name.startsWith('sb-') && cookie.name.includes('auth-token')
  );

  console.log("[Middleware] Path:", request.nextUrl.pathname, "Cookies:", cookieNames, "HasAuth:", hasAuthCookie);

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

  return NextResponse.next({ request });
}

export const config = {
  matcher: [
    "/((?!_next/static|_next/image|favicon.ico|.*\.(?:svg|png|jpg|jpeg|gif|webp)$).*)",
  ],
};
