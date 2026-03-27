# SICOP Public REST API -- Exhaustive Reference v3
**Reverse-engineered via browser DevTools, March 7, 2026**
**Project:** sicop-health | github.com/ocreamer888/sicop-health
**API Host:** prod-api.sicop.go.cr | **SPA:** www.sicop.go.cr/app

---

## 1. Infrastructure

| Property | Value |
|---|---|
| API Host | prod-api.sicop.go.cr |
| Web SPA | www.sicop.go.cr/app |
| Remote IP | 159.60.157.204:443 |
| Protocol | HTTPS only |
| Auth | None -- all listed endpoints are fully public |
| CORS | Open -- callable from browser or server |
| Framework | Angular (polyfills-KS6J6CYI.js, lazy-loaded chunks) |
| API versioning | /api/v1/ on all routes |

### Microservice Prefixes
```
https://prod-api.sicop.go.cr/bid/api/v1/public/    <- Licitaciones / carteles
https://prod-api.sicop.go.cr/comn/api/v1/public/   <- Common catalog / code tables
https://prod-api.sicop.go.cr/epum/api/v1/public/   <- UI menus / suppliers
```

---

## 2. All Endpoints

### 2.1 bid module -- Core ETL

#### POST /bid/api/v1/public/epCartelReleaseAdjuMod/listPageRelease
- **Purpose:** Licitaciones PUBLICADAS
- **typeKey:** RPT_PUB
- **Volume (90d):** ~3,425-4,407 records
- **Status:** OK 200 confirmed in production
- **Angular route:** /module/bid/public/contests-published-awarded

#### POST /bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded
- **Purpose:** Licitaciones ADJUDICADAS
- **typeKey:** RPT_ADJ
- **Volume (90d):** ~16,428 records
- **Status:** OK 200 confirmed in production
- **Angular route:** /module/bid/public/contests-published-awarded

#### POST /bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified
- **Purpose:** Licitaciones MODIFICADAS
- **typeKey:** RPT_MOD
- **Volume (90d):** ~11,549 records
- **Status:** OK 200 confirmed in production
- **Angular route:** /module/bid/public/contests-published-awarded
- **WARNING:** Same instCartelNo repeats -- one row per modification event. NEVER upsert. Always INSERT into licitacionesmodificaciones.

#### POST /bid/api/v1/public/epCartel/getGeneralReport
- **Purpose:** Dashboard summary stats -- SICOP-wide totals
- **Status:** OK 200 confirmed
- **Required params:** dateBefore, dateAfter (NOT in formFilters -- direct body fields)
- **Angular route:** /module/bid/public/general-report

#### POST /bid/api/v1/public/priceBankCata/list
- **Purpose:** Price bank catalog (precioshistoricos via REST)
- **Status:** 500 INTERNAL_SERVER_ERROR -- correct params unknown
- **Angular route:** /module/bid/public/price-bank-cata
- **Next step:** Navigate to page, capture working payload from DevTools

#### POST /bid/api/v1/public/contestsPublishedAwarded/list
- **Purpose:** Possibly combined published+awarded in one call
- **Status:** 500 INTERNAL_SERVER_ERROR -- params unknown

---

### 2.2 epum module -- Suppliers / UI

#### POST /epum/api/v1/public/sanctionedSuppliers/list
- **Purpose:** Blacklisted / sanctioned suppliers
- **Status:** 500 INTERNAL_SERVER_ERROR -- params unknown
- **Next step:** Navigate to /module/epum/public/sanctioned-suppliers, capture payload

#### POST /epum/api/v1/public/ptMenu/getHeader
- **Purpose:** Page header navigation (UI only -- ignore for ETL)
- **Status:** OK 200

#### POST /epum/api/v1/public/ptMenu/getUserActionMenu
- **Purpose:** User action nav menu (UI only -- ignore for ETL)
- **Status:** OK 200

---

### 2.3 comn module -- Catalog Code Tables

#### GET /comn/api/v1/public/coCommonCd/list/{CODE}
- **Purpose:** Returns array of options for each code class
- **Status:** OK 200 on all tested codes
- **Response format:** Array of `{ cdCls, cd, cdNmEs, cdNm2Es, cdOrd }`

#### POST /comn/api/v1/public/comnMlangTransinfo/list
- **Purpose:** UI translation strings (ignore for ETL)
- **Status:** OK 200

---

## 3. Angular Page to Endpoint Map

| Angular Route | Endpoints Called | Status |
|---|---|---|
| /module/bid/public/intro-reports | (landing only -- no data calls) | N/A |
| /module/bid/public/contests-published-awarded | listPageRelease + listPageAwarded + listPageModified + BD104 | Fully mapped |
| /module/bid/public/general-report | epCartel/getGeneralReport | Mapped |
| /module/bid/public/price-bank-cata | priceBankCata/list | 500 |
| /module/epum/public/sanctioned-suppliers | sanctionedSuppliers/list | 500 |
| /module/bid/public/participation-history | Unknown | Not mapped |
| /module/bid/public/awarded-proc-supplier | Unknown | Not mapped |
| Every page (init) | comnMlangTransinfo/list + ptMenu/getHeader + ptMenu/getUserActionMenu | OK |

---

## 4. Request Body Format

### 4.1 listPage* endpoints (Release / Awarded / Modified)

CRITICAL: flat body like `{"bgnYmd":"20260101"}` always returns 400.
Must use the `formFilters` wrapper:

```json
{
  "pageNumber": 0,
  "pageSize": 100,
  "tableSorter": { "sorter": "", "order": "desc" },
  "tableFilters": [],
  "formFilters": [
    { "field": "bgnYmd", "value": "2026-01-01T00:00:00.000Z" },
    { "field": "endYmd", "value": "2026-03-07T23:59:59.999Z" },
    { "field": "typeKey", "value": "RPT_PUB" }
  ]
}
```

Rules:
- `bgnYmd` / `endYmd`: ISO 8601 with Z suffix. Python: `fecha.strftime("%Y-%m-%dT%H:%M:%S.000Z")`
- `typeKey`: RPT_PUB | RPT_ADJ | RPT_MOD
- `pageNumber`: 0-indexed
- `pageSize`: 100 recommended (max tested)
- `instNm` in formFilters: **IGNORED BY API** -- always returns full dataset. Filter post-fetch in Python.
- `tableFilters`: always empty array `[]`

### 4.2 getGeneralReport

```json
{ "dateBefore": "2026-01-01", "dateAfter": "2026-03-07" }
```

Direct fields, NOT formFilters wrapper. Date format YYYY-MM-DD (no time).

---

## 5. Response Envelope

```json
{
  "content": [ /* bid records array */ ],
  "pageable": {
    "pageNumber": 0, "pageSize": 100,
    "sort": { "sorted": true, "unsorted": false, "empty": false },
    "offset": 0, "paged": true, "unpaged": false
  },
  "totalPages": 1643,
  "totalElements": 16428,
  "last": false, "numberOfElements": 100, "size": 100,
  "number": 0, "first": true, "empty": false
}
```

Pagination: `for page in range(0, response["totalPages"])`

---

## 6. Complete Field Reference -- content[] records

Every field observed across all three endpoints. Confirmed from real production responses.

| API camelCase | Parser snake_case | DB column | Type | RPT_PUB | RPT_ADJ | RPT_MOD | Notes |
|---|---|---|---|---|---|---|---|
| instCartelNo | instcartelno | instcartelno | TEXT | Y | Y | Y (repeats) | UNIQUE KEY. Format: 2026LD-000001-0031700001 |
| cartelNo | cartelno | cartelno | TEXT | Y | Y | Y | Sequential: "20260300369" |
| proceType | procetype | procetype | TEXT | Y | Y | Y | Full name: "LICITACION REDUCIDA", "PROCEDIMIENTOS ESPECIALES" |
| instNm | instnm | instnm | TEXT | Y | Y | Y | Full institution name |
| cartelNm | cartelnm | cartelnm | TEXT | Y | Y | Y | Bid title -- primary classifier input |
| openbidDt | openbiddt | openbiddt | TIMESTAMPTZ | Y | Y | Y | Offer opening datetime. ISO no-Z: "2026-03-16T10:01:00" |
| biddocStartDt | biddocstartdt | biddocstartdt | TIMESTAMPTZ | Y | Y | Y | Publication/start datetime |
| biddocEndDt | biddocenddt | biddocenddt | TIMESTAMPTZ | Y | Y | Y | Offer deadline -- use for licitacionesporvencer view |
| cartelCate | cartelcate | cartelcate | TEXT | null | "1" | null | Only "1" on RPT_ADJ |
| supplierNm | suppliernm | suppliernm | TEXT | null | sometimes | null | Winner name (often null on RPT_ADJ -- parse from detalle) |
| supplierCd | suppliercd | suppliercd | TEXT | null | Y | null | Supplier cedula juridica |
| currencyType | currencytype | currencytype | TEXT | null | null/Y | null | Often null even on RPT_ADJ -- parse from detalle |
| amt | amt | montocolones | NUMERIC | null | null | null | ALWAYS null -- parse from detalle via regex |
| detalle | detalle | detalle | TEXT | null | Y | null | "Se adjudica LMG LANCO MEDICAL GROUP por un monto de USD 9,792" |
| modReason | modreason | modreason | TEXT | null | null | Y | "Se realiza modificacion en: Fecha/hora de apertura de ofertas" |
| modalidad | modalidad | modalidad | TEXT | Y | Y | Y | Licitacion publica vs directa |
| excepcionCd | excepcioncd | excepcioncd | TEXT | sometimes | sometimes | sometimes | Art. 55/60/66 LGCP code (BD105 catalog) |
| unspscCd | unspsccd | unspsccd | TEXT | sometimes | sometimes | null | 8-digit UNSPSC family code. Primary classification signal |
| adjFirmeDt | adjfirmedt | adjfirmedt | TIMESTAMPTZ | null | Y | null | Firmeza de adjudicacion datetime |
| vigenciaContrato | vigenciacontrato | vigenciacontrato | TEXT | sometimes | sometimes | null | Contract duration value |
| unidadVigencia | unidadvigencia | unidadvigencia | TEXT | sometimes | sometimes | null | Duration unit: "MESES", "ANOS" |

### Derived / Computed Fields (generated by parser.py, not in API)

| Field | DB column | Source | Method |
|---|---|---|---|
| tipoprocedimiento | tipoprocedimiento | instCartelNo prefix | regex `r'^\d{4}([A-Z]{2})-'` |
| instcode | instcode | instCartelNo suffix | `instcartelno.split('-')[-1]` |
| amt (parsed) | montocolones | detalle text | MONTO_PATTERN regex |
| currencytype (parsed) | currencytype | detalle text | MONTO_PATTERN regex |
| adjudicatario (parsed) | adjudicatario | detalle text | "Se adjudica X por un monto de" |
| clasificacionunspsc | clasificacionunspsc | unspscCd | alias for legacy CSV compat |
| esmedica | esmedica | cartelnm + instnm | classifier.py v3.10 |
| categoria | categoria | cartelnm keywords | classifier.py v3.10 |
| estado | estado | typekey | RPT_PUB->Publicado, RPT_ADJ->Adjudicado, RPT_MOD->Modificado |
| numeroprocedimiento | numeroprocedimiento | instCartelNo | alias for legacy view compat |
| descripcion | descripcion | cartelnm | alias for legacy view compat |
| institucion | institucion | instnm | alias for legacy view compat |
| adjudicatario | adjudicatario | suppliernm | alias for legacy view compat |
| fechatramite | fechatramite | biddocstartdt | alias for legacy view compat |
| fechalimiteoferta | fechalimiteoferta | biddocenddt | alias for legacy view compat |

---

## 7. tipoprocedimiento -- instCartelNo Prefix Codes

| Prefix | Label (BD103) |
|---|---|
| LD | Licitacion Reducida (Directa) |
| LY | Licitacion Mayor |
| LE | Licitacion Menor / Especial |
| XE | Contratacion por Excepcion (Art. 66 LGCP) |
| PX | Procedimiento Menor |
| PE | Procedimientos Especiales |
| SE | Subasta Inversa Electronica |
| RE | Remate |

```python
import re
TIPO_PROC_RE = re.compile(r'^\d{4}([A-Z]{2})-')
# 2026LD-000001-0031700001 -> 'LD'
# 2026XE-000025-0001101142 -> 'XE'  (CCSS Art.66 urgente)
# 2026PX-000018-0018000001 -> 'PX'
tipoprocedimiento = TIPO_PROC_RE.match(instcartelno).group(1)

# instcode = institution segment
# 2026LD-000001-0031700001 -> '0031700001'
# CCSS codes match: r'000115\d{4}' or r'0001101\d{3}'
instcode = instcartelno.split('-')[-1] if instcartelno else None
```

---

## 8. Amount Extraction (detalle regex)

amt is **always null** in the API response. Real data examples from production:

```
Se adjudica LMG LANCO MEDICAL GROUP por un monto de USD 9792
Se adjudica PAVILOS Y CORDELES HERCULES LIMITADA por un monto de USD 296100
Se adjudica PROYECTOS DE INGENIERIA Y SUMINISTRO por un monto de USD 8595.91
Se adjudica SERVICIO DE LIMPIEZA A SU MEDIDA por un monto de CRC 63802.4781
Se adjudica ASOCIACION INSTITUTO por un monto de CRC 23045643.75
Se adjudica JOZABAD AARON VARGAS MORA por un monto de CRC 497305.2369
Se adjudica EVERLLENCE PANAMA INC por un monto de USD 115109.94
Se adjudica CARAVANA INTERNACIONAL por un monto de CRC 3710110
```

Format variations observed:
- `USD 9792` -- no decimals, no thousands sep
- `USD 8595.91` -- dot decimal
- `CRC 1.577.215,92` -- CR format: dots=thousands, comma=decimal
- `CRC 63802.4781` -- dot decimal only
- `USD 135.00` -- no space after currency code (edge case)
- `CRC 290,000,000.04` -- comma thousands
- `$95,500` -- dollar sign without code

```python
import re

MONTO_PATTERN = re.compile(
    r'(?:monto\s+de|total\s+de|por\s+un\s+monto\s+de)?\s*'
    r'(?P<currency>USD|CRC|EUR)\s*'
    r'(?P<amount>[\d,\.]+)',
    re.IGNORECASE
)

CURRENCY_MAP = {'CRC': 'CRC', 'USD': 'USD', '$': 'USD', 'EUR': 'EUR'}

def parse_amount_str(s: str, currency: str) -> float | None:
    # CR format: ends in ,XX with dots as thousands (1.577.215,92)
    if re.search(r',\d{2}$', s) and '.' in s:
        s = s.replace('.', '').replace(',', '.')
    # INT format: comma as thousands (9,792.00)
    elif re.search(r'\.\d{2}$', s) and ',' in s:
        s = s.replace(',', '')
    else:
        s = s.replace(',', '')
    try: return float(s)
    except ValueError: return None

def extract_monto_detalle(detalle):
    if not detalle: return None, None
    best_monto, best_currency = None, None
    for match in MONTO_PATTERN.finditer(detalle):
        currency = CURRENCY_MAP.get(match.group('currency').upper(), match.group('currency').upper())
        monto = parse_amount_str(match.group('amount'), currency)
        if monto is not None and (best_monto is None or monto > best_monto):
            best_monto, best_currency = monto, currency
    return best_monto, best_currency

# CRITICAL -- always use 'is not None', never 'or':
# WRONG: currencytype = currency or item.get('currencyType')  (0.0 falls through)
# RIGHT: currencytype = currency if currency is not None else item.get('currencyType')
```

---

## 9. Code Catalog (BD tables) -- Full Values

### BD101 -- Document Types
| cd | cdNmEs |
|---|---|
| T001 | Oferta |
| T002 | Subsanacion oferta de parte |
| T003 | Subsanacion oferta de oficio |
| T004 | Solicitud de informacion etapa contractual |
| T008 | Invitacion a proveedores |
| T009 | Solicitud de Contratacion |
| T010 | Pliego de condiciones |
| T012 | Anuncios |
| T013 | Aclaracion al pliego de condiciones |
| T014 | Recursos |
| T017 | Modificacion de presupuesto (pliego de condiciones) |
| T018 | Solicitud de oferta economica (Modalidad por etapas) |
| T023 | Resultado final del estudio de las ofertas |
| T024 | Mejora de precio |
| T025 | Prorroga del acto final |
| T026 | Subasta Electronica |
| T027 | Acto final (Adjudicacion) |
| T028 | Declaracion infructuoso/desierto |

### BD103 -- Procedure Type Codes
| cd | cdNmEs | cdOrd |
|---|---|---|
| LY | LICITACION MAYOR | 10 |
| LE | LICITACION MENOR | 11 |
| PE | PROCEDIMIENTOS ESPECIALES | 11 |
| LD | LICITACION REDUCIDA | 12 |
| SE | SUBASTA INVERSA ELECTRONICA | 14 |
| RE | REMATE | 14 |
| PX | PROCEDIMIENTO POR EXCEPCION | 15 |

### BD104 -- Report Type Keys
| cd | cdNmEs |
|---|---|
| RPT_PUB | Pliego de condiciones publicados |
| RPT_ADJ | Pliego de condiciones adjudicados |
| RPT_MOD | Pliego de condiciones modificados |

### BD105 -- Exception Procedure Codes (excepcionCd)
| cd | cdNmEs |
|---|---|
| C0000103 | Proveedor unico |
| C0000104 | Patrocinio |
| C0000105 | Medio de comunicacion social |
| C0000106 | Capacitacion abierta |
| C0000107 | Numerarios |
| C0000108 | Alianzas estrategicas |
| C0000109 | Bienes y servicios artisticos |
| C0000110 | Reparaciones indeterminadas |
| C0000111 | Acuerdos internacionales |
| C0000112 | Entes de derecho publico |

### BD106 -- Search Filter Field Types
| cd | cdNmEs |
|---|---|
| 01 | Partida |
| 02 | Tipo procedimiento |
| 03 | Numero de procedimiento |
| 04 | Numero de SICOP |

### BD107 -- Test/Prueba Flag
| cd | cdNmEs |
|---|---|
| N | Prueba (fake/test bid -- filter in ETL) |

### BD109 -- Adjudication Scope
| cd | cdNmEs |
|---|---|
| 0 | Elegir |
| 1 | Por partida |
| 2 | Todas las partidas |

---

## 10. Classifier (classifier.py v3.10)

### categoria output values
| categoria | DB mapped | Description |
|---|---|---|
| MEDICAMENTO | MEDICAMENTO | Drugs, biologics, vaccines, reagents, hemoderivados |
| EQUIPAMIENTO | EQUIPAMIENTO | Medical devices, imaging, surgical equipment, ECMO, TAC |
| INSUMO | INSUMO | Consumables, syringes, sutures, gloves, colchas/cobijas hospitalarias |
| SERVICIOSALUD | SERVICIO | Health services, lab, maintenance |
| TECNOLOGIA | SERVICIO | Health IT, telemedicine |
| OTROMEDICO | null (excluded from medicas full upsert) | Medical but uncategorized |

```python
CATEGORIA_MAP = {
    'MEDICAMENTO': 'MEDICAMENTO',
    'EQUIPAMIENTO': 'EQUIPAMIENTO',
    'INSUMO': 'INSUMO',
    'SERVICIOSALUD': 'SERVICIO',
    'TECNOLOGIA': 'SERVICIO',
    'OTROMEDICO': None,
}

ESTADO_MAP = {
    'RPT_PUB': 'Publicado',
    'RPT_ADJ': 'Adjudicado',
    'RPT_MOD': 'Modificado',
}
```

### classifier v3.10 new additions
New KEYWORDS_DIRECTOS: betametasona, gases medicinales, instrumental laparoscopico,
insumos odontologicos, suplementos nutricionales, ropa/colchones hospitalarios,
cirugia de torax, medicina general, laboratorio de marcha, sillas de ruedas a medida,
analisis quimico-bacteriologico agua, helio

New EXCLUSIONES: cctv, fotovoltaic, extintor, alarma incendi, vehiculos
alineado/tramado, mesas/sillas plegables, mini racks picking, manteles/cubremanteles,
ablandador de agua, baterias/papel bond, pruebas psicologicas, reclutamiento personal
ejecutivo, control de filas, aviones no tripulados, calibracion equipo medicion,
fumigacion plagas, cable electrico, llantas, frutas/vegetales, quimicos lavadora
vajilla, materiales obra civil, UPS/Eaton mantenimiento

Gap 6 fix: level-3 re-verifies exclusions after institution-level match.
00a0 fix: non-breaking space (U+00A0) converted to regular space BEFORE NFD normalization
(previously eliminated by encode('ascii','ignore'), fusing words like 'oxigeno' + 'hiperbar').

---

## 11. Institution Filtering (post-fetch)

API ignores `instNm` in formFilters -- always returns full SICOP dataset.
Filter is applied in Python after fetching all pages.

```python
import unicodedata, re

INSTITUCIONES_TARGET = [
    'CAJA COSTARRICENSE DE SEGURO SOCIAL',
    'INSTITUTO NACIONAL DE SEGUROS',
    'MINISTERIO DE SALUD',
    'INSTITUTO COSTARRICENSE DE INVESTIGACION Y ENSENANZA EN NUTRICION Y SALUD',
    'UNIVERSIDAD DE COSTA RICA',
]

def _norm(texto): return unicodedata.normalize('NFD', texto.lower()).encode('ascii','ignore').decode('ascii')
INSTITUCIONES_NORM = [_norm(i) for i in INSTITUCIONES_TARGET]

def es_institucion_salud(instnm: str, instcode: str | None) -> bool:
    n = _norm(instnm or '')
    if any(t in n for t in INSTITUCIONES_NORM): return True
    # CCSS sub-units identified by instcode suffix
    if instcode and re.match(r'000115\d{4}|0001101\d{3}', instcode): return True
    return False
```

---

## 12. DB Schema v2.1 (Supabase / PostgreSQL)

### licitacionesmedicas -- upsert by instcartelno

```sql
CREATE TABLE IF NOT EXISTS licitacionesmedicas (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Core identifiers
    instcartelno        TEXT UNIQUE NOT NULL,   -- conflict key
    cartelno            TEXT,
    instcode            TEXT,                    -- last segment of instCartelNo

    -- Legacy aliases (backward compat views)
    numeroprocedimiento TEXT,                    -- = instcartelno
    descripcion         TEXT,                    -- = cartelnm
    institucion         TEXT,                    -- = instnm
    adjudicatario       TEXT,                    -- = suppliernm
    estado              TEXT,                    -- RPT_PUB->Publicado, etc.
    fechatramite        TIMESTAMPTZ,             -- = biddocstartdt
    fechalimiteoferta   TIMESTAMPTZ,             -- = biddocenddt

    -- Institution + description
    instnm              TEXT,
    cartelnm            TEXT,

    -- Procedure
    procetype           TEXT,                    -- Full text from API
    tipoprocedimiento   TEXT,                    -- Derived: LD/LY/XE/PX/PE/SE/RE
    typekey             TEXT,                    -- RPT_PUB | RPT_ADJ | RPT_MOD
    modalidad           TEXT,
    excepcioncd         TEXT,                    -- BD105 code
    cartelcate          TEXT,                    -- '1' on RPT_ADJ, null on RPT_PUB
    modreason           TEXT,                    -- RPT_MOD only

    -- UNSPSC
    unspsccd            TEXT,                    -- 8-digit UNSPSC family code
    clasificacionunspsc TEXT,                    -- alias = unspsccd (legacy)

    -- Supplier (winner)
    suppliernm          TEXT,
    suppliercd          TEXT,                    -- Cedula juridica del proveedor

    -- Amounts (parsed from detalle -- amt field is ALWAYS null in API)
    montocolones        NUMERIC,                 -- parsed amount
    currencytype        TEXT,                    -- CRC | USD | EUR (from detalle)
    detalle             TEXT,                    -- Raw adjudication text

    -- Dates
    biddocstartdt       TIMESTAMPTZ,             -- publication date
    biddocenddt         TIMESTAMPTZ,             -- offer deadline
    openbiddt           TIMESTAMPTZ,             -- offer opening date
    adjfirmedt          TIMESTAMPTZ,             -- adjudication firmeza date

    -- Contract
    vigenciacontrato    TEXT,
    unidadvigencia      TEXT,                    -- MESES | ANOS

    -- Classifier output (WARNING: False is valid for esmedica -- use KEEP_FALSY)
    esmedica            BOOLEAN DEFAULT FALSE,
    categoria           TEXT,                    -- MEDICAMENTO | EQUIPAMIENTO | INSUMO | SERVICIO

    -- Raw + metadata
    rawdata             JSONB,
    notificado          BOOLEAN DEFAULT FALSE,
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_instcartelno   ON licitacionesmedicas(instcartelno);
CREATE INDEX IF NOT EXISTS idx_openbiddt      ON licitacionesmedicas(openbiddt DESC);
CREATE INDEX IF NOT EXISTS idx_biddocenddt    ON licitacionesmedicas(biddocenddt);
CREATE INDEX IF NOT EXISTS idx_categoria      ON licitacionesmedicas(categoria);
CREATE INDEX IF NOT EXISTS idx_typekey        ON licitacionesmedicas(typekey);
CREATE INDEX IF NOT EXISTS idx_instnm         ON licitacionesmedicas(instnm);
CREATE INDEX IF NOT EXISTS idx_esmedica       ON licitacionesmedicas(esmedica);
```

### licitacionesmodificaciones -- always INSERT, never upsert

```sql
CREATE TABLE IF NOT EXISTS licitacionesmodificaciones (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    instcartelno    TEXT NOT NULL,   -- NOT unique -- same bid has N modification rows
    cartelno        TEXT,
    procetype       TEXT,
    instnm          TEXT,
    cartelnm        TEXT,
    instcode        TEXT,
    openbiddt       TIMESTAMPTZ,     -- new date after modification
    biddocstartdt   TIMESTAMPTZ,
    modreason       TEXT,            -- what changed
    esmedica        BOOLEAN DEFAULT FALSE,
    categoria       TEXT,
    rawdata         JSONB,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_mod_instcartelno ON licitacionesmodificaciones(instcartelno);
CREATE INDEX IF NOT EXISTS idx_mod_created_at   ON licitacionesmodificaciones(created_at DESC);
ALTER TABLE licitacionesmodificaciones ENABLE ROW LEVEL SECURITY;
CREATE POLICY mod_select_public ON licitacionesmodificaciones FOR SELECT USING (true);
```

### Other tables

```sql
-- precioshistoricos (future: populated from priceBankCata/list once params found)
CREATE TABLE IF NOT EXISTS precioshistoricos (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    descripcionitem TEXT NOT NULL,
    institucion     TEXT,
    proveedor       TEXT,
    preciounitario  NUMERIC,
    cantidad        NUMERIC,
    unidad          TEXT,
    currencytype    TEXT,
    instcartelno    TEXT REFERENCES licitacionesmedicas(instcartelno) ON DELETE CASCADE,
    fecha           DATE,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- alertasconfig (user-defined alerts -- no direct API dep)
CREATE TABLE IF NOT EXISTS alertasconfig (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    userid      UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    keywords    TEXT,
    categorias  TEXT,
    canal       TEXT,   -- 'email' | 'whatsapp'
    activo      BOOLEAN DEFAULT TRUE,
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    updated_at  TIMESTAMPTZ DEFAULT NOW()
);

-- institucionessalud (seed data)
CREATE TABLE IF NOT EXISTS institucionessalud (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre TEXT NOT NULL,
    codigoccss TEXT,
    tipo TEXT,   -- 'Hospital' | 'EBAIS' | 'Area de Salud'
    region TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## 13. Uploader CAMPOS_BASE and KEEP_FALSY

Controls which fields are written for non-medical records
(preserves esmedica/categoria on re-runs for medical ones):

```python
CAMPOS_BASE = {
    'instcartelno', 'cartelno', 'instcode',
    'numeroprocedimiento', 'descripcion', 'institucion',
    'instnm', 'cartelnm',
    'procetype', 'tipoprocedimiento', 'typekey',
    'modalidad', 'excepcioncd', 'cartelcate', 'modreason', 'estado',
    'montocolones', 'currencytype', 'detalle',
    'adjudicatario', 'suppliernm', 'suppliercd',
    'unspsccd', 'clasificacionunspsc',
    'fechatramite', 'biddocstartdt', 'fechalimiteoferta', 'biddocenddt',
    'openbiddt', 'adjfirmedt',
    'vigenciacontrato', 'unidadvigencia',
    'rawdata',
    # NOT included: 'esmedica', 'categoria' -- preserved on re-runs
}

KEEP_FALSY = {'esmedica', 'montocolones'}  # False/0 are valid values
```

---

## 14. Error Response Schema

```json
{
  "id": "e6c33c11-91fb-42e1-97be-8582d10ac2a2",
  "status": "INTERNAL_SERVER_ERROR",
  "timestamp": "2026-03-07 18:48:40",
  "message": "Ocurrio un error inesperado.",
  "module": "bid",
  "userError": false,
  "details": null
}
```

| HTTP | status | Meaning |
|---|---|---|
| 400 | BAD_REQUEST | Missing required param -- check `message` for param name |
| 500 | INTERNAL_SERVER_ERROR | Endpoint exists but params unknown, or server bug |

---

## 15. Known API Quirks

1. **amt is ALWAYS null** -- even on RPT_ADJ. Parse amount from `detalle` via regex.
2. **instNm filter is ignored** -- formFilters `instNm` returns full SICOP dataset.
3. **modReason duplicates instCartelNo** -- never upsert modificadas. Always INSERT.
4. **proceType is full text** -- 'LICITACION REDUCIDA' not 'LD'. Extract from instCartelNo prefix.
5. **cartelCate is null on RPT_PUB** -- only '1' on RPT_ADJ.
6. **Dates have no timezone suffix** -- '2026-03-16T10:01:00' (no Z). Costa Rica = UTC-6.
7. **supplierNm is often null on RPT_ADJ** -- winner name is in detalle text.
8. **currencyType is null on RPT_ADJ** -- always parse from detalle.
9. **BD107 test bids in prod data** -- fake bids injected in SICOP prod. Filter by testYn.
10. **bgnYmd flat format rejected** -- must be inside formFilters array as ISO string with Z suffix.
11. **camelCase vs snake_case parser bug** -- always try both key variants in uploader.
12. **esmedica falsy bug** -- False is valid. Use KEEP_FALSY + filter_none(), never raw `if v`.
13. **500 != dead endpoint** -- priceBankCata/list, sanctionedSuppliers/list exist but need params.

---

## 16. Production ETL Run Stats (March 5, 2026)

```
publicadas:   332-370 records / 4 pages  (3-day window)
adjudicadas:  487-514 records / 5-6 pages (3-day window)
modificadas:  831-955 records / 9-10 pages (3-day window)
publicadas:   81 of 370 are target institutions
adjudicadas:  149 of 487 are target institutions
modificadas:  418 of 955 are target institutions
Total runtime: ~42 seconds for 3-day window on GitHub Actions (ubuntu-latest, Python 3.13)
ETL volumes (90d): 4,407 pub / 16,428 adj / 11,549 mod = ~32,384 records backfill
```

---

## 17. Datos Abiertos Servlet Layer

**Confirmed via live JS parse of `CE_MOD_DATOSABIERTOSVIEW.jsp` (2026-03-27)**

This is a **separate download layer** from the REST API above. It lives on the main JSP host, not `prod-api.sicop.go.cr`.

### Base URL

```
https://www.sicop.go.cr/moduloPcont/servlet/cont/rp
```

Referer required: `https://www.sicop.go.cr/moduloPcont/pcont/rp/CE_MOD_DATOSABIERTOSVIEW.jsp`

### Two-Step Download Protocol

```
Step 1: POST {base}/{controller}.java
        Content-Type: application/x-www-form-urlencoded
        Body: {date_from}=DDMMYYYY & {date_to}=DDMMYYYY & {inst_cd}=CEDULA & {inst_nm}= & cmd=create
        Response: plain-text ZIP filename token (e.g. "Solicitud de contratac 1774514981965.zip")

Step 2: GET {base}/{controller}.java?cmd=download&fileZipName={token}
        Response: ZIP archive containing one JSON file (direct array, no wrapper)
```

- **Date format:** DDMMYYYY (e.g. `01032026` for 2026-03-01)
- **Max date range:** 183 days (6 months) — enforced by SICOP JS validation
- **Empty `inst_cd`** = all institutions
- **CCSS cédula in DA:** `4000042147` (different from REST API `0031700001`)

### Confirmed Controller Map (all 11 — no others exist)

| Key | JSON Controller | Date params | Inst params | ETL status |
|-----|----------------|-------------|-------------|------------|
| SC | `CE_DA_SC_CONTROLLER_JSON` | `bgnYmd`, `endYmd` | `instCdSC`, `instNmSC` | ✅ implemented |
| DC | `CE_DA_DC_CONTROLLER_JSON` | `bgnYmdDC`, `endYmdDC` | `instCdDC`, `instNmDC` | ✅ implemented |
| O | `CE_DA_O_CONTROLLER_JSON` | `bgnYmdO`, `endYmdO` | `instCdO`, `instNmO` | ✅ implemented |
| AF | `CE_DA_AF_CONTROLLER_JSON` | `bgnYmdAF`, `endYmdAF` | `instCdAF`, `instNmAF` | planned (G2 — adjudicaciones) |
| C | `CE_DA_C_CONTROLLER_JSON` | `bgnYmdC`, `endYmdC` | `instCdC`, `instNmC` | not yet |
| OP | `CE_DA_OP_CONTROLLER_JSON` | `bgnYmdOP`, `endYmdOP` | `instCdOP`, `instNmOP` | not yet |
| A | `CE_DA_A_CONTROLLER_JSON` | `bgnYmdA`, `endYmdA` | `instCdA`, `instNmA` | not yet |
| R | `CE_DA_R_CONTROLLER_JSON` | `bgnYmdR`, `endYmdR` | `instCdR`, `instNmR` | not yet |
| IC | `CE_DA_IC_CONTROLLER_JSON` | *(no date range)* | `instCdIC`, `instNmIC`, `provincias`, `cantones` | not yet |
| P | `CE_DA_P_CONTROLLER_JSON` | *(no date/inst)* | `tamano` | not yet |
| CB | `CE_DA_CB_CONTROLLER_JSON` | *(no date/inst)* | `cateId` | not yet |

### SC Lines Anomaly

The SC report's **CSV** format uses `CE_DA_SC_LINES_CONTROLLER.java` — NOT `CE_DA_SC_CONTROLLER_CSV.java` like every other report. This suggests a separate "lines" variant for SC exists. A JSON version (`CE_DA_SC_LINES_CONTROLLER_JSON`) is **unconfirmed** — probe before using.

### ⚠️ Correction: No "Reports 1.1 / 2.1" endpoints

The SICOP data dictionary labels (e.g. "Report 1.1 — Solicitudes de Contratación Líneas", "Report 2.1 — Directamente Contratados Líneas") are **sections of the data dictionary PDF**, not separate servlet endpoints. Only the 11 controllers listed above exist on the download page.

---

## 18. Endpoints Still to Map

| Endpoint | Suspected Purpose | Next Step |
|---|---|---|
| /bid/api/v1/public/priceBankCata/list | Price bank catalog | Navigate to /price-bank-cata, capture payload |
| /bid/api/v1/public/contestsPublishedAwarded/list | Combined list? | Probe with formFilters wrapper |
| /epum/api/v1/public/sanctionedSuppliers/list | Blacklisted suppliers | Navigate to page, capture payload |
| Unknown (participation-history route) | Supplier participation history | Find route, capture endpoint name |
| Unknown (awarded-proc-supplier route) | Supplier win rate | Find route, capture endpoint name |

---

## 18. Angular Chunk List (source code inspection)

```javascript
// Paste in browser console at www.sicop.go.cr/app to find which chunk contains an endpoint:
['chunk-V5OJQD7P','chunk-YWKLJ2Q7','chunk-7UPV726K','chunk-NNHYRGIP',
 'chunk-L4BYVTWQ','chunk-BCOKLJYZ','chunk-YROX2J2T','chunk-2LMKCJXE',
 'chunk-S3VCOOKP','chunk-VYPLITVA','chunk-JBHTHSJ6','chunk-5LM6TPM7',
 'chunk-VIV3BAMN','chunk-7OVNSAXR','chunk-XO3JRKJM','chunk-OMAZD27I',
 'chunk-LEHQLR5Z','chunk-QRJZDVM4','chunk-UOFGVAZR','chunk-4YRY4IP2',
 'chunk-TN3S2DM4','chunk-UWVVJR4Y','chunk-5N5AS6A5','chunk-X7YJLVET',
 'chunk-JKBLGHAJ','chunk-TWZW5B45','chunk-POHVFDYF','chunk-HZHDEPKW',
 'chunk-AUBNM7UW','chunk-D6PUZ23C','chunk-2LFG3ARM','chunk-AFPUQH3A',
 'chunk-ML6EM65R','chunk-FBWTQ4CA'].forEach(c =>{
  fetch(`/app/${c}.js`).then(r=>r.text()).then(src=>{
    if(src.includes('priceBankCata')) console.log('FOUND IN: '+c)
  })
})
```

---

## 19. Repo Structure

```
sicop-health/
  services/etl/
    fetcher.py          <- 3 REST endpoints, retry 3x, exponential backoff, timeout 45s
    parser.py           <- v2.1: 7 new fields, robust monto regex, is_not_None fix
    classifier.py       <- v3.10: 18 new keywords, 12 new exclusions, Gap 6 + 00a0 fix
    uploader.py         <- v2.4: CAMPOS_BASE, KEEP_FALSY, exec_upsert helper, try/except
    main.py             <- orchestrator: fetch -> parse -> classify -> upload -> DA enrichment
    datos_abiertos.py   <- DA servlet scraper: SC/DC/O reports, parsers, upserters
    tests/              <- 20 DA tests passing; REST tests need update to v3.10
  supabase/migrations/
    001_initial_schema.sql   <- v1 CSV-era fields
    002_schema_v2.sql        <- REST API alignment (instcartelno, openbiddt, etc.)
    003_schema_v2.1.sql      <- +9 columns (tipoprocedimiento, unspsccd, suppliercd,
                                  modalidad, excepcioncd, biddocenddt, adjfirmedt,
                                  vigenciacontrato, unidadvigencia)
    004_instcode_esmedica.sql <- instcode + esmedica on licitacionesmodificaciones
    009_datos_abiertos.sql   <- presupuesto_estimado, moneda_presupuesto,
                                  modalidad_participacion on licitaciones_medicas;
                                  da_ofertas table (offer history, FK → licitaciones_medicas)
```