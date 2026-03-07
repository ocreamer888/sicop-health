# SICOP Health Intelligence — Project Specification
_Last updated: 2026-03-06_

---

## 1. Executive Summary

**What:** SaaS B2B platform monitoring medical procurement tenders from Costa Rica's SICOP (Sistema Integrado de Compras Públicas).

**Target Users:** Healthcare suppliers (pharmaceuticals, medical equipment distributors, laboratories).

**Core Value:** Automated detection of new business opportunities, price history analysis, and real-time alerts via WhatsApp/Email.

**Legal Basis:** Public data guaranteed by Costa Rican law (Ley 8292, Ley 9097, Directriz Presidencial N° 025-H).

---

## 2. Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        Data Sources                             │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │ SICOP API   │  │ SICOP API    │  │ SICOP API    │           │
│  │ (Publicadas)│  │ (Adjudicadas)│  │(Modificadas) │           │
│  └──────┬──────┘  └───────┬──────┘  └───────┬──────┘           │
└─────────┼─────────────────┼─────────────────┼───────────────────┘
          │                 │                 │
          └─────────────────┼─────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                     ETL Pipeline (Python)                         │
│  ┌─────────┐  ┌─────────┐  ┌───────────┐  ┌──────────┐        │
│  │ Fetcher │→ │ Parser  │→ │Classifier │→ │ Uploader │        │
│  └─────────┘  └─────────┘  └───────────┘  └─────┬────┘        │
└─────────────────────────────────────────────────┼───────────────┘
                                                    │
                                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Supabase (PostgreSQL)                         │
│  ┌────────────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │licitaciones_medicas│  │licitaciones_ │  │   precios_   │       │
│  │   (main table)     │  │modificaciones│  │  historicos  │       │
│  └────────────────────┘  └──────────────┘  └──────────────┘       │
│  ┌────────────────────┐  ┌──────────────┐                        │
│  │   alertas_config   │  │instituciones │                        │
│  │  (per-user alerts) │  │   _salud     │                        │
│  └────────────────────┘  └──────────────┘                        │
└────────────────────────────────────────────┬────────────────────┘
                                             │
                              ┌──────────────┴──────────────┐
                              ▼                              ▼
┌──────────────────────────────────┐  ┌──────────────────────┐
│     Next.js 16 (App Router)      │  │   Edge Functions     │
│  ┌──────────┐  ┌──────────────┐  │  │ ┌────────────────┐ │
│  │/dashboard│  │/licitaciones │  │  │ │ match-alerts   │ │
│  │  (SSR)   │  │   (SSR)      │  │  │ │ send-email     │ │
│  └──────────┘  └──────────────┘  │  │ │ send-whatsapp  │ │
│  ┌──────────┐  ┌──────────────┐  │  │ └────────────────┘ │
│  │/alertas  │  │/licitaciones │  │  │                    │
│  │  (CSR)   │  │  /[id]       │  │  └────────────────────┘
│  └──────────┘  └──────────────┘  │
│  ┌──────────┐                    │
│  │/auth/    │                    │
│  │ login    │                    │
│  └──────────┘                    │
└──────────────────────────────────┘
```

---

## 3. Database Schema

### 3.1 Core Tables

#### `licitaciones_medicas`
Main table containing all medical procurement tenders.

```sql
CREATE TABLE licitaciones_medicas (
    -- Identity
    id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    instcartelno          TEXT UNIQUE NOT NULL,  -- Logical PK: 2026LD-000003-0001102555
    cartelno              TEXT,
    
    -- Description
    cartelnm              TEXT,                   -- Tender title
    instnm                TEXT,                   -- Institution name
    inst_code             TEXT,                   -- Institution code (extracted from instcartelno)
    
    -- Status
    estado                TEXT,                   -- Publicado | Adjudicado | Desierto | Cancelado
    es_medica             BOOLEAN DEFAULT FALSE,
    categoria             TEXT,                   -- MEDICAMENTO | EQUIPAMIENTO | INSUMO | SERVICIO
    
    -- Procedure
    procetype             TEXT,                   -- Full label from API
    tipo_procedimiento    TEXT,                   -- LD | LY | LE | LG | LP | PX | PE | XE | CD
    typekey               TEXT,                   -- RPT_PUB | RPT_ADJ | RPT_MOD
    modalidad             TEXT,
    excepcion_cd          TEXT,                   -- Legal exception code
    cartel_cate           TEXT,
    mod_reason            TEXT,                   -- Modification reason
    
    -- Classification
    unspsc_cd             TEXT,                   -- 8-digit UNSPSC code
    
    -- Provider
    supplier_nm           TEXT,                   -- Adjudicatario
    supplier_cd           TEXT,                   -- Provider ID
    
    -- Financial
    monto_colones         NUMERIC,
    currency_type         TEXT,                   -- CRC | USD
    detalle               TEXT,
    
    -- Dates
    biddoc_start_dt       TIMESTAMPTZ,            -- Publication date
    biddoc_end_dt         TIMESTAMPTZ,            -- Deadline
    openbid_dt            TIMESTAMPTZ,            -- Bid opening
    adj_firme_dt          TIMESTAMPTZ,            -- Adjudication firm date
    
    -- Contract
    vigencia_contrato     TEXT,
    unidad_vigencia       TEXT,
    
    -- Metadata
    raw_data              JSONB,
    created_at            TIMESTAMPTZ DEFAULT NOW(),
    updated_at            TIMESTAMPTZ DEFAULT NOW()
);
```

**Indexes:**
```sql
CREATE INDEX idx_licitaciones_instcartelno ON licitaciones_medicas(instcartelno);
CREATE INDEX idx_licitaciones_instnm ON licitaciones_medicas(instnm);
CREATE INDEX idx_licitaciones_inst_code ON licitaciones_medicas(inst_code);
CREATE INDEX idx_licitaciones_tipo_proc ON licitaciones_medicas(tipo_procedimiento);
CREATE INDEX idx_licitaciones_unspsc ON licitaciones_medicas(unspsc_cd);
CREATE INDEX idx_licitaciones_supplier ON licitaciones_medicas(supplier_cd);
CREATE INDEX idx_licitaciones_biddoc_start ON licitaciones_medicas(biddoc_start_dt DESC);
CREATE INDEX idx_licitaciones_biddoc_end ON licitaciones_medicas(biddoc_end_dt) WHERE biddoc_end_dt IS NOT NULL;
CREATE INDEX idx_licitaciones_typekey ON licitaciones_medicas(typekey);
CREATE INDEX idx_licitaciones_currency ON licitaciones_medicas(currency_type);
CREATE INDEX idx_licitaciones_es_medica ON licitaciones_medicas(es_medica);
CREATE INDEX idx_licitaciones_categoria ON licitaciones_medicas(categoria) WHERE es_medica = true;
CREATE INDEX idx_licitaciones_estado ON licitaciones_medicas(estado);
```

#### `licitaciones_modificaciones`
Tracks modifications to tenders (date changes, etc.).

```sql
CREATE TABLE licitaciones_modificaciones (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    inst_cartel_no  TEXT NOT NULL,   -- References licitacion (not strict FK)
    cartel_no       TEXT,
    proce_type      TEXT,
    inst_nm         TEXT,
    cartel_nm       TEXT,
    inst_code       TEXT,
    es_medica       BOOLEAN DEFAULT FALSE,
    categoria       TEXT,
    openbid_dt      TIMESTAMPTZ,     -- New date after modification
    biddoc_start_dt TIMESTAMPTZ,
    mod_reason      TEXT,            -- Reason for modification
    raw_data        JSONB,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_mod_inst_cartel_no ON licitaciones_modificaciones(inst_cartel_no);
CREATE INDEX idx_mod_created_at ON licitaciones_modificaciones(created_at DESC);
```

#### `precios_historicos`
Historical prices by item for market intelligence.

```sql
CREATE TABLE precios_historicos (
    id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    descripcion_item      TEXT NOT NULL,
    clasificacion_unspsc  TEXT,
    institucion           TEXT,
    proveedor             TEXT,
    precio_unitario       NUMERIC,
    cantidad              NUMERIC,
    unidad                TEXT,
    numero_procedimiento  TEXT REFERENCES licitaciones_medicas(instcartelno) ON DELETE CASCADE,
    fecha                 DATE,
    created_at            TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_precios_descripcion ON precios_historicos(descripcion_item);
CREATE INDEX idx_precios_fecha ON precios_historicos(fecha DESC);
CREATE INDEX idx_precios_procedimiento ON precios_historicos(numero_procedimiento);
```

#### `alertas_config`
Per-user alert configuration.

```sql
CREATE TABLE alertas_config (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    nombre      TEXT,                   -- Alert name
    keywords    TEXT[],                 -- ["insulina", "metformina"]
    categorias  TEXT[],                 -- ["MEDICAMENTO", "EQUIPAMIENTO"]
    instituciones TEXT[],               -- ["0001102555", "0001102102"]
    monto_min   NUMERIC,
    monto_max   NUMERIC,
    canales     TEXT[],                 -- ["email", "whatsapp"]
    activo      BOOLEAN DEFAULT TRUE,
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    updated_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_alertas_user ON alertas_config(user_id);
CREATE INDEX idx_alertas_activo ON alertas_config(user_id, activo);
```

#### `alertas_enviadas`
Tracks sent notifications to prevent duplicates.

```sql
CREATE TABLE alertas_enviadas (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    alerta_id     UUID REFERENCES alertas_config(id),
    instcartelno  TEXT REFERENCES licitaciones_medicas(instcartelno),
    user_id       UUID REFERENCES auth.users(id),
    enviado_at    TIMESTAMPTZ DEFAULT NOW(),
    canal         TEXT,                   -- "email" | "whatsapp"
    UNIQUE(alerta_id, instcartelno, canal)
);

CREATE INDEX idx_alertas_enviadas_user ON alertas_enviadas(user_id);
CREATE INDEX idx_alertas_enviadas_fecha ON alertas_enviadas(enviado_at DESC);
```

#### `instituciones_salud`
Catalog of health institutions.

```sql
CREATE TABLE instituciones_salud (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre          TEXT NOT NULL,
    codigo_ccss     TEXT,
    tipo            TEXT,               -- Hospital, EBAIS, etc.
    region          TEXT,
    direccion       TEXT,
    telefono        TEXT,
    email           TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
```

### 3.2 Views

#### `resumen_por_categoria`
Dashboard summary by category.

```sql
CREATE OR REPLACE VIEW resumen_por_categoria AS
SELECT
  categoria,
  COUNT(*)                                              AS total,
  COUNT(*) FILTER (WHERE typekey = 'RPT_PUB')           AS publicadas,
  COUNT(*) FILTER (WHERE typekey = 'RPT_ADJ')           AS adjudicadas,
  SUM(monto_colones) FILTER (WHERE currency_type = 'CRC') AS monto_crc,
  SUM(monto_colones) FILTER (WHERE currency_type = 'USD') AS monto_usd
FROM licitaciones_medicas
WHERE es_medica = true AND categoria IS NOT NULL
GROUP BY categoria
ORDER BY total DESC;
```

#### `resumen_por_institucion`
Summary by institution for institutional dashboard.

```sql
CREATE OR REPLACE VIEW resumen_por_institucion AS
SELECT
  instnm,
  inst_code,
  COUNT(*)                                              AS total,
  COUNT(*) FILTER (WHERE es_medica = true)              AS medicas,
  COUNT(*) FILTER (WHERE typekey = 'RPT_PUB')           AS publicadas,
  COUNT(*) FILTER (WHERE typekey = 'RPT_ADJ')           AS adjudicadas,
  SUM(monto_colones) FILTER (WHERE currency_type = 'CRC') AS monto_crc,
  SUM(monto_colones) FILTER (WHERE currency_type = 'USD') AS monto_usd
FROM licitaciones_medicas
WHERE instnm IS NOT NULL
GROUP BY instnm, inst_code
ORDER BY medicas DESC;
```

#### `licitaciones_por_vencer`
Tenders expiring in next 7 days.

```sql
CREATE OR REPLACE VIEW licitaciones_por_vencer AS
SELECT
  instcartelno,
  cartelnm,
  instnm,
  inst_code,
  categoria,
  tipo_procedimiento,
  unspsc_cd,
  currency_type,
  monto_colones       AS amt,
  biddoc_end_dt       AS deadline,
  openbid_dt,
  biddoc_start_dt     AS publicado_dt,
  es_medica
FROM licitaciones_medicas
WHERE biddoc_end_dt BETWEEN NOW() AND (NOW() + INTERVAL '7 days')
  AND es_medica = true
ORDER BY biddoc_end_dt ASC;
```

### 3.3 Row Level Security (RLS)

**CRITICAL:** Run this in production to enforce authentication.

```sql
-- Enable RLS
ALTER TABLE licitaciones_medicas ENABLE ROW LEVEL SECURITY;
ALTER TABLE licitaciones_modificaciones ENABLE ROW LEVEL SECURITY;
ALTER TABLE precios_historicos ENABLE ROW LEVEL SECURITY;
ALTER TABLE alertas_config ENABLE ROW LEVEL SECURITY;
ALTER TABLE alertas_enviadas ENABLE ROW LEVEL SECURITY;
ALTER TABLE instituciones_salud ENABLE ROW LEVEL SECURITY;

-- Public read access to tenders (authenticated users)
CREATE POLICY "Authenticated users can view licitaciones"
  ON licitaciones_medicas FOR SELECT TO authenticated USING (true);

CREATE POLICY "Authenticated users can view modificaciones"
  ON licitaciones_modificaciones FOR SELECT TO authenticated USING (true);

CREATE POLICY "Authenticated users can view precios"
  ON precios_historicos FOR SELECT TO authenticated USING (true);

CREATE POLICY "Authenticated users can view instituciones"
  ON instituciones_salud FOR SELECT TO authenticated USING (true);

-- User-scoped alerts
CREATE POLICY "Users can view their own alerts"
  ON alertas_config FOR SELECT TO authenticated USING (auth.uid() = user_id);

CREATE POLICY "Users can create their own alerts"
  ON alertas_config FOR INSERT TO authenticated WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own alerts"
  ON alertas_config FOR UPDATE TO authenticated USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own alerts"
  ON alertas_config FOR DELETE TO authenticated USING (auth.uid() = user_id);

-- Alert history scoped to user
CREATE POLICY "Users can view their own alert history"
  ON alertas_enviadas FOR SELECT TO authenticated USING (auth.uid() = user_id);
```

---

## 4. Frontend Structure

### 4.1 Routes

| Route | Type | Protection | Description |
|-------|------|------------|-------------|
| `/` | redirect | — | → `/dashboard` |
| `/dashboard` | Server Component | authenticated | Main dashboard with metrics |
| `/licitaciones` | Server Component | authenticated | List all tenders (paginated) |
| `/licitaciones/[id]` | Server Component | authenticated | Detail view (id = instcartelno) |
| `/alertas` | Server Component | authenticated | Alert configuration UI |
| `/precios` | Server Component | authenticated | Price history (pending) |
| `/auth/login` | Server Component | public | Login form |
| `/auth/callback` | Route Handler | public | OAuth/magic link callback |

### 4.2 Key Components

```typescript
// lib/types.ts — Central type definitions
type Categoria = "MEDICAMENTO" | "EQUIPAMIENTO" | "INSUMO" | "SERVICIO";
type Estado = "Publicado" | "Adjudicado" | "Desierto" | "Cancelado";
type TypeKey = "RPT_PUB" | "RPT_ADJ" | "RPT_MOD";
type TipoProcedimiento = "LD" | "LY" | "LE" | "LG" | "LP" | "PX" | "PE" | "XE" | "CD";

interface Licitacion {
  id: string;
  instcartelno: string;
  cartelnm: string | null;
  instnm: string | null;
  categoria: Categoria | null;
  tipo_procedimiento: TipoProcedimiento | null;
  monto_colones: number | null;
  currency_type: string | null;
  estado: Estado | null;
  // ... see schema above
}

type LicitacionPreview = Pick<Licitacion,
  "id" | "instcartelno" | "cartelnm" | "instnm" | "categoria" |
  "tipo_procedimiento" | "monto_colones" | "currency_type" |
  "biddoc_start_dt" | "biddoc_end_dt" | "estado" | "es_medica"
>;
```

### 4.3 Data Fetching Pattern

```typescript
// Server Components use:
import { createClient } from "@/lib/supabase/server";

async function getData() {
  const supabase = await createClient();
  const { data } = await supabase
    .from("licitaciones_medicas")
    .select("...")
    .eq("es_medica", true)
    .not("categoria", "is", null)
    .order("biddoc_start_dt", { ascending: false });
  return data;
}
```

---

## 5. ETL Pipeline

### 5.1 Architecture

```
services/etl/
├── main.py              # Entry point, orchestration
├── fetcher.py           # HTTP requests to SICOP API
├── parser.py            # Data transformation, column mapping
├── classifier.py        # Medical classification logic
├── uploader.py          # Supabase bulk insert/update
└── requirements.txt
```

### 5.2 Execution

**Local:**
```bash
cd services/etl
python main.py --dias 7    # Last 7 days
python main.py --dias 90   # Backfill 90 days
```

**Production (GitHub Actions):**
- Runs every hour via `.github/workflows/etl-cron.yml`
- Uses `SUPABASE_SERVICE_KEY` (bypasses RLS)
- Logs to GitHub Actions console

### 5.3 Classification Logic

```python
# Primary: UNSPSC code prefix
MEDICAL_UNSPSC_PREFIXES = ("42", "51", "53", "85", "41")

# Secondary: Keyword matching in description
MEDICAL_KEYWORDS = [
    "medicamento", "fármaco", "vacuna", "insulina", "antibiótico",
    "tomógrafo", "resonancia", "ventilador", "desfibrilador",
    "jeringa", "catéter", "sutura", "reactivo", "PCR",
    "gases medicinales", "instrumental laparoscópico"
]

# Result categories
CATEGORIAS = ["MEDICAMENTO", "EQUIPAMIENTO", "INSUMO", "SERVICIO"]
```

---

## 6. Alert System (Pending Implementation)

### 6.1 User Flow

1. User creates alert at `/alertas` with:
   - Keywords ("insulina", "metformina")
   - Categories (MEDICAMENTO, INSUMO)
   - Institutions (CCSS codes)
   - Amount range (optional)
   - Channels (email, whatsapp)

2. ETL detects new tender → calls `match-alerts` edge function
3. Edge function evaluates all active alerts against tender
4. For each match: insert into `alertas_enviadas` (deduplication)
5. Call `send-email` or `send-whatsapp` edge function
6. User receives notification within 5 minutes

### 6.2 Edge Functions (To Build)

```typescript
// supabase/functions/match-alerts/index.ts
// Input: instcartelno
// Logic: Evaluate all active alerts, return matches
// Output: Array of { alerta_id, user_id, canales }

// supabase/functions/send-email/index.ts
// Input: user_email, alerta_nombre, licitacion_data
// Integration: Resend API
// Template: HTML with design system colors

// supabase/functions/send-whatsapp/index.ts
// Input: user_phone, alerta_nombre, licitacion_summary
// Integration: WhatsApp Business API (Meta)
// Template: Approved message template
```

---

## 7. Current Status

### ✅ Complete
- [x] ETL pipeline (Python, hourly cron)
- [x] Database schema v2.9 with all columns
- [x] Next.js frontend with App Router
- [x] Authentication (login, middleware, protected routes)
- [x] Dashboard with real metrics
- [x] Licitaciones list + detail pages
- [x] RLS migration (pending execution in prod)

### ⏳ In Progress / Pending
- [ ] Alert configuration UI (`/alertas`)
- [ ] Alert matching engine (edge function)
- [ ] Email notifications (Resend)
- [ ] WhatsApp notifications (optional)
- [ ] Price history view (`/precios`)
- [ ] 90-day backfill execution
- [ ] Institution filter in licitaciones list

### ❌ Not Started
- [ ] Mobile app (React Native)
- [ ] Team/enterprise accounts
- [ ] ERP integrations (SAP, Oracle)
- [ ] Regional expansion (Guatemala, Panamá)

---

## 8. Deployment Checklist

### Pre-launch (Must Have)
- [ ] Run `004_rls.sql` in Supabase Dashboard
- [ ] Create admin user in Supabase Auth
- [ ] Verify ETL running and populating data
- [ ] Test login → dashboard flow end-to-end
- [ ] Test alert creation → matching → notification flow
- [ ] Set up Resend account and verify email delivery

### Production Environment
```bash
# apps/web/.env.local
NEXT_PUBLIC_SUPABASE_URL=https://ofjsiatheyuhhdpxfaea.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ...

# services/etl/.env
SUPABASE_URL=https://ofjsiatheyuhhdpxfaea.supabase.co
SUPABASE_SERVICE_KEY=eyJ...  # Service role, bypasses RLS
```

### Post-launch (Nice to Have)
- [ ] Custom domain
- [ ] Email template branding
- [ ] Analytics (PostHog/Plausible)
- [ ] Error monitoring (Sentry)

---

## 9. Design System Quick Reference

### Colors
- Background dark: `#1a1f1a`
- Background card: `#2c3833`
- Background hover: `#3d4d45`
- Text cream: `#f9f5df`
- Text body: `#f2f5f9`
- Text muted: `var(--color-text-muted)`
- Accent green: `#84a584`
- Accent olive: `#898a7d`

### Border Radius
- Cards: `rounded-[24px]`
- Inner elements: `rounded-[16px]`
- Pills/buttons: `rounded-[60px]`

### Fonts
- Heading: `font-[family-name:var(--font-montserrat)]`
- Body: `font-[family-name:var(--font-plus-jakarta)]`

---

## 10. Common Tasks

### Add New Migration
```bash
# Create file with timestamp
supabase migration new add_alertas_enviadas
# Edit supabase/migrations/...
# Test locally: supabase db reset
# Deploy: supabase db push
```

### Debug ETL
```bash
cd services/etl
python main.py --dias 1 --verbose
# Check GitHub Actions logs for production runs
```

### Add New Page
1. Create `app/nueva-pagina/page.tsx`
2. Use `createClient()` from `@/lib/supabase/server`
3. Protected automatically by middleware
4. Add to Nav if needed

---

**This document is the single source of truth. Update it when schema changes, features are added, or architecture evolves.**
