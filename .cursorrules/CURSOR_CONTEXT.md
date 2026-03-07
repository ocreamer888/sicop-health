# SICOP Health Intelligence — Cursor Context
_Last updated: 2026-03-07_

---

## Project Overview
SaaS B2B que monitorea licitaciones médicas del sistema de compras públicas de Costa Rica (SICOP).
Usuarios target: proveedores del sector salud (farmas, distribuidoras de equipo médico, laboratorios).

---

## Monorepo Structure
```
sicop-health/
├── apps/web/                    # Next.js 16.1 — App Router
│   └── src/
│       ├── middleware.ts                ✅ session refresh + route protection
│       ├── app/
│       │   ├── dashboard/page.tsx       ✅ updated
│       │   ├── licitaciones/
│       │   │   ├── page.tsx             ✅ query licitaciones_medicas direct
│       │   │   └── [id]/page.tsx        ✅ query by instcartelno
│       │   ├── alertas/
│       │   │   ├── page.tsx             ⏳ needs rewrite → notification inbox
│       │   │   ├── actions.ts           ⏳ needs rewrite → getNotificaciones()
│       │   │   ├── alerta-form.tsx      🔒 preserved — future detailed search UI
│       │   │   └── alerta-card.tsx      ⏳ needs rewrite → NotificacionCard
│       │   └── auth/
│       │       ├── actions.ts            ✅ signIn, signOut (server actions)
│       │       ├── callback/route.ts     ✅ code exchange
│       │       ├── layout.tsx            ✅ no Nav
│       │       └── login/page.tsx        ✅ email/password
│       ├── components/
│       │   ├── nav.tsx                   ✅ Dashboard | Licitaciones | Alertas (Bell)
│       │   ├── licitaciones-table.tsx   ✅ links use instcartelno
│       │   └── ui/
│       │       ├── stat-card.tsx
│       │       └── badge.tsx
│       └── lib/
│           ├── types.ts                 ✅ schema v2.9 + AlertaConfig / AlertaFormData
│           └── supabase/
│               ├── client.ts
│               └── server.ts
├── services/etl/                # Python 3.13
│   ├── main.py
│   ├── fetcher.py
│   ├── parser.py                v2.2
│   ├── classifier.py            v3.8
│   ├── uploader.py              v2.9
│   └── requirements.txt
├── supabase/
│   ├── migrations/
│   │   ├── 001_initial_schema.sql
│   │   ├── 002_...sql
│   │   ├── 003_schema_v2.sql            ✅ applied in prod
│   │   └── 004_rls.sql                  ✅ applied in prod
│   └── functions/
│       ├── notify-new-licitacion/       ⏳ not built yet
│       └── send-email/                  ⏳ not built yet
└── .github/workflows/
    └── etl-cron.yml                    ✅ running hourly
```

---

## DB Schema v2.9 — licitaciones_medicas (post-migration 003)

### Columnas removidas (NO usar)
```
❌ numero_procedimiento  → instcartelno
❌ descripcion           → cartelnm
❌ institucion           → instnm
❌ adjudicatario         → supplier_nm
❌ clasificacion_unspsc  → unspsc_cd
❌ fecha_tramite         → biddoc_start_dt
❌ fecha_limite_oferta   → biddoc_end_dt
```

### Columnas actuales
```sql
instcartelno     TEXT  NOT NULL UNIQUE  -- PK lógica, formato: 2026LD-000003-0001102555
cartelno         TEXT
cartelnm         TEXT                   -- título licitación
instnm           TEXT                   -- nombre institución
inst_code        TEXT                   -- código numérico institución
estado           TEXT                   -- Publicado | Adjudicado | Desierto | Cancelado
es_medica        BOOLEAN DEFAULT false
categoria        TEXT                   -- MEDICAMENTO | EQUIPAMIENTO | INSUMO | SERVICIO
tipo_procedimiento TEXT                 -- LD | LY | LE | LP | PX | PE | XE | CD
procetype        TEXT                   -- label largo del API
typekey          TEXT                   -- RPT_PUB | RPT_ADJ | RPT_MOD
modalidad        TEXT
excepcion_cd     TEXT
cartel_cate      TEXT
mod_reason       TEXT
unspsc_cd        TEXT
supplier_nm      TEXT
supplier_cd      TEXT
monto_colones    NUMERIC
currency_type    TEXT                   -- CRC | USD
detalle          TEXT
biddoc_start_dt  TIMESTAMPTZ            -- fecha publicación
biddoc_end_dt    TIMESTAMPTZ            -- deadline ofertas
openbid_dt       TIMESTAMPTZ
adj_firme_dt     TIMESTAMPTZ
vigencia_contrato TEXT
unidad_vigencia  TEXT
raw_data         JSONB
created_at       TIMESTAMPTZ DEFAULT now()
updated_at       TIMESTAMPTZ DEFAULT now()
```

### Otras tablas
```
licitaciones_modificaciones  -- inst_cartel_no, mod_reason, es_medica, etc.
precios_historicos           -- FK → licitaciones_medicas(instcartelno)
alertas_config               -- user_id, keywords[], categorias[], unspsc[], canal[], activo
                             -- ⚠️ En producción pero NO usada por la app actualmente.
                             --    Candidata para futura feature de búsquedas guardadas.
instituciones_salud          -- nombre, codigo_ccss, tipo, region
```
Note: `alertas_enviadas` NO existe en producción (solo en documentación antigua).

### Vista SQL activa
```sql
-- resumen_por_categoria
-- Filtra: es_medica=true AND categoria IS NOT NULL
-- Columnas: categoria, total, publicadas, adjudicadas, monto_crc, monto_usd
```

---

## TypeScript Types — lib/types.ts (v2.9)

```typescript
type Categoria = "MEDICAMENTO" | "EQUIPAMIENTO" | "INSUMO" | "SERVICIO"
type Estado    = "Publicado" | "Adjudicado" | "Modificado" | "Desierto" | "Cancelado" | (string & {})
type TypeKey   = "RPT_PUB" | "RPT_ADJ" | "RPT_MOD"
type TipoProcedimiento = "LD" | "LY" | "LE" | "LG" | "LP" | "PX" | "PE" | "XE" | "CD" | (string & {})

const TIPO_LABELS: Record<string, string>  // exportado — usar en lugar de definir local

interface Licitacion        // schema completo post-migration 003
interface DashboardStats    // columnas: publicadas, adjudicadas, monto_crc, monto_usd

type LicitacionPreview = Pick<Licitacion,
  "id" | "instcartelno" | "cartelnm" | "instnm" | "categoria" |
  "tipo_procedimiento" | "monto_colones" | "currency_type" |
  "biddoc_start_dt" | "biddoc_end_dt" | "estado" | "es_medica"
>
// LicitacionLike NO existe — fue eliminado. Usar LicitacionPreview.

interface AlertaConfig      // future search/filter config — preserved for later use
type AlertaFormData         // Omit<AlertaConfig, 'id'|'user_id'|'created_at'|'updated_at'>
                            // ⚠️ AlertaConfig type has more fields than the production DB
                            //    schema (nombre, instituciones, monto_min, monto_max).
                            //    Do NOT use it for direct Supabase queries against alertas_config.
```

---

## ETL Status

```
Pipeline:       ✅ Production-ready
Last run:       2026-03-06 02:17 CST
HTTP status:    200 OK (upsert) / 201 Created (insert) — 0 errores
Métricas:       65 médicas de 163 procesados (40%)
                32 pub médicas | 15 adj médicas | 18 modificaciones
Cron:           GitHub Actions — hourly
Clasificación:  ~40% médicas del total SICOP
```

### ETL Column Map (uploader.py v2.9)
```python
# Campos que escribe el ETL → columnas DB
instcartelno    ← instCartelNo del API     (PK lógica, conflict key)
cartelnm        ← cartelNm
instnm          ← instNm
inst_code       ← instCode
tipo_procedimiento ← extraído de instCartelNo (ej: "2026LD-..." → "LD")
typekey         ← RPT_PUB | RPT_ADJ | RPT_MOD
currency_type   ← CRC | USD (con guard para ambigüedad)
```

---

## Frontend Status

| Archivo | Estado | Notas |
|---|---|---|
| `middleware.ts` | ✅ | session refresh, redirect unauthenticated → /auth/login |
| `dashboard/page.tsx` | ✅ | queries v2, nuevasEstaSemana real |
| `licitaciones/[id]/page.tsx` | ✅ | query by instcartelno, columnas v2 |
| `licitaciones-table.tsx` | ✅ | link href uses instcartelno (not id) |
| `lib/types.ts` | ✅ | schema v2.9 + AlertaConfig / AlertaFormData |
| `auth/login/page.tsx` | ✅ | email/password, server action, error via searchParams |
| `auth/actions.ts` | ✅ | signIn, signOut |
| `nav.tsx` | ✅ | Dashboard \| Licitaciones \| Alertas (Bell icon) |
| `licitaciones/page.tsx` | ⏳ | still uses view licitaciones_activas — switch to licitaciones_medicas |
| `alertas/page.tsx` | ⏳ | built as CRUD rule builder — needs rewrite as notification inbox |
| `alertas/actions.ts` | ⏳ | has CRUD actions — needs rewrite: single getNotificaciones() |
| `alertas/alerta-form.tsx` | 🔒 | preserved — future detailed search UI (do not delete) |
| `alertas/alerta-card.tsx` | ⏳ | needs rewrite as read-only NotificacionCard |

---

## Pending Tasks (ordered)

1. **`licitaciones/page.tsx`** — actualizar a columnas v2 (instcartelno, cartelnm, instnm)
2. **Backfill 90 días** — `python main.py --dias 90` una sola vez
3. **`alertas/page.tsx`** — rewrite as notification inbox (query licitaciones_medicas, es_medica=true, DESC)
4. **`alertas/actions.ts`** — rewrite: single `getNotificaciones()` action
5. **`alertas/alerta-card.tsx`** — rewrite as read-only `NotificacionCard`
6. **`supabase/functions/notify-new-licitacion`** — edge function: DB webhook on INSERT → fetch all users → send email (Resend) + WhatsApp placeholder
7. **`supabase/functions/send-email`** — Resend email edge function
8. **DB Webhook** — configure in Supabase Dashboard: INSERT on licitaciones_medicas → notify-new-licitacion
9. **`precios/page.tsx`** — historial de precios por ítem con chart

---

## Key Rules for This Codebase

- **Nunca usar** `numero_procedimiento`, `descripcion`, `institucion`, `adjudicatario`, `fecha_tramite`, `fecha_limite_oferta` — columnas eliminadas en migration 003
- **Siempre** importar `TIPO_LABELS` de `@/lib/types`, no redefinir local
- **LicitacionLike no existe** — usar `LicitacionPreview` para listas/tablas
- **`licitaciones_activas`** (view) fue eliminada — query directo a `licitaciones_medicas`
- **`resumen_por_categoria`** retorna strings para números — siempre `Number(r.monto_crc ?? 0)`
- **currency_type** leer siempre de columna DB, nunca de `raw_data?.currencytype`
- **Supabase client** en Server Components: `await createClient()` de `@/lib/supabase/server`
- **Rutas protegidas**: middleware redirige a `/auth/login` si no hay sesión; solo `/auth/*` es público
- **Detail URL**: usar `instcartelno` en links y en `[id]` (la view `licitaciones_activas` no expone `id`)

---

## Auth & RLS

- **Login**: email/password vía Supabase Auth; usuarios se crean en Supabase Dashboard (sin self-signup por ahora).
- **Middleware**: refresca sesión en cada request; sin sesión → redirect a `/auth/login`.
- **RLS** (migration 004): `licitaciones_medicas`, `licitaciones_modificaciones`, `precios_historicos`, `instituciones_salud` → SELECT para `authenticated`. `alertas_config` → CRUD solo donde `auth.uid() = user_id` (tabla en prod pero no usada actualmente). ETL usa service_role y no se ve afectado.

---

## Supabase Config

```
Project URL:    https://ofjsiatheyuhhdpxfaea.supabase.co
Auth:           Supabase Auth (email/password). RLS habilitado (004_rls.sql).
Client pattern:
  Server Components → import { createClient } from "@/lib/supabase/server"
  Client Components → import { createClient } from "@/lib/supabase/client"
```

---

## Design System / UI Rules

```
Font heading:   var(--font-montserrat)      → font-[family-name:var(--font-montserrat)]
Font body:      var(--font-plus-jakarta)    → font-[family-name:var(--font-plus-jakarta)]
Font mono:      font-mono (Tailwind default)

Colores principales:
  Background dark:   #1a1f1a
  Background card:   #2c3833
  Background hover:  #3d4d45
  Text cream:        #f9f5df
  Text body:         #f2f5f9
  Text secondary:    #e4e4e4
  Text muted:        var(--color-text-muted)
  Accent green:      #84a584
  Accent olive:      #898a7d

Border radius:
  Cards:    rounded-[24px]
  Inner:    rounded-[16px]
  Pills:    rounded-[60px]
  Badges:   rounded-full

Badge variants: "default" | "secondary" | "sage" | "olive"

Estado → color:
  Publicado   #84a584
  Adjudicado  #898a7d
  Desierto    #5d6a85
  Cancelado   #a58484
```

---

## SICOP API

```
Base:        https://prod-api.sicop.go.cr/bid-api/v1/public
Endpoints:
  publicadas:   /ep/CartelReleaseAdjuModlistPage/Release
  adjudicadas:  /ep/CartelReleaseAdjuModlistPage/Awarded
  modificadas:  /ep/CartelReleaseAdjuModlistPage/Modified

Auth:        ninguna — público
Format:      JSON paginado (pageNumber, pageSize, tableSorter)
TypeKeys:    RPT_PUB | RPT_ADJ | RPT_MOD

instCartelNo format: {año}{tipo}-{seq}-{instCode}
  Ejemplo: 2026LD-000003-0001102555
  tipo_procedimiento se extrae del segmento central (LD, XE, LY...)
  inst_code se extrae del último segmento (0001102555)
```

---

## ETL Environment Variables

```bash
# services/etl/.env
SUPABASE_URL=https://ofjsiatheyuhhdpxfaea.supabase.co
SUPABASE_SERVICE_KEY=...   # service role — bypasa RLS
```

```bash
# apps/web/.env.local
NEXT_PUBLIC_SUPABASE_URL=https://ofjsiatheyuhhdpxfaea.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=...
```

---

## Instituciones Target (30 códigos activos)

```python
# classifier.py — INSTITUTION_CODES set
# Núcleo CCSS (~160 unidades de compra bajo inst_code 0001*)
# Ministerio de Salud
# INS (Instituto Nacional de Seguros)
# IAFA, CENDEISSS, hospitales nacionales, EBAIS
# 418 de 996 modificadas son instituciones target (run 2026-03-06)
```

---

## Clasificación Médica — Lógica del Classifier

```python
# Primario — código UNSPSC (más confiable)
unspsc_cd.startswith(("42", "51", "53", "85", "41"))

# Secundario — keyword match en cartelnm
KEYWORDS = [
  "medicamento", "fármaco", "vacuna", "insulina", "antibiótico",
  "tomógrafo", "resonancia", "ventilador", "desfibrilador",
  "jeringa", "catéter", "sutura", "reactivo", "PCR",
  "gases medicinales", "instrumental laparoscópico", ...
]

# Resultado → categoria
MEDICAMENTO | EQUIPAMIENTO | INSUMO | SERVICIO
```

---

## App Routes

```
/                     → redirect → /dashboard (protected)
/dashboard            → DashboardPage (protected)
/licitaciones         → LicitacionesPage (protected; still uses view — pending update)
/licitaciones/[id]    → LicitacionDetailPage, id = instcartelno (protected)
/auth/login           → LoginPage (public)
/auth/callback        → code exchange for magic link/OAuth (public)
/alertas              → ⏳ notification inbox — all new licitaciones medicas, newest first
                         each card links to /licitaciones/[instcartelno]
/precios              → ⏳ not built
```

---

## Known Issues / Gotchas

```
1. resumen_por_categoria retorna NUMERIC como string — siempre Number(r.monto_crc ?? 0)
2. currency_type: algunos rows tienen "₡" en vez de "CRC" — normalizar en display
3. es_medica=true con categoria=null (~44 rows) — excluir con .not("categoria","is",null)
4. licitaciones_activas (view) no expone id — licitaciones/page.tsx sigue usándola; links deben usar instcartelno
5. licitaciones/page.tsx: migrar query a licitaciones_medicas para consistencia
6. StatCard "nuevas esta semana" usa created_at, no biddoc_start_dt — puede incluir re-runs
7. alertas_config en producción: tabla existente con columnas reales = id, user_id, keywords[],
   categorias[], unspsc[], canal[], activo. NO tiene: nombre, instituciones, monto_min, monto_max.
   El type AlertaConfig en types.ts tiene campos extra — solo usar para futura feature de búsqueda.
8. alertas_enviadas NO existe en producción — ignorar cualquier referencia en documentación antigua.
9. /alertas page y actions.ts: actualmente implementados como CRUD de reglas (incorrecto).
   Pendiente reescribir como notification inbox que consulta licitaciones_medicas directamente.
```