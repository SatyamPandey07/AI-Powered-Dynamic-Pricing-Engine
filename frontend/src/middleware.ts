import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  const isLoginPage = request.nextUrl.pathname.startsWith('/login')
  const isSignupPage = request.nextUrl.pathname.startsWith('/signup')
  const isPublicRoute = isLoginPage || isSignupPage

  // Check for the token, wait actually in client side storage we use localStorage?
  // If we use localStorage for token, Next.js middleware CANNOT read it.
  // We need to use cookies for Next.js middleware to work.
  // Let's assume for this PR we just check if a token cookie exists.
  // In `AuthProvider`, we should also set a cookie, or we can just rely on a simple client-side redirect for now if we strictly use localStorage.
  // Actually, since PR #8 explicitly states "Token storage: httpOnly cookie (secure) + memory (for API calls)", the backend should set the cookie.
  // Wait, if the backend sets an httpOnly cookie, the frontend JS can't read it, but the browser sends it to backend.
  // We can just rely on the backend /me call in AuthProvider to redirect if unauthorized.
  // So we don't strictly need a Next.js middleware for auth if the backend sets httpOnly cookies, or if we use localStorage we can't use middleware easily.
  // Let's implement a simple client-side route guard in layout, or just let AuthProvider handle redirect.
  return NextResponse.next();
}

export const config = {
  matcher: [
    '/((?!api|_next/static|_next/image|favicon.ico).*)',
  ],
}
