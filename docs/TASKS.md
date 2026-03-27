# SICOP-Health — Task Tracker

> Last updated: 2026-03-26
> Status key: `[ ]` pending · `[~]` in progress · `[x]` done · `[-]` blocked · `[?]` needs investigation

---

## Tier 1 — Data (unblocks workflow nodes)

### G1 · Node 6: Line-item quantities + unit prices
> DA Reports 1.1 / 2.1 → new `lineascarteles` table → Node 6 display

- [ ] Confirm exact field names for Reports 1.1 and 2.1 via `SICOP_Exploitable_Data_Reference.md` and live probe
- [ ] Create migration `010_lineascarteles.sql` (`instcartelno`, `linea`, `codigoproducto`, `descripcion`, `cantidad`, `unidad`, `precio_unitario_estimado`, `moneda`)
- [ ] Add `fetch_report` config entries for `SC_L` (1.1) and `DC_L` (2.1) in `datos_abiertos.py`
- [ ] Add `parse_sc_linea_record` and `parse_dc_linea_record` parsers (TDD)
- [ ] Add `upsert_lineascarteles` upserter (TDD)
- [ ] Wire into `run_datos_abiertos` after scalar enrichment
- [ ] Update `types.ts` — add `LineaCartel` type
- [ ] Update Node 6 in `page.tsx` — show line table when data present

### G2 · Node 12: Competitor pricing + price history
> DA Reports 5.1 / 6.2 → populate `precios_historicos` → Node 12 full display

- [ ] Confirm field names for Reports 5.1 (adjudicated lines) and 6.2 (historical prices) via live probe
- [ ] Create migration `011_precios_historicos.sql` (if schema changes needed)
- [ ] Add `fetch_report` config entries for `ADJ_L` (5.1) and `HIST` (6.2)
- [ ] Add `parse_adj_linea_record` and `parse_hist_record` parsers (TDD)
- [ ] Add `upsert_precios_historicos` upserter (TDD)
- [ ] Wire into `run_datos_abiertos`
- [ ] Frontend Node 12: price history table + competitor list from `da_ofertas`
- [ ] Frontend Node 12: query `precios_historicos` for prior awards on same UNSPSC

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
> `test_classifier.py` and `test_parser.py` fail on import; calibrated against v1, classifier is v3.10

- [ ] Audit what changed between classifier v1 and v3.10
- [ ] Rewrite `test_classifier.py` against current `KEYWORDS_*` sets and `clasificar_licitacion` signature
- [ ] Rewrite `test_parser.py` against current `parse_*` field names
- [ ] Rewrite `test_main.py` against current flow (dias_atras, output shape)
- [ ] Rewrite `test_uploader.py` against current field names (`instcartelno` not `numero_procedimiento`)
- [ ] Target: `python -m pytest tests/ -v` → 0 failures

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

- [x] **DA SC report** — `presupuesto_estimado` + `moneda_presupuesto` extracted and patched (4,664 rows) · 2026-03-26
- [x] **DA DC report** — `modalidad_participacion` extracted and patched · 2026-03-26
- [x] **DA O report** — `da_ofertas` table populated (384 rows, 60-day backfill) · 2026-03-26
- [x] **Node 2** unblocked — presupuesto display in detail page · 2026-03-26
- [x] **Node 3** unblocked — modalidad / pre-cal blocked status in detail page · 2026-03-26
- [x] **Migration 009** — `presupuesto_estimado`, `moneda_presupuesto`, `modalidad_participacion` columns + `da_ofertas` table · 2026-03-26
- [x] **12-node workflow UI** — all nodes render with correct status logic · 2026-03-25
- [x] **Institution / category / date filter bar** on licitaciones list · 2026-03-25
- [x] **ETL v2.4** — fetcher, parser, classifier v3.10, uploader v2.9 operational · pre-2026-03-26
