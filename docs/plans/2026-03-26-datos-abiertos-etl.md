# Datos Abiertos ETL — Implementation Record

> **Status: COMPLETE** · Executed 2026-03-26 / 2026-03-27
> Branch: `feat/datos-abiertos-etl` (not yet merged to main)

---

## What was built

New `datos_abiertos.py` module in `services/etl/` wires the SICOP JSP servlet download layer into the hourly ETL pipeline, running after the existing REST phase.

### Files created / modified

| File | Change |
|------|--------|
| `supabase/migrations/009_datos_abiertos.sql` | New: `presupuesto_estimado`, `moneda_presupuesto`, `modalidad_participacion` on `licitaciones_medicas`; `da_ofertas` table |
| `services/etl/datos_abiertos.py` | New: download engine, SC/DC/O parsers, scalar + oferta upserters, `run_datos_abiertos` orchestrator |
| `services/etl/tests/test_datos_abiertos.py` | New: 20 unit tests — all passing |
| `services/etl/main.py` | Modified: `run_datos_abiertos` called after REST phase (non-fatal try/except) |
| `apps/web/src/lib/types.ts` | Modified: added `presupuesto_estimado`, `moneda_presupuesto`, `modalidad_participacion` to `Licitacion` |
| `apps/web/src/app/licitaciones/[id]/page.tsx` | Modified: Node 2 + Node 3 unblocked; `completedNodes` updated |

### Backfill results (60-day window, 2026-03-27)

```
DA scalar:  4,664 rows patched (presupuesto + modalidad on licitaciones_medicas)
DA ofertas: 384 rows upserted (da_ofertas, FK-filtered to tracked procedures)
```

---

## Confirmed API facts

**Servlet base:** `https://www.sicop.go.cr/moduloPcont/servlet/cont/rp`

**Two-step download protocol:**
1. `POST {base}/{controller}.java` · form params: `{date_from}=DDMMYYYY`, `{date_to}=DDMMYYYY`, `{inst_cd}=CEDULA`, `{inst_nm}=`, `cmd=create`
2. Response body = plain-text ZIP filename token
3. `GET {base}/{controller}.java?cmd=download&fileZipName={token}` → ZIP with one JSON file (direct array)

**Date format:** `DDMMYYYY` (e.g. `01032026`)
**Max date range:** 183 days (SICOP JS validation)
**Empty `inst_cd`** = all institutions
**CCSS cédula in DA:** `4000042147` (≠ REST API `0031700001`)

### Confirmed controllers (all 11 — from live JS parse 2026-03-27)

| Key | Controller | ETL status |
|-----|-----------|------------|
| SC | `CE_DA_SC_CONTROLLER_JSON` | ✅ implemented |
| DC | `CE_DA_DC_CONTROLLER_JSON` | ✅ implemented |
| O  | `CE_DA_O_CONTROLLER_JSON`  | ✅ implemented |
| AF | `CE_DA_AF_CONTROLLER_JSON` | planned (G2 — adjudicaciones en firme) |
| C  | `CE_DA_C_CONTROLLER_JSON`  | not yet |
| OP | `CE_DA_OP_CONTROLLER_JSON` | not yet |
| A  | `CE_DA_A_CONTROLLER_JSON`  | not yet |
| R  | `CE_DA_R_CONTROLLER_JSON`  | not yet |
| IC | `CE_DA_IC_CONTROLLER_JSON` | not yet (no date range — inst + geo filter only) |
| P  | `CE_DA_P_CONTROLLER_JSON`  | not yet (no date/inst — size filter only) |
| CB | `CE_DA_CB_CONTROLLER_JSON` | not yet (no date/inst — category filter only) |

---

## Mid-execution discoveries

### ⚠️ "Reports 1.1 / 2.1" do not exist as servlet endpoints

The original plan referenced "Report 1.1 — Solicitudes Líneas" and "Report 2.1 — DC Líneas" as distinct download targets. After probing the live JSP JavaScript (2026-03-27), these labels were confirmed to be **sections of the data dictionary PDF**, not separate servlet controllers. Only the 11 controllers above exist on the download page.

Consequence: G1 (Node 6 line items) cannot use a non-existent `CE_DA_SC_LINES_CONTROLLER_JSON` without first probing whether it exists. See `docs/TASKS.md` G1 for the updated investigation tasks.

### SC lines anomaly

SC's CSV controller is `CE_DA_SC_LINES_CONTROLLER.java` (not `CE_DA_SC_CONTROLLER_CSV.java` like all others). This suggests a separate lines variant may exist. A JSON version is **unconfirmed** — must probe before using.

### O report fixes required

Two bugs surfaced during backfill that were fixed before merging:

1. **Duplicate composite key**: O report returned duplicate `(instcartelno, suppliercd)` pairs in the same batch. Fix: `seen: dict[tuple, dict]` dedup before upsert.
2. **FK violation**: O report fetches all institutions, returning many `instcartelno` values not in `licitaciones_medicas`. Fix: query `known_set` before filtering.

---

## What remains open

See `docs/TASKS.md` for the full gap list. Key items spawned by this plan:

- **G1** — Node 6 line items: probe `CE_DA_SC_LINES_CONTROLLER_JSON` and full DC JSON fields before implementing
- **G2** — Node 12 competitor pricing: probe `CE_DA_AF_CONTROLLER_JSON` field names, then implement `parse_af_record` + `upsert_precios_historicos`
- **G3** — `MODALIDAD_PROCEDIMIENTO` coverage gap (~85% NULL) — may be a SICOP data quality issue
- **Branch merge** — `feat/datos-abiertos-etl` not yet merged to `main`
