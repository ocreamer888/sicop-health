# SICOP Health Intelligence — Strategic Task List
_Last updated: 2026-03-07_

---

# SHIP MVP — Active Sprint (NOW)

**Goal:** Get the product in users' hands immediately. Cut scope to what works today.

**Definition of Done:**
- User can sign up, log in, see medical bids
- User can browse/search licitaciones
- User gets notifications for new medical bids (in-app)
- ETL runs hourly fetching new data

### Ship Checklist
- [x] **REST API ETL is working** (`fetcher.py` uses REST endpoints)
- [ ] **24-hour incremental fetch configured** (not 90-day every run)
- [ ] **90-day backfill completed** (~32K medical bids in DB)
- [ ] **Authentication working** (signup/login/logout)
- [ ] **Licitaciones page loads** with real data
- [ ] **Alertas page shows notifications**
- [ ] **Parse confidence UI** for amounts (HIGH/LOW/NONE)
- [ ] **First admin user created**
- [ ] **Hourly GitHub Actions running**
- [ ] **Smoke test passed** (end-to-end flow)

**Post-Ship (P2):** Email notifications, WhatsApp, advanced filters, analytics dashboard

---

## P0: REST API Migration — The Massive Unlock

**Context:** REST API discovery eliminates CSV download flow entirely. This is a **foundational change** that unlocks everything else. Must complete before any other work.

### ETL Architecture Rewrite
- [ ] **Rewrite `fetcher.py` to use REST API endpoints**
  - Target: `listPageRelease`, `listPageAwarded`, `listPageModified`
  - Implement pagination through `totalPages`
  - Use `formFilters` wrapper with ISO 8601 dates
  - **Deliverable:** `services/etl/fetcher.py` v2.0 with REST calls

- [ ] **Eliminate `parser.py` entirely**
  - REST returns clean JSON — no CSV encoding bugs, no pandas
  - Move `detalle` regex (amount/supplier parsing) to thin `extractor.py` or `uploader.py`
  - Delete `parser.py` v2.1 and all CSV parsing logic
  - **Deliverable:** 50% code reduction, no pandas dependency

- [ ] **Implement 24-hour incremental fetch**
  - `bgnYmd = NOW() - INTERVAL '24 hours'` as default
  - Keep `--backfill` flag for 90-day initial load
  - **Deliverable:** ~95% reduction in fetch time (42s → 3s)

- [ ] **Test source-side filtering in `formFilters`**
  - Try passing `proceType`, `instCd` to reduce data volume
  - If supported: fetch only medical bids, eliminate post-fetch filter
  - **Deliverable:** Document which filters work

### Data Schema Updates (Post-REST)
- [ ] **Add new API fields to schema**
  - `cartelcate` (Bienes/Servicios/Obras)
  - `excepcioncd` (BD105 exception codes)
  - `modreason` (modification reason text)
  - `vigenciacontrato` + `unidadvigencia`
  - **Deliverable:** Migration to add REST-only fields

- [ ] **Add parse_confidence column**
  - Migration: `ALTER TABLE licitaciones_medicas ADD COLUMN parse_confidence TEXT CHECK (parse_confidence IN ('NONE', 'LOW', 'HIGH'))`
  - Logic: NONE = no monto AND no supplier, LOW = partial, HIGH = both present
  - **Deliverable:** Schema supports confidence scoring for detalle parsing

---

## P1: Validation & Deep Data — COMPLETE ✅

**Status:** Documented 2026-03-08. Not blockers for core product. Full findings in `scripts/p1_output/P1_FINDINGS.md`.

### Summary
| Task | Status | Finding |
|------|--------|---------|
| JSP endpoint test | ✅ | `CE_MOD_DATOSABIERTOSVIEW.jsp` works (200 OK) but returns HTML form, not JSON directly |
| Proveedores catalog | ✅ | Accessible via JSP but requires Playwright form submission to export |
| UNSPSC line items | ✅ | Detail endpoints (lineItems, partidas) return 500 — need Angular app context |

### Key Finding
The datos abiertos module **is viable** but requires browser automation (Playwright/Selenium) to:
1. Navigate the JSP form
2. Fill date ranges and filters  
3. Click export button
4. Parse JSON/Excel export

**This is P4 work** — valuable for price benchmarking and exact UNSPSC classification, but not required for core product MVP. The REST API ETL (P0) provides sufficient data (~32K records, 95% classifier accuracy).

### Path Forward (When Ready for P4)
```python
# Playwright pattern for datos abiertos
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto(JSP_URL)
    page.fill("#bgnYmd", "01/01/2026")
    page.fill("#endYmd", "07/03/2026")
    page.select_option("#tipoReporte", "DETALLE_PLIEGO")
    # ... trigger export and parse
```

**Alternative for MVP:** Build supplier normalization incrementally from existing `licitaciones_medicas` data via `supplierNm` + `supplierCd` parsing.

---

## P2: Frontend Features (Blocked until REST migration stable)

**Context:** UI work that becomes possible/trivial once REST ETL is running.

### UI Enhancements
- [ ] **Update UI to surface parse confidence**
  - HIGH: Show formatted amount and supplier normally
  - LOW/NONE: Show "Monto no disponible" + raw detalle excerpt + "Ver en SICOP" link
  - **Deliverable:** Honest data presentation, keep users in-app

- [ ] **Real pagination on licitaciones table**
  - Use `totalElements`, `totalPages` from API response
  - Add page controls with actual page numbers
  - **Deliverable:** Browse 32K+ records efficiently

- [ ] **Procedure type filter dropdown**
  - Source from BD103 codes: LY, LE, LD, PX, SE, RE
  - Full text labels: "LICITACIÓN MAYOR", "LICITACIÓN REDUCIDA"
  - **Deliverable:** Filter by procedure type in UI

- [ ] **Dashboard stats from `getGeneralReport`**
  - Call `epCartel/getGeneralReport` for SICOP-wide summary
  - Display total published/adjudicated counts
  - **Deliverable:** Real summary stats card on dashboard

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
- [x] **Migrate `licitaciones/page.tsx` from view to direct table query**
  - Changed from `licitaciones_activas` to `licitaciones_medicas`
  - Added filters: `es_medica = true`, `categoria IS NOT NULL`
  - Kept same columns for `LicitacionPreview` compatibility
  - **Status:** Complete — `apps/web/src/app/licitaciones/page.tsx` queries table directly

- [x] **Run 90-day backfill**
  - Execute: `cd services/etl && python main.py --dias 90`
  - Validate row counts in Supabase dashboard
  - **Deliverable:** 500+ licitaciones in DB with full history

### 1.2 Apply RLS in Production
- [x] **Execute migration 004_rls.sql in Supabase Dashboard**
  - Navigate to SQL Editor → New query
  - Paste contents of `supabase/migrations/004_rls.sql`
  - Run and verify no errors
  - **Test:** Try accessing data without auth (should fail)

- [x] **Create first admin user**
  - Supabase Dashboard → Authentication → Users → Add user
  - Set email/password for initial access
  - **Deliverable:** Can log in to /dashboard with real credentials

---

## Phase 2: Core Value — Alert System (Weeks 2-3)

**Goal:** Working alert creation → matching → notification flow. This is the product.

### 2.1 Notification Inbox UI (`/alertas`) — IMPLEMENTED
- [x] **Create alertas page scaffold**
  - Route: `/alertas/page.tsx` — Shows notification inbox, not alert config
  - Protected route (inherits middleware)
  - Layout matches design system

- [x] **Build notifications list view**
  - Shows new medical licitaciones from last 30 days
  - Links to detail pages
  - Empty state when no new notifications

- [x] **Create `notificaciones` table (migration 005)**
  - One row per new licitacion detected by webhook
  - Prevents duplicate notifications (UNIQUE on instcartelno)
  - RLS: authenticated users can read all


### 2.3 Notification Engine (Broadcast Pattern) — CODE COMPLETE
- [x] **Create edge function: `notify-new-licitacion`**
  - Triggered by DB webhook on `licitaciones_medicas` INSERT
  - Sends notification to ALL authenticated users (broadcast pattern)
  - Calls `send-email` edge function for each user
  - Prevents duplicates via `notificaciones` table

- [ ] **Integrate into ETL**
  - DB Webhook: `licitaciones_medicas` INSERT → `notify-new-licitacion`
  - Currently not deployed — pending email domain verification

### 2.3 Email Notifications (Resend) PENDING
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

| Phase | Criteria | Status |
|-------|----------|--------|
| **1** | Can log in, see 500+ licitaciones, navigate detail pages without errors | In progress — 1.1 complete, 1.2 pending |
| **2** | New medical licitacion triggers in-app notification for all users (broadcast pattern). Email notification pending domain. | Partial — Code complete, deployment blocked |
| **2b** | (Future) Create personalized alert with "insulina", only matching licitaciones trigger notification | Not started — requires alert matching engine |
| **3** | Dashboard shows personalized recommendations, can export to Excel | Not started |
| **4** | 3+ paying customers, expansion to Guatemala scoped | Not started |

---

## Current Blockers

1. ~~`licitaciones/page.tsx` still queries deprecated view~~ — **FIXED** ✅
2. RLS not applied in prod — **Run `004_rls.sql` in Supabase SQL Editor**
3. No 90-day backfill — **Run `cd services/etl && python main.py --dias 90`**
4. Email notifications blocked — **Need verified custom domain (see Pending section)**
5. No first admin user — **Create in Supabase Auth Dashboard**

---

## Pending — Blocked

### Email Notifications (Resend + Custom Domain)
- **Status:** Code complete (`supabase/functions/send-email/index.ts`), deployment blocked by domain verification.
- **Blocker:** Resend requires a verified custom domain to send emails. Free subdomains (`*.vercel.app`) are not accepted.
- **Options to unblock:**
  | Option | Effort | Notes |
  |--------|--------|-------|
  | 1. Acquire custom domain | Medium | Buy `sicop-health.com`, verify in Resend, add DNS records (SPF, DKIM, DMARC) |
  | 2. Switch provider | Low-Medium | SendGrid, Postmark, or AWS SES may allow unverified domains with limits |
  | 3. Defer email | Zero | Keep in-app notifications only; email later when domain acquired |
- **If proceeding with Option 1 (custom domain):**
  1. Acquire domain (e.g. `sicop-health.com`)
  2. Verify in Resend dashboard → add DNS records
  3. Update `from` field in `send-email/index.ts` (currently `alertas@sicop-health.com`)
  4. Add `RESEND_API_KEY` secret to Supabase Edge Functions
  5. Add `SITE_URL` secret pointing to custom domain
  6. Deploy: `notify-new-licitacion` and `send-email`
  7. Create DB Webhook: `licitaciones_medicas` INSERT → `notify-new-licitacion`
- **Files ready to deploy:**
  - `supabase/functions/notify-new-licitacion/index.ts`
  - `supabase/functions/send-email/index.ts`
  - `supabase/migrations/005_notificaciones.sql` ← run first in SQL Editor

---

**Next action:** Pick Phase 1.1 or Phase 1.2 and start immediately.
