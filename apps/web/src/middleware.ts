import { NextResponse, type NextRequest } from "next/server";

export async function middleware(request: NextRequest) {
  // Simple auth check - look for auth cookie presence
  // Full auth verification happens in server components
  const hasAuthCookie = request.cookies.has('sb-access-token') ||
                        request.cookies.has('sb-refresh-token');

  const isAuthPage = request.nextUrl.pathname.startsWith("/auth");
  const isPublicPage = request.nextUrl.pathname === "/";

  // Redirect to login if no auth cookie and trying to access protected page
  if (!hasAuthCookie && !isAuthPage && !isPublicPage) {
    const url = request.nextUrl.clone();
    url.pathname = "/auth/login";
    return NextResponse.redirect(url);
  }

  // Redirect to dashboard if has auth cookie and accessing login
  if (hasAuthCookie && request.nextUrl.pathname === "/auth/login") {
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
