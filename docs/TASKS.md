# SICOP-Health — Task Tracker

> Last updated: 2026-03-27
> Status key: `[ ]` pending · `[~]` in progress · `[x]` done · `[-]` blocked · `[?]` needs investigation

---

## Tier 1 — Data (unblocks workflow nodes)

### G1 · Node 6: Line-item quantities + unit prices
> **BLOCKED at data layer** (2026-03-27): `CE_DA_SC_LINES_CONTROLLER_JSON` returns 404 — no JSON line-item endpoint exists.
> DC report probed: has richer fields (TIPO_PROCEDIMIENTO, FECHA_APERTURA, EXCEPCION_CD, NOMBRE_UNIDAD_COMPRA, FECHA_CIERRE_RECEPCION) but no line-level data.
> No DA controller provides line-item quantities. Node 6 requires an alternative data source.

- [x] Confirm controller map via live JS parse of JSP page — see `memory/reference_da_controllers.md`
- [x] Probe `CE_DA_SC_LINES_CONTROLLER_JSON` — **404, does not exist**
- [x] Inspect full DC JSON record fields — procedure-level only, no line items
- [-] Design `lineas_cartel` table schema — blocked, no data source
- [-] Create migration, parser, upserter, frontend — all blocked
- [?] Alternative: DA C or OP controllers may have line-level data — unprobed

### G2 · Node 12: Competitor pricing + adjudication status
> AF probe complete (2026-03-27). AF report has 3 interleaved schemas in a flat array:
> - HEADER (1529 records): NUMERO_PROCEDIMIENTO + adjudication dates — **joinable, implemented**
> - PARTIDA (90 records): NUMERO_PARTIDA → 30 procedures, CANTIDAD_SOLICITADA appears to be supplier cedula
> - PRICING (151 records): CEDULA_PROVEEDOR + PRECIO_UNITARIO_ADJUDICADO + NRO_ACTO — **NRO_ACTO has no join key to procedures (0 overlap with NRO_SICOP)**
> Competitor pricing per procedure is NOT feasible from AF data. Adjudication dates ARE feasible and implemented.

- [x] Confirm controller name — `CE_DA_AF_CONTROLLER_JSON`
- [x] Probe AF JSON — 1770 records, 3 schemas, PRICING section has no procedure join key
- [x] Migration `010_adjudicaciones_columns.sql` — adds `fecha_adj_firme TIMESTAMPTZ`, `desierto BOOLEAN` to `licitaciones_medicas`
- [x] Add `AF` to `REPORT_CONFIGS` in `datos_abiertos.py`
- [x] Add `parse_af_record` parser (TDD) — parses HEADER schema only, skips PRICING/PARTIDA
- [x] Add `upsert_adjudicaciones` upserter (TDD) — patches licitaciones_medicas on instcartelno
- [x] Wire into `run_datos_abiertos` — stats now include `"adjudicaciones": int`
- [-] `precios_historicos` table — blocked, AF PRICING section has no procedure join key
- [ ] Frontend Node 12: show `fecha_adj_firme` + `desierto` status
- [ ] Frontend Node 12: competitor list from `da_ofertas` (suppliers who bid)
- [?] Alternative pricing source: DA C (contratos) or OP controllers may have awarded amounts per procedure

### G3 · Node 3 coverage gap
> DC report returns `MODALIDAD_PROCEDIMIENTO` for only ~15% of records

- [?] Check if Reports 2 or 3 have better coverage for modalidad
- [?] Confirm whether the 85% NULL is a SICOP data quality issue or a filter/scope issue
- [ ] If better source found: add parser + update `run_datos_abiertos`

---

## Tier 2 — Product (core user workflows)

### G4 · Node 4: User qualification profile
> Needed before Node 4 ("Elegibilidad") can evaluate a specific supplier

- [ ] Design `user_profiles` table schema (`user_id`, `razon_social`, `cedula`, `categorias_autorizadas[]`, `unspsc_autorizados[]`, `registro_sanitario`, `es_precalificado`)
- [ ] Create migration for `user_profiles` (or confirm it's in gamification schema)
- [ ] Build onboarding step 4 (or extend existing 3-step wizard) to capture qualification data
- [ ] Update Node 4 logic in `page.tsx` to compare `licitacion.modalidad_participacion` + `licitacion.unspsc_cd` against user profile
- [ ] Gate Node 4 status: `active` = qualified · `blocked` = pre-cal required · `pendiente` = profile incomplete

### G5 · Notifications not wired
> `notifier.py` has email template + Resend skeleton; WhatsApp is a stub; never called from ETL

- [ ] Add `send_alert_notifications(licitaciones_medicas)` call in `main.py` after upsert
- [ ] Implement `send_whatsapp_notification()` via WhatsApp Business API (or Twilio sandbox)
- [ ] Add `notifier` unit tests (mock Resend + WhatsApp)
- [ ] Verify Resend API key is set in `.env`
- [ ] Test email end-to-end with a real alert config

### G6 · Auth not validated end-to-end
> Routes exist but live Supabase Auth flow not confirmed working

- [ ] Test login → session → dashboard flow against live project
- [ ] Test forgot-password email delivery via Supabase
- [ ] Test invite flow
- [ ] Fix onboarding: replace hardcoded `CATEGORIAS` / `INSTITUCIONES` lists with DB queries
- [ ] Add RLS policy validation (confirm `alertas_config`, `notifications` tables have correct user-scoped policies)

---

## Tier 3 — Quality / Tech debt

### G7 · Stale ETL test suite
> Fixed 2026-03-27. All 85 tests passing (excl. test_fetcher.py which needs `respx`).

- [x] Audit what changed between classifier v1 and v3.12
- [x] Rewrite `test_classifier.py` — fixed `KEYWORDS_MEDICOS` → `KEYWORDS_DIRECTOS_RAW`, fixed 3 broken assertions (19 tests)
- [x] Rewrite `test_parser.py` — removed pandas-dependent legacy tests, 13 new `parse_batch` tests against current schema
- [x] Rewrite `test_main.py` — fixed `dias_atras` default, added `run_datos_abiertos` mock (8 tests)
- [x] Rewrite `test_uploader.py` — fixed `on_conflict` key, mock chain, error-swallowing, env var message (15 tests)
- [x] `conftest.py` — added stubs for `supabase`, `pandas`, `dotenv` (not installed in test env)
- [x] Target: `python3 -m pytest tests/ -v` → **85/85 passing**

### G8 · Node 7: use `presupuesto_estimado` over `monto_colones`
> WhatsApp spec sheet currently uses `monto_colones` (awarded amount, post-adjudication)
> `presupuesto_estimado` (from DA) is the right figure at offer time

- [ ] Update `WhatsAppButton.tsx` to prefer `presupuesto_estimado` + `moneda_presupuesto` when available
- [ ] Remove inline warning comment about `monto_colones` not being available

### G9 · Historical price data 2000–2024
> Referenced in docs as a PDF source; extraction method unknown

- [?] Investigate whether SICOP JSP layer exposes pre-2024 historical prices via a report endpoint
- [?] If PDF-only: evaluate cost/effort of PDF extraction pipeline
- [ ] Decision needed before implementation

### G10 · Gamification tables not populated
> `user_profiles`, `user_activity`, `user_badges` tables exist; dashboard renders defaults for all users

- [ ] Wire `user_activity` insert on licitación page view (server action or API route)
- [ ] Wire `user_activity` insert on alert creation
- [ ] Add `IntelScore` calculation logic (define scoring formula)
- [ ] Add streak calculation (query consecutive activity days)
- [ ] Seed initial badge definitions into DB
- [ ] Wire badge award on first view, first alert, first week streak

---

## Completed

- [x] **G7 stale tests** — 85/85 passing; conftest stubs supabase/pandas/dotenv · 2026-03-27
- [x] **G2 partial — AF adjudication dates** — `fecha_adj_firme` + `desierto` on `licitaciones_medicas`; migration 010 · 2026-03-27
- [x] **G1 probe** — SC_LINES_JSON 404 (no JSON line-item endpoint); DC fields mapped (procedure-level only) · 2026-03-27
- [x] **DA SC report** — `presupuesto_estimado` + `moneda_presupuesto` extracted and patched (4,664 rows) · 2026-03-26
- [x] **DA DC report** — `modalidad_participacion` extracted and patched · 2026-03-26
- [x] **DA O report** — `da_ofertas` table populated (384 rows, 60-day backfill) · 2026-03-26
- [x] **Node 2** unblocked — presupuesto display in detail page · 2026-03-26
- [x] **Node 3** unblocked — modalidad / pre-cal blocked status in detail page · 2026-03-26
- [x] **Migration 009** — `presupuesto_estimado`, `moneda_presupuesto`, `modalidad_participacion` columns + `da_ofertas` table · 2026-03-26
- [x] **12-node workflow UI** — all nodes render with correct status logic · 2026-03-25
- [x] **Institution / category / date filter bar** on licitaciones list · 2026-03-25
- [x] **ETL v2.4** — fetcher, parser, classifier v3.10, uploader v2.9 operational · pre-2026-03-26
