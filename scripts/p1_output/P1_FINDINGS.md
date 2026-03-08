# P1 Validation Results: Datos Abiertos & UNSPSC Discovery

**Date:** 2026-03-08  
**Status:** Complete — documented findings, no blockers for core product

---

## Executive Summary

The datos abiertos module exists and is accessible, but requires browser-based interaction to export data. The REST API line-item endpoints are not directly callable (500 errors), suggesting they need upstream context (like a selected cartel from UI state) that the Angular app provides.

**Bottom line:** The JSP datos abiertos approach is viable but needs Playwright automation. The core product can ship without this — REST API ETL provides sufficient data for MVP.

---

## P1.1: Datos Abiertos JSP Endpoint

### Test Results
| Test | Result | Notes |
|------|--------|-------|
| JSP URL accessibility | ✅ 200 OK | `CE_MOD_DATOSABIERTOSVIEW.jsp` exists |
| Form params with `tipoReporte` | ✅ 200 OK | Returns HTML form page |
| JSON export directly | ❌ Not available | Returns HTML, not JSON |

### Findings
- The endpoint `https://www.sicop.go.cr/moduloPcont/pcont/rp/CE_MOD_DATOSABIERTOSVIEW.jsp` **exists and returns 200**
- Response is an HTML form page (110KB) with JavaScript date validation
- The actual form body appears to be loaded dynamically or via separate include
- Multiple report types supported via `tipoReporte` parameter:
  - `DETALLE_PLIEGO` — Line-item bid details (target for UNSPSC)
  - `PROVEEDORES` — Supplier catalog with cédula jurídica
  - `CONTRATOS` — Contracts
  - `ORDENES` — Purchase orders

### Path Forward
**To extract data from datos abiertos, you need:**
1. **Playwright/Selenium automation** — Navigate the form, fill dates, click export
2. **Export format detection** — The JSP likely generates Excel/PDF or JSON via form submission
3. **Headless scraping** — Run in GitHub Actions with Playwright

**Reference file:** `p1_output/datos_abiertos_response.html` — contains the form page structure with date validation JavaScript

---

## P1.2: Proveedores Catalog

### Test Results
| Test | Result | Notes |
|------|--------|-------|
| `tipoReporte=PROVEEDORES` | ✅ 200 OK | Returns HTML form page |
| JSON export | ❌ Not directly available | Same form structure as detalle pliego |

### Findings
- The proveedores catalog lives in the same datos abiertos module
- The page title confirms: "Compras según tipo de proveedor"
- The supplier data (cédula jurídica, nombre, size classification) is **behind the form**

### Path Forward
Same as P1.1: Requires Playwright form submission to access the export.

**Alternative:** Build supplier normalization incrementally:
1. Extract unique `supplierNm` values from existing `licitaciones_medicas`
2. Parse `detalle` text for supplier names
3. Cross-reference with `supplierCd` (cedula jurídica) when available
4. Build canonical `proveedores` table over time

**This is sufficient for MVP** — exact canonical names can come later.

---

## P1.3: UNSPSC Line-Item Discovery

### Test Results
| Endpoint | Status | Result |
|----------|--------|--------|
| `epCartel/getDetail` | ❌ 500 | Needs additional context |
| `epCartel/lineItems` | ❌ 500 | Needs additional context |
| `epCartel/partidas` | ❌ 500 | Needs additional context |
| JSP detalle pliego | ✅ 200 | HTML form (not JSON) |

### Key Finding: Sample Adjudicada
```
instCartelNo: 2026XE-000054-0000400001
Title: S.E- Contratación Directa de Escasa Cuantía, Adquisición de ...
UNSPSC (cartel level): null
```

This confirms that `unspscCd` is **null at the cartel level** for adjudicadas in the list view.

### Hypothesis: Line-Item Data Lives Elsewhere
The detail endpoints return 500 because they need:
- A session/context from navigating the Angular app
- Additional parameters not in the URL (cartel state from previous selection)
- Authentication that the list endpoints don't require

### Path Forward
**Option A: JSP Datos Abiertos + Playwright (Recommended)**
- Navigate to datos abiertos module
- Filter by institution (CCSS) and procedure type
- Export detalle pliego as JSON
- Extract line-item UNSPSC codes from export

**Option B: Defer until after MVP**
- The classifier.py at 95% accuracy is sufficient for launch
- UNSPSC codes become valuable for price benchmarking (Phase 4)
- Core product doesn't require exact UNSPSC classification

---

## P1.4: Price Bank Catalog (Bonus)

### Test Results
| Payload Structure | Status |
|-------------------|--------|
| Standard `formFilters` | ❌ 500 |
| Direct `dateBefore/dateAfter` | ❌ 500 |
| Minimal pagination | ❌ 500 |
| With `instCartelNo` filter | ❌ 500 |

### Findings
- `priceBankCata/list` consistently returns 500
- The endpoint likely requires **context from the Angular app** (selected procedure, cartel ID from upstream state)
- Not a standalone list endpoint like `listPageRelease`

### Path Forward
**To map this endpoint:**
1. Navigate to `/module/bid/public/price-bank-cata` in browser
2. Open DevTools → Network tab
3. Trigger a search/filter
4. Capture the working request payload
5. Use the Angular chunk search script (Section 18 of API Reference) to find the exact endpoint pattern

---

## Strategic Recommendations

### For Core Product (Ship Now)
The REST API ETL migration (P0) provides everything needed for MVP:
- ✅ ~32K records with hourly updates
- ✅ 95%+ classification accuracy via classifier.py
- ✅ Parsed amounts/suppliers from detalle (95% coverage)
- ✅ Full text search on cartelNm
- ✅ Institution and procedure type filtering

**The datos abiertos deep-dive is P4 material** — valuable for price benchmarking and exact UNSPSC classification, but not required for core product-market fit.

### For P4 (Post-MVP) Data Depth
```
Implementation: Playwright-based datos abiertos scraper
├── Navigate to JSP form
├── Fill date ranges and filters
├── Click export button
├── Parse JSON/Excel export
├── Extract line-item UNSPSC codes
├── Populate precios_historicos table
└── Enable price benchmarking features
```

### Estimated Effort
| Approach | Effort | Output |
|----------|--------|--------|
| Playwright datos abiertos scraper | 1-2 days | Proveedores + UNSPSC line items |
| Wait for SICOP to document API | Unknown | ? |
| Manual CSV download | 30 min/week | Limited scale |

---

## Files Generated

```
scripts/p1_output/
├── datos_abiertos_response.html      # Form page structure
├── proveedores_raw.html              # Proveedores form page
├── detalle_pliego_jsp_*.html         # Detalle pliego sample
├── price_bank_cata_working.json      # (if found)
└── p1_summary.json                    # Structured results
```

---

## Next Actions

1. **For P0 REST Migration** — Proceed with confidence. The core API endpoints work beautifully.

2. **For P4 Data Depth** — When ready, implement Playwright scraper for datos abiertos:
   ```python
   # Example pattern
   with sync_playwright() as p:
       browser = p.chromium.launch()
       page = browser.new_page()
       page.goto("https://www.sicop.go.cr/moduloPcont/pcont/rp/CE_MOD_DATOSABIERTOSVIEW.jsp")
       page.fill("#bgnYmd", "01/01/2026")
       page.fill("#endYmd", "07/03/2026")
       page.select_option("#tipoReporte", "DETALLE_PLIEGO")
       with page.expect_download() as download_info:
           page.click("#btnExportar")
       download = download_info.value
       download.save_as("detalle_pliego.json")
   ```

3. **For Documentation** — Update SICOP_API_Reference_v3.md Section 17 with findings: JSP endpoints work but require browser automation.
