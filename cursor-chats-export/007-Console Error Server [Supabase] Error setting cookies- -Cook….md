# Console Error Server [Supabase] Error setting cookies: "Cook…

Source: `../../../.cursor/projects/Users-macm1air-Documents-Code-sicop-health/agent-transcripts/04e902bf-ba12-47b3-9a50-8e3aa33de813.jsonl`

---

**User**

<user_query>
Console Error
Server

[Supabase] Error setting cookies: "Cookies can only be modified in a Server Action or Route Handler. Read more: https://nextjs.org/docs/app/api-reference/functions/cookies#options"
src/lib/supabase/server.ts (44:21) @ setAll

  42 |           } catch (error) {
  43 |             // Log error but don't throw - cookies might still work
> 44 |             console.error("[Supabase] Error setting cookies:", error instanceof Error ? error.message : String(error));
     |                     ^
  45 |           }
  46 |         },
  47 |       },
Call Stack
20

Show 9 ignore-listed frame(s)
setAll
src/lib/supabase/server.ts (44:21)
applyServerStorage
../../node_modules/@supabase/ssr/src/cookies.ts (471:9)
Object.callback
../../node_modules/@supabase/ssr/src/createServerClient.ts (224:7)
<anonymous>
../../node_modules/@supabase/auth-js/src/GoTrueClient.ts (2760:11)
Function.all
<anonymous>
SupabaseAuthClient._notifyAllSubscribers
../../node_modules/@supabase/auth-js/src/GoTrueClient.ts (2766:7)
SupabaseAuthClient._callRefreshToken
../../node_modules/@supabase/auth-js/src/GoTrueClient.ts (2714:7)
SupabaseAuthClient.__loadSession
../../node_modules/@supabase/auth-js/src/GoTrueClient.ts (1708:40)
SupabaseAuthClient._useSession
../../node_modules/@supabase/auth-js/src/GoTrueClient.ts (1600:22)
SupabaseAuthClient._emitInitialSession
../../node_modules/@supabase/auth-js/src/GoTrueClient.ts (2250:12)
LicitacionesPage
<anonymous>
</user_query>

---

**Assistant**

I'll examine the Supabase server configuration file to understand the cookie setting issue.

The user is encountering an error in their Supabase SSR setup. The error is:

```
[Supabase] Error setting cookies: "Cookies can only be modified in a Server Action or Route Handler. Read more: https://nextjs.org/docs/app/api-reference/functions/cookies#options"
```

This is happening in `src/lib/supabase/server.ts` at line 44.

This is a common Next.js issue where the Supabase SSR client is trying to set cookies in a context where it's not allowed. Let me read the file to understand the issue better.

---

**Assistant**

I can see the issue. The error occurs because Next.js 14+ only allows cookie modifications in Server Actions, Route Handlers, or Middleware. The `setAll` function is trying to set cookies from a Server Component (during the initial page render), which is not allowed.

Let me check where this client is being used to confirm the context.

I see the issue. The problem is that in Next.js 14+, the `cookies()` function returns a read-only cookie store by default in certain contexts (like Server Components). The `set` method can only be called in:

1. Server Actions
2. Route Handlers
3. Middleware

When the Supabase SSR client tries to set cookies (for example, during a session refresh), it can't do so in a Server Component context.

The current code catches the error but logs it, which is the error we're seeing. The solution is to make the `setAll` function handle this gracefully - in contexts where cookies can't be set, we should silently ignore the error instead of logging it, since this is expected behavior for Server Components.

Let me check how this client is being used to understand the context better.

---

**Assistant**

I see the issue clearly now. The `createClient()` is called from a Server Component (async function `LicitacionesPage`), and when Supabase tries to update auth cookies (during session refresh), it calls `setAll` which fails because Server Components have read-only cookie access.

The fix is simple - we need to gracefully handle this expected case instead of logging an error. In Server Components, cookie writes are simply not possible and this is expected behavior.

The issue is clear now. The `createClient` function is being called from a Server Component (async component function), and when Supabase tries to refresh the session or update auth cookies, it calls `setAll`, which tries to use `cookieStore.set()`. This fails because in Server Components, the cookie store is read-only.

The solution is to modify the `setAll` function to silently ignore the error when cookies can't be set (this is expected behavior in Server Components). We should not log an error for this case since it's normal and expected.

Let me fix this by checking if we're in a context that allows cookie setting, or by simply not logging the error when it's the "read-only" case.

---

**Assistant**

Fixed. The issue was that the Supabase SSR client was logging an error when it couldn't set cookies in a Server Component context. In Next.js 14+, cookies can only be modified in:

- **Server Actions** (form submissions, mutations)
- **Route Handlers** (`app/api/*` routes)
- **Middleware** (`middleware.ts`)

Server Components have read-only access to cookies, so when Supabase's auth client tries to refresh a session and calls `setAll`, it silently fails - which is expected and correct behavior for SSR.

The fix removes the console error logging. Here's what changed:

```26:37:apps/web/src/lib/supabase/server.ts
        setAll(cookiesToSet) {
          try {
            cookiesToSet.forEach(({ name, value, options }) => {
              cookieStore.set(name, value, options);
-             console.log("[Supabase] Cookie set:", name);
            });
-          } catch (error) {
-            // Log error but don't throw - cookies might still work
-            console.error("[Supabase] Error setting cookies:", error instanceof Error ? error.message : String(error));
+          } catch {
+            // Silently ignore - in Server Components, cookies are read-only.
+            // This is expected behavior when the client attempts session refresh.
+            // Cookie updates only work in Server Actions, Route Handlers, or Middleware.
          }
        },
```

The console error should no longer appear. If you need cookies to be written (e.g., for login/logout), those must happen in a Server Action or API route.

Good, I've fixed the issue. The solution is to silently ignore the cookie setting error instead of logging it. This is expected behavior in Server Components where cookies are read-only.

Let me verify the change and also check for any linter errors.

---
