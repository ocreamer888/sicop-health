# SICOP Health Intelligence

Plataforma SaaS B2B que extrae, clasifica y monitorea licitaciones de medicamentos y tecnología médica del sistema de compras públicas de Costa Rica (SICOP), entregando inteligencia accionable a proveedores del sector salud.

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

## Estructura del Proyecto

```
sicop-health/
│
├── apps/
│   └── web/                        # Next.js + React + Tailwind
│       ├── app/                    # Rutas de la aplicación
│       ├── components/             # Componentes React
│       ├── lib/                    # Utilidades (Supabase client)
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
│   └── migrations/
│       └── 001_initial_schema.sql  # Schema inicial
│
├── .github/
│   └── workflows/
│       └── etl-cron.yml            # Cron cada hora
│
└── README.md
```

## Setup Inicial

### 1. Supabase (Base de Datos y Auth)

1. Crea un proyecto en [Supabase](https://supabase.com)
2. Ejecuta el schema inicial:
   ```bash
   # En el SQL Editor de Supabase, ejecuta:
   # supabase/migrations/001_initial_schema.sql
   ```
3. Obtén las credenciales:
   - Project URL (Settings > API)
   - `anon` key (para frontend)
   - `service_role` key (para ETL)

### 2. Frontend (Next.js)

```bash
cd apps/web

# Crear archivo de environment
cp .env.local.example .env.local
# Editar .env.local con tus credenciales de Supabase

# Instalar dependencias (ya instaladas)
npm install

# Iniciar servidor de desarrollo
npm run dev
```

El frontend estará disponible en http://localhost:3000

### 3. ETL (Python)

```bash
cd services/etl

# Crear virtual environment (opcional pero recomendado)
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Crear archivo de environment
cp .env.example .env
# Editar .env con tus credenciales

# Ejecutar ETL manualmente
python main.py
```

### 4. GitHub Actions (Cron ETL)

1. Ve a Settings > Secrets and variables > Actions en tu repo de GitHub
2. Agrega los siguientes secrets:
   - `SUPABASE_URL`
   - `SUPABASE_SERVICE_KEY`
   - `RESEND_API_KEY` (opcional, para notificaciones)
   - `RESEND_FROM_EMAIL` (opcional)

El ETL se ejecutará automáticamente cada hora.

### 5. Configuración de Notificaciones (Resend)

1. Crea una cuenta en [Resend](https://resend.com)
2. Verifica tu dominio
3. Genera una API key
4. Configura las variables de entorno

## Flujo de Datos

```
1. GitHub Actions dispara el ETL cada hora
│
▼
2. fetcher.py → GET sicop.go.cr → CSV raw
│
▼
3. parser.py → pandas DataFrame normalizado
│
▼
4. classifier.py → Filtro dual (UNSPSC + keywords)
│
▼
5. uploader.py → Supabase REST API
│   ├──→ INSERT nuevas → trigger notifier.py
│   └──→ UPDATE estado → trigger notifier.py
│
▼
6. notifier.py → Resend + WhatsApp
│
▼
7. Supabase Realtime → Frontend React
```

## Categorías UNSPSC Médicas

El sistema clasifica licitaciones con los siguientes códigos UNSPSC:
- `42` - Equipamiento médico
- `51` - Medicamentos y farmacéuticos
- `53` - Insumos médicos
- `85` - Servicios de salud
- `41` - Equipos de laboratorio

## Comandos Útiles

### Frontend
```bash
cd apps/web
npm run dev          # Desarrollo
npm run build        # Build de producción
npm run lint         # Linting
```

### ETL
```bash
cd services/etl
python main.py       # Ejecutar ETL manualmente
python fetcher.py    # Probar solo el fetcher
python parser.py     # Probar solo el parser
```

## Ambientes

| Ambiente | Frontend | ETL | Base de Datos |
| :-- | :-- | :-- | :-- |
| **Local** | `next dev` (localhost:3000) | `python main.py` manual | Supabase local CLI |
| **Staging** | Vercel Preview | GitHub Actions (branch develop) | Supabase proyecto staging |
| **Producción** | Vercel Production | GitHub Actions (branch main) | Supabase proyecto prod |

## Roadmap

### Semana 1 — ETL Base ✅
- [x] Setup monorepo + entorno Python
- [x] `fetcher.py` — descarga CSV de SICOP
- [x] `parser.py` — normalización con pandas
- [x] `classifier.py` — filtro UNSPSC médico
- [x] `uploader.py` — upsert en Supabase
- [x] Schema SQL inicial en Supabase

### Semana 2 — Dashboard Base ⏳
- [ ] Setup Next.js + Tailwind + Supabase client
- [ ] Auth con Supabase (login/logout)
- [ ] `/licitaciones` — tabla con filtros básicos
- [ ] `/dashboard` — conteos y métricas simples
- [ ] Deploy en Vercel

### Semana 3 — Alertas + Cron ⏳
- [ ] `notifier.py` — integración Resend
- [ ] `/alertas` — UI para configurar keywords
- [ ] Test end-to-end del pipeline completo

### Semana 4 — Inteligencia de Precios ⏳
- [ ] Schema `precios_historicos`
- [ ] `/precios/:item` — gráfica histórica
- [ ] `/proveedores` — ranking + win rate
- [ ] Beta con 2-3 usuarios reales

## Licencia

Propietaria - SICOP Health Intelligence

## Contacto

Para soporte o consultas: [tu-email@example.com]
