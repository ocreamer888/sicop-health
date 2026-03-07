# SICOP Health Intelligence — Strategic Task List
_Last updated: 2026-03-06_

---

## Philosophy

**Ship the core value proposition first.** The alert system is what differentiates this from a spreadsheet. Everything else is optimization.

**Order of attack:**
1. Foundation (data integrity + auth solidity)
2. Core Value (alert system end-to-end)
3. Growth (analytics, exports, expansion)

---

## Phase 1: Foundation (Week 1)

**Goal:** Solid data layer and auth. No cracks in the foundation.

### 1.1 Fix Data Layer Inconsistencies
- [ ] **Migrate `licitaciones/page.tsx` from view to direct table query**
  - Change from `licitaciones_activas` to `licitaciones_medicas`
  - Add filters: `es_medica = true`, `categoria IS NOT NULL`
  - Keep same columns for `LicitacionPreview` compatibility
  - **Test:** Links from /licitaciones to detail pages work correctly

- [ ] **Run 90-day backfill**
  - Execute: `cd services/etl && python main.py --dias 90`
  - Validate row counts in Supabase dashboard
  - **Deliverable:** 500+ licitaciones in DB with full history

### 1.2 Apply RLS in Production
- [ ] **Execute migration 004_rls.sql in Supabase Dashboard**
  - Navigate to SQL Editor → New query
  - Paste contents of `supabase/migrations/004_rls.sql`
  - Run and verify no errors
  - **Test:** Try accessing data without auth (should fail)

- [ ] **Create first admin user**
  - Supabase Dashboard → Authentication → Users → Add user
  - Set email/password for initial access
  - **Deliverable:** Can log in to /dashboard with real credentials

---

## Phase 2: Core Value — Alert System (Weeks 2-3)

**Goal:** Working alert creation → matching → notification flow. This is the product.

### 2.1 Alert Configuration UI (`/alertas`)
- [ ] **Create alertas page scaffold**
  - Route: `/alertas/page.tsx`
  - Protected route (inherits middleware)
  - Layout matches design system

- [ ] **Build alert creation form**
  - Fields:
    - `nombre` (text input)
    - `keywords` (tag input, comma-separated)
    - `categorias` (multi-select: MEDICAMENTO, EQUIPAMIENTO, INSUMO, SERVICIO)
    - `instituciones` (multi-select from `instituciones_salud` table)
    - `monto_min`, `monto_max` (number inputs, optional)
    - `canales` (checkboxes: email, whatsapp)
  - Submit creates row in `alertas_config`
  - **Validation:** At least one of keywords, categorias, or instituciones required

- [ ] **Build alerts list view**
  - Table showing user's active/inactive alerts
  - Toggle on/off switch
  - Edit and Delete actions
  - Empty state when no alerts created

### 2.2 Alert Matching Engine
- [ ] **Create edge function: `match-alerts`**
  - Trigger: HTTP endpoint (called by ETL after insert)
  - Input: `instcartelno` of new licitacion
  - Logic:
    1. Fetch licitacion data
    2. Query `alertas_config` for all active alerts
    3. For each alert, evaluate match:
       - Keywords: OR match in `cartelnm` (case-insensitive)
       - Categorias: exact match on `categoria`
       - Instituciones: match on `inst_code`
       - Monto: between min/max if specified
    4. Insert matches into `alertas_enviadas` table (prevent duplicates)
    5. Return array of matched alert IDs + user emails

- [ ] **Create `alertas_enviadas` table (migration 005)**
  ```sql
  CREATE TABLE alertas_enviadas (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    alerta_id UUID REFERENCES alertas_config(id),
    instcartelno TEXT REFERENCES licitaciones_medicas(instcartelno),
    user_id UUID REFERENCES auth.users(id),
    enviado_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(alerta_id, instcartelno) -- prevent duplicates
  );
  ```

- [ ] **Integrate matching into ETL**
  - After `uploader.py` inserts new licitaciones
  - Call edge function for each new `instcartelno`
  - Log matches for debugging

### 2.3 Email Notifications (Resend)
- [ ] **Setup Resend account**
  - Sign up at resend.com
  - Verify domain (or use onboarding domain)
  - Get API key

- [ ] **Create edge function: `send-email`**
  - Use Deno runtime
  - Template HTML matching design system colors
  - Content:
    - Alert name that matched
    - Licitacion details (instcartelno, cartelnm, instnm, monto, deadline)
    - CTA button: "Ver en SICOP Health" (links to our platform)
    - Secondary link: "Ver en SICOP oficial"

- [ ] **Wire notification flow**
  - `match-alerts` returns matched users
  - For each match with email channel: call `send-email`
  - Log successes/failures

### 2.4 Test End-to-End
- [ ] **Create test alert**
  - Keyword: "insulina"
  - User: your email
  - Channel: email

- [ ] **Verify detection**
  - Manually trigger ETL or wait for hourly run
  - Confirm new licitacion with "insulina" triggers match
  - Check `alertas_enviadas` table has row

- [ ] **Verify notification**
  - Email received within 5 minutes
  - Links work correctly
  - Design renders properly

---

## Phase 3: Polish & Growth (Week 4)

**Goal:** Make it feel professional and sticky.

### 3.1 Dashboard Enhancements
- [ ] **Add "Licitaciones que te interesan" section**
  - Based on user's alert keywords
  - Show top 5 matches from last 7 days
  - Appears above "Recientes" if user has alerts

- [ ] **Gráfico por institución**
  - Bar chart: CCSS vs MINSA vs INS vs Otros
  - Reuse same data from dashboard query

### 3.2 WhatsApp Integration (Optional but high value)
- [ ] **Setup WhatsApp Business API**
  - Meta Business account
  - Verify phone number
  - Create message template (needs Meta approval)

- [ ] **Create edge function: `send-whatsapp`**
  - Call WhatsApp Business API
  - Use approved template
  - Personalize with licitacion data

### 3.3 Export Features
- [ ] **Export table to Excel**
  - Button on /licitaciones
  - Server-side CSV generation
  - Download via API route

---

## Phase 4: Expansion (Post-MVP)

**Goal:** Scale the product.

### 4.1 Data Depth
- [ ] **ETL de precios con Playwright**
  - Scrape detail pages of adjudicaciones
  - Extract item-level prices
  - Populate `precios_historicos`

- [ ] **Vista /precios**
  - Search product by name/UNSPSC
  - Price evolution chart
  - Institution comparison

### 4.2 Multi-tenancy
- [ ] **Team accounts**
  - `empresas` table
  - Multiple users per empresa
  - Shared alerts within empresa
  - Admin role can manage team

### 4.3 Regional Expansion
- [ ] **Guatemala: Guatecompras**
  - New fetcher for guatecompras.gt API
  - Reuse classifier logic
  - Separate table or add `pais` column

---

## Execution Rules

1. **Complete Phase 1 before touching Phase 2**
   - Bad data ruins the alert system

2. **Each task must have a testable deliverable**
   - "Build form" is vague. "Form creates row in alertas_config on submit" is testable.

3. **No premature optimization**
   - 100 users = don't worry about scale yet
   - Focus on features that get us to 100 users

4. **Daily commits**
   - Every task ends with a commit
   - No "work in progress" branches older than 24h

---

## Success Criteria (Definition of Done)

| Phase | Criteria |
|-------|----------|
| **1** | Can log in, see 500+ licitaciones, navigate detail pages without errors |
| **2** | Create alert with "insulina", new CCSS licitacion triggers, email arrives with correct link |
| **3** | Dashboard shows personalized recommendations, can export to Excel |
| **4** | 3+ paying customers, expansion to Guatemala scoped |

---

## Current Blockers

1. `licitaciones/page.tsx` still queries deprecated view — **Fix in Phase 1.1**
2. RLS not applied in prod — **Fix in Phase 1.2**
3. No alert matching engine — **Build in Phase 2.2**
4. No notification sender — **Build in Phase 2.3**

---

## Pending — Blocked

### Email Notifications (Resend + Custom Domain)
- **Status:** Code complete (`supabase/functions/send-email/index.ts`), deployment blocked.
- **Blocker:** Resend requires a verified custom domain to send emails. The current site runs on `sicop-health-web.vercel.app` which is a free subdomain Resend does not accept as a sender domain.
- **What's needed before unblocking:**
  1. Acquire a custom domain (e.g. `sicop-health.com`)
  2. Verify the domain in Resend dashboard (add DNS records: SPF, DKIM, DMARC)
  3. Update `from` field in `send-email/index.ts` to use verified domain (currently set to `alertas@sicop-health.com`)
  4. Add `RESEND_API_KEY` secret to Supabase Edge Functions
  5. Add `SITE_URL` secret pointing to custom domain
  6. Deploy both edge functions: `notify-new-licitacion` and `send-email`
  7. Create DB Webhook in Supabase: `licitaciones_medicas` INSERT → `notify-new-licitacion`
- **Files ready to deploy:**
  - `supabase/functions/notify-new-licitacion/index.ts`
  - `supabase/functions/send-email/index.ts`
  - `supabase/migrations/005_notificaciones.sql` ← run this first in SQL Editor

---

**Next action:** Pick Phase 1.1 or Phase 1.2 and start immediately.
