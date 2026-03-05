<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# crea un documento md sobre el diagrama de la arquitectura del app

Aquí está el documento completo:

```markdown
# SICOP Health Intelligence — Arquitectura del Sistema

## Visión General

Plataforma SaaS B2B que extrae, clasifica y monitorea licitaciones de
medicamentos y tecnología médica del sistema de compras públicas de Costa
Rica (SICOP), entregando inteligencia accionable a proveedores del sector salud.

---

## Stack Tecnológico

| Capa | Tecnología | Responsabilidad |
|---|---|---|
| Frontend | Next.js 16.1 + React + Tailwind | UI, dashboard, alertas |
| Auth | Supabase Auth | Login, sesiones, roles |
| Base de Datos | Supabase PostgreSQL | Almacenamiento central |
| Realtime | Supabase Realtime | Actualizaciones en vivo al UI |
| ETL | Python 3.12 + httpx + pandas | Extracción y limpieza de SICOP |
| Cron | GitHub Actions | Ejecuta ETL cada hora |
| Notificaciones | Resend (email) + WhatsApp API | Alertas a usuarios |
| Deploy Frontend | Vercel | Hosting del web app |
| Fuente de Datos | SICOP Datos Abiertos | CSV público sin autenticación |

---

## Diagrama de Arquitectura

```

┌─────────────────────────────────────────────────────────────────────┐
│                        FUENTE DE DATOS                              │
│                                                                     │
│   sicop.go.cr/moduloBid/report/RE_DatosAbiertosConcursosView.jsp   │
│   └── CSV público · sin auth · sin anti-bot · sin rate limit       │
└────────────────────────────┬────────────────────────────────────────┘
│ HTTP GET (cada hora)
▼
┌─────────────────────────────────────────────────────────────────────┐
│                     ETL PIPELINE (Python)                           │
│                     services/etl/                                   │
│                                                                     │
│  ┌──────────┐   ┌──────────┐   ┌─────────────┐   ┌─────────────┐  │
│  │ fetcher  │→  │ parser   │→  │ classifier  │→  │  uploader   │  │
│  │          │   │          │   │             │   │             │  │
│  │ httpx    │   │ pandas   │   │ UNSPSC      │   │ supabase-py │  │
│  │ GET CSV  │   │ normalize│   │ 42/51/53/85 │   │ upsert rows │  │
│  │          │   │ clean    │   │ + keywords  │   │             │  │
│  └──────────┘   └──────────┘   └─────────────┘   └──────┬──────┘  │
│                                                          │         │
│  Trigger: GitHub Actions cron '0 * * * *'               │         │
└─────────────────────────────────────────────────────────┼─────────┘
│ REST API
▼
┌─────────────────────────────────────────────────────────────────────┐
│                         SUPABASE                                    │
│                                                                     │
│  ┌─────────────────────┐   ┌──────────────────┐                    │
│  │    PostgreSQL DB     │   │   Supabase Auth  │                    │
│  │                     │   │                  │                    │
│  │ licitaciones_medicas│   │ usuarios         │                    │
│  │ precios_historicos  │   │ roles            │                    │
│  │ proveedores         │   │ sesiones         │                    │
│  │ alertas_config      │   └──────────────────┘                    │
│  │ instituciones_salud │                                           │
│  └──────────┬──────────┘   ┌──────────────────┐                    │
│             │              │ Supabase Realtime│                    │
│             └─────────────►│ broadcast nuevas │                    │
│                            │ licitaciones     │                    │
│                            └────────┬─────────┘                    │
└─────────────────────────────────────┼───────────────────────────────┘
│ Supabase JS SDK
┌─────────────────┴─────────────────┐
│                                   │
▼                                   ▼
┌───────────────────────────────┐   ┌───────────────────────────────┐
│     FRONTEND (Next.js)        │   │     NOTIFICACIONES            │
│     apps/web/                 │   │     services/etl/notifier.py  │
│                               │   │                               │
│  /dashboard                   │   │  Email (Resend)               │
│  └── métricas + overview      │   │  └── nuevas licitaciones      │
│                               │   │  └── cambios de estado        │
│  /licitaciones                │   │  └── vencimientos             │
│  └── tabla filtrable          │   │                               │
│  └── búsqueda por keyword     │   │  WhatsApp API                 │
│  └── detalle de cartel        │   │  └── alertas críticas         │
│                               │   │                               │
│  /precios/:item               │   └───────────────────────────────┘
│  └── histórico por producto   │
│  └── gráfica de tendencia     │
│                               │
│  /proveedores                 │
│  └── ranking por categoría    │
│  └── win rate + precios       │
│                               │
│  /alertas                     │
│  └── config por usuario       │
│  └── keywords + UNSPSC        │
│                               │
│  Deploy: Vercel               │
└───────────────────────────────┘

```

---

## Flujo de Datos Completo

```

1. GitHub Actions dispara el ETL cada hora
│
▼
2. fetcher.py → GET sicop.go.cr → CSV raw
│
▼
3. parser.py → pandas DataFrame normalizado
    - Limpia encoding (UTF-8)
    - Parsea fechas al formato ISO
    - Normaliza montos a NUMERIC
    - Extrae numero_procedimiento como ID único
│
▼
4. classifier.py → Filtro dual
    - PRIMARIO: clasificacion.startswith(["42","51","53","85","41"])
    - SECUNDARIO: keyword match en descripcion
    - Asigna categoria: MEDICAMENTO | EQUIPAMIENTO | INSUMO | SERVICIO
│
▼
5. uploader.py → Supabase REST API
    - upsert con conflict en numero_procedimiento (no duplicados)
    - Detecta filas NUEVAS vs ACTUALIZADAS
    - Detecta cambios de estado (Publicado → Adjudicado, etc.)
│
├──→ INSERT nuevas → trigger notifier.py
└──→ UPDATE estado → trigger notifier.py (si config activa)
│
▼
6. notifier.py → Resend + WhatsApp
    - Consulta alertas_config de cada usuario
    - Match contra categorías y keywords configurados
    - Envía solo si hay match (no spam)
│
▼
7. Supabase Realtime → Frontend React
    - Dashboard se actualiza sin refresh
    - Badge de notificaciones en vivo
```

---

## Schema de Base de Datos

```sql
-- Tabla principal
CREATE TABLE licitaciones_medicas (
  id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  numero_procedimiento  TEXT UNIQUE NOT NULL,
  descripcion           TEXT,
  institucion           TEXT,
  tipo_procedimiento    TEXT,        -- LN, LA, LD, SI, etc.
  clasificacion_unspsc  TEXT,        -- Código UNSPSC raw
  categoria             TEXT,        -- MEDICAMENTO | EQUIPAMIENTO | etc.
  monto_colones         NUMERIC,
  adjudicatario         TEXT,
  estado                TEXT,        -- Publicado | Adjudicado | Desierto
  fecha_tramite         DATE,
  fecha_limite_oferta   DATE,
  raw_data              JSONB,       -- Fila completa del CSV
  created_at            TIMESTAMPTZ  DEFAULT NOW(),
  updated_at            TIMESTAMPTZ  DEFAULT NOW()
);

-- Histórico de precios por ítem
CREATE TABLE precios_historicos (
  id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  descripcion_item      TEXT,
  clasificacion_unspsc  TEXT,
  institucion           TEXT,
  proveedor             TEXT,
  precio_unitario       NUMERIC,
  cantidad              NUMERIC,
  unidad                TEXT,
  numero_procedimiento  TEXT REFERENCES licitaciones_medicas(numero_procedimiento),
  fecha                 DATE
);

-- Configuración de alertas por usuario
CREATE TABLE alertas_config (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id     UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  keywords    TEXT[],          -- ["insulina", "metformina"]
  categorias  TEXT[],          -- ["MEDICAMENTO", "EQUIPAMIENTO"]
  unspsc      TEXT[],          -- ["5110", "4214"]
  canal       TEXT[],          -- ["email", "whatsapp"]
  activo      BOOLEAN DEFAULT TRUE,
  created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- Índices para performance
CREATE INDEX idx_licitaciones_fecha     ON licitaciones_medicas(fecha_tramite DESC);
CREATE INDEX idx_licitaciones_categoria ON licitaciones_medicas(categoria);
CREATE INDEX idx_licitaciones_estado    ON licitaciones_medicas(estado);
CREATE INDEX idx_licitaciones_inst      ON licitaciones_medicas(institucion);
CREATE INDEX idx_precios_descripcion    ON precios_historicos(descripcion_item);
```


---

## Estructura del Repositorio

```
sicop-health/
│
├── apps/
│   └── web/                        # Next.js + React + Tailwind
│       ├── app/
│       │   ├── (auth)/login/
│       │   ├── dashboard/
│       │   ├── licitaciones/
│       │   │   └── [id]/
│       │   ├── precios/
│       │   └── alertas/
│       ├── components/
│       │   ├── ui/                 # Componentes base Tailwind
│       │   ├── LicitacionesTable/
│       │   ├── PreciosChart/
│       │   └── AlertasForm/
│       ├── lib/
│       │   ├── supabase.ts
│       │   └── utils.ts
│       └── package.json
│
├── services/
│   └── etl/                        # Python ETL
│       ├── main.py                 # Orquestador principal
│       ├── fetcher.py              # GET SICOP CSV
│       ├── parser.py               # Normalización con pandas
│       ├── classifier.py           # Filtro UNSPSC + keywords
│       ├── uploader.py             # Escritura en Supabase
│       ├── notifier.py             # Email + WhatsApp
│       ├── requirements.txt
│       └── .env.example
│
├── supabase/
│   ├── migrations/
│   │   └── 001_initial_schema.sql
│   └── config.toml
│
├── .github/
│   └── workflows/
│       └── etl-cron.yml            # Cron cada hora
│
└── README.md
```


---

## Ambientes

| Ambiente | Frontend | ETL | Base de Datos |
| :-- | :-- | :-- | :-- |
| **Local** | `next dev` (localhost:3000) | `python main.py` manual | Supabase local CLI |
| **Staging** | Vercel Preview | GitHub Actions (branch develop) | Supabase proyecto staging |
| **Producción** | Vercel Production | GitHub Actions (branch main) | Supabase proyecto prod |


---

## Roadmap de Desarrollo

### Semana 1 — ETL Base

- [ ] Setup monorepo + entorno Python
- [ ] `fetcher.py` — descarga CSV de SICOP
- [ ] `parser.py` — normalización con pandas
- [ ] `classifier.py` — filtro UNSPSC médico
- [ ] `uploader.py` — upsert en Supabase
- [ ] Schema SQL inicial en Supabase
- [ ] Test manual: `python main.py`


### Semana 2 — Dashboard Base

- [ ] Setup Next.js + Tailwind + Supabase client
- [ ] Auth con Supabase (login/logout)
- [ ] `/licitaciones` — tabla con filtros básicos
- [ ] `/dashboard` — conteos y métricas simples
- [ ] Deploy en Vercel


### Semana 3 — Alertas + Cron

- [ ] Schema `alertas_config`
- [ ] `notifier.py` — integración Resend
- [ ] `/alertas` — UI para configurar keywords
- [ ] `etl-cron.yml` — GitHub Actions cada hora
- [ ] Test end-to-end del pipeline completo


### Semana 4 — Inteligencia de Precios

- [ ] Schema `precios_historicos`
- [ ] `/precios/:item` — gráfica histórica
- [ ] `/proveedores` — ranking + win rate
- [ ] Pulir UI + mobile responsive
- [ ] Beta con 2-3 usuarios reales

---

*Documento generado: Marzo 2026*
*Stack: Next.js 14 · Supabase · Python 3.12 · GitHub Actions · Vercel*

```

Puedes copiar esto directamente como `ARCHITECTURE.md` en la raíz del repo. ¿Arrancamos con el `001_initial_schema.sql` o con el `fetcher.py`?```

