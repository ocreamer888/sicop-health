# SICOP Health Intelligence

Plataforma SaaS B2B que extrae, clasifica y monitorea licitaciones de medicamentos y tecnología médica del sistema de compras públicas de Costa Rica (SICOP), entregando inteligencia accionable a proveedores del sector salud.

---

## Stack Tecnológico

| Capa | Tecnología | Responsabilidad |
|---|---|---|
| Frontend | Next.js 15 (App Router) + Tailwind CSS | UI, dashboard, notificaciones |
| Auth | Supabase Auth | Login, sesiones, middleware |
| Base de Datos | Supabase PostgreSQL | Almacenamiento central + RLS |
| Edge Functions | Supabase Edge Functions (Deno) | Notificaciones + envío de email |
| ETL | Python 3.12 + httpx + pandas | Extracción y clasificación de SICOP |
| Cron | GitHub Actions | Ejecuta ETL cada hora |
| Notificaciones | Resend (email) · WhatsApp (pendiente, proveedor TBD) | Alertas a usuarios |
| Deploy Frontend | Vercel | Hosting del web app |
| Fuente de Datos | SICOP Datos Abiertos | CSV público sin autenticación |

---

## Estructura del Proyecto

```
sicop-health/
│
├── apps/
│   └── web/                            # Next.js 15 (App Router)
│       └── src/
│           ├── app/
│           │   ├── auth/               # Login, forgot-password, invite, reset
│           │   ├── dashboard/          # Métricas y resumen
│           │   ├── licitaciones/       # Tabla de licitaciones con filtros
│           │   └── alertas/            # Centro de notificaciones
│           │       ├── page.tsx        # Inbox de notificaciones
│           │       ├── actions.ts      # Server action: getNotificaciones()
│           │       ├── notificacion-card.tsx
│           │       └── alerta-form.tsx # Reservado para búsqueda avanzada
│           ├── components/
│           │   └── nav.tsx             # Navegación global
│           └── lib/
│               ├── types.ts            # Tipos TypeScript centralizados
│               └── supabase/           # Clientes server/client/middleware
│
├── supabase/
│   ├── migrations/
│   │   ├── 001_initial_schema.sql
│   │   ├── 002_complete_schema.sql
│   │   ├── 003_schema_v2.sql
│   │   ├── 004_rls.sql                 # Row Level Security
│   │   └── 005_notificaciones.sql      # Tabla de notificaciones ← correr en prod
│   └── functions/
│       ├── notify-new-licitacion/      # Webhook handler: detecta nuevas licitaciones
│       │   └── index.ts
│       └── send-email/                 # Envía email via Resend
│           └── index.ts
│
├── services/
│   └── etl/                            # Python ETL pipeline
│       ├── main.py
│       ├── fetcher.py
│       ├── parser.py
│       ├── classifier.py
│       ├── uploader.py
│       └── requirements.txt
│
├── docs/
│   └── plans/                          # Documentos de diseño
│
├── .github/
│   └── workflows/
│       └── etl-cron.yml                # ETL cada hora
│
├── PROJECT.md                          # Contexto técnico completo
├── TASKS.md                            # Lista de tareas y blockers
└── README.md
```

---

## Flujo de Datos

```
GitHub Actions (cada hora)
  → ETL Python: fetcher → parser → classifier → uploader
  → INSERT en licitaciones_medicas (Supabase)
  → DB Webhook dispara notify-new-licitacion (Edge Function)
      → Verifica: es_medica=true AND estado IN (Publicado, Modificado)
      → INSERT en notificaciones (dedup por instcartelno)
      → listUsers() → send-email por cada usuario (Resend)
      → // TODO: WhatsApp (proveedor pendiente)

Usuario en /alertas
  → Lee tabla notificaciones JOIN licitaciones_medicas
  → Ve cards con título, institución, categoría, monto, cierre
  → Click "Ver licitación" → /licitaciones/{instcartelno}
```

---

## Setup

### 1. Supabase

1. Crea un proyecto en [supabase.com](https://supabase.com)
2. En el SQL Editor, ejecuta las migraciones en orden:
   ```
   001_initial_schema.sql
   002_complete_schema.sql
   003_schema_v2.sql
   004_rls.sql
   005_notificaciones.sql   ← tabla del centro de notificaciones
   ```
3. Obtén las credenciales desde Settings → API:
   - Project URL
   - `anon` key (frontend)
   - `service_role` key (ETL + Edge Functions)

### 2. Frontend

```bash
cd apps/web
cp .env.example .env.local
# Editar .env.local con credenciales de Supabase
npm install
npm run dev
```

Disponible en `http://localhost:3000`

### 3. ETL

```bash
cd services/etl
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Editar .env con SUPABASE_URL y SUPABASE_SERVICE_KEY
python main.py
```

### 4. Edge Functions (requiere dominio propio para email)

> **Blocker:** Resend requiere dominio verificado. No se puede usar con subdominios de Vercel.
> Ver checklist completo en `TASKS.md → Pending — Blocked`.

```bash
# Una vez que tengas dominio y CLI de Supabase instalado:
supabase functions deploy notify-new-licitacion --no-verify-jwt
supabase functions deploy send-email --no-verify-jwt
supabase secrets set RESEND_API_KEY=re_xxx SITE_URL=https://tu-dominio.com
```

Luego crear el DB Webhook en Supabase Dashboard → Database → Webhooks:
- Tabla: `licitaciones_medicas` · Evento: `INSERT`
- URL: `https://<project-ref>.supabase.co/functions/v1/notify-new-licitacion`
- Header: `Authorization: Bearer <SERVICE_ROLE_KEY>`

### 5. GitHub Actions (Cron ETL)

En Settings → Secrets → Actions del repo, agrega:
- `SUPABASE_URL`
- `SUPABASE_SERVICE_KEY`

---

## Comandos Útiles

```bash
# Frontend
cd apps/web
npm run dev        # Desarrollo local
npm run build      # Build de producción
npm run lint       # Linting

# ETL
cd services/etl
python main.py     # Ejecutar pipeline completo
```

---

## Estado Actual

| Área | Estado |
|---|---|
| Auth (login, forgot-password, invite, reset) | ✅ Completo |
| Dashboard con métricas | ✅ Completo |
| Tabla `/licitaciones` con filtros | ✅ Completo |
| Centro de notificaciones `/alertas` | ✅ UI completa |
| Edge function `notify-new-licitacion` | ✅ Código listo, pendiente deploy |
| Edge function `send-email` | ✅ Código listo, bloqueado por dominio |
| DB Webhook configurado | ⏳ Pendiente |
| Migración `005_notificaciones.sql` en prod | ⏳ Pendiente |
| WhatsApp | ⏳ Proveedor por definir |

---

## Licencia

Propietaria — SICOP Health Intelligence
