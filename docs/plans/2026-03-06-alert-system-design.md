# Alert System Design
_Date: 2026-03-06_

## Overview

Build an end-to-end alert system for SICOP Health Intelligence that:
1. Lets authenticated users configure keyword/category/institution filters as named alerts
2. Automatically evaluates new tenders against those filters via Supabase Database Webhook
3. Sends email notifications via Resend when a match is found

---

## Architecture

```
INSERT into licitaciones_medicas (ETL)
        │
        ▼
Supabase Database Webhook (INSERT event)
        │  { instcartelno, record }
        ▼
Edge Function: match-alerts
  ├─ Query all active alertas_config rows
  ├─ Evaluate each alert rule against the tender
  │    ├─ keywords: any match in cartelnm (case-insensitive)
  │    ├─ categorias: exact match if filter is set
  │    ├─ instituciones: inst_code match if filter is set
  │    └─ monto range: check monto_colones if min/max set
  ├─ For each match:
  │    ├─ INSERT into alertas_enviadas (UNIQUE constraint prevents duplicates)
  │    └─ Invoke send-email edge function
        │
        ▼
Edge Function: send-email
  ├─ Input: { user_email, alerta_nombre, licitacion }
  ├─ Render HTML email (design system tokens)
  └─ POST to Resend API
```

---

## Database (tables already deployed)

### `alertas_config`
| Column | Type | Description |
|--------|------|-------------|
| id | UUID PK | |
| user_id | UUID FK auth.users | Owner |
| nombre | TEXT | Alert display name |
| keywords | TEXT[] | ["insulina", "metformina"] — OR logic |
| categorias | TEXT[] | ["MEDICAMENTO"] — if empty, all categories |
| instituciones | TEXT[] | inst_code values — if empty, all institutions |
| monto_min | NUMERIC | Optional lower bound |
| monto_max | NUMERIC | Optional upper bound |
| canales | TEXT[] | ["email"] — whatsapp deferred |
| activo | BOOLEAN | Enable/disable without deleting |
| created_at / updated_at | TIMESTAMPTZ | |

### `alertas_enviadas`
Dedup log. UNIQUE on `(alerta_id, instcartelno, canal)`.

---

## Edge Functions

### `supabase/functions/match-alerts/index.ts`
- **Trigger**: Supabase Database Webhook on INSERT into `licitaciones_medicas`
- **Auth**: Service role key (set in Supabase Secrets)
- **Input**: Webhook payload containing the new row
- **Logic**:
  1. Parse `instcartelno` and tender fields from payload
  2. Fetch all `alertas_config` where `activo = true`
  3. For each alert, evaluate match:
     - keywords: `cartelnm.toLowerCase()` includes any keyword
     - categorias: if non-empty, `categoria` must be in array
     - instituciones: if non-empty, `inst_code` must be in array
     - monto: if `monto_min` set, `monto_colones >= monto_min`; similarly for max
  4. For each match: attempt insert into `alertas_enviadas` (ignore duplicate conflict)
  5. If insert succeeded (not duplicate): call `send-email` function

### `supabase/functions/send-email/index.ts`
- **Trigger**: Called by `match-alerts` (internal HTTP call within Supabase)
- **Auth**: Service role key
- **Input**: `{ user_email, alerta_nombre, licitacion: { instcartelno, cartelnm, instnm, categoria, monto_colones, currency_type, biddoc_end_dt } }`
- **Resend API**: POST to `https://api.resend.com/emails`
- **Template**: HTML email with SICOP Health branding

---

## Frontend: `/alertas` page

### Route
`apps/web/src/app/alertas/page.tsx` — Client Component (`"use client"`)

### Components
- `AlertaCard` — displays an alert with toggle, edit, delete actions
- `AlertaForm` — create/edit form (slide-in drawer or inline)
- Empty state component

### Form Fields
| Field | Input | Notes |
|-------|-------|-------|
| Nombre | text | Required |
| Keywords | tag input | Type + Enter to add, removable chips |
| Categorías | multi-checkbox | MEDICAMENTO, EQUIPAMIENTO, INSUMO, SERVICIO |
| Instituciones | tag input | Institution codes |
| Monto mínimo | number | Optional |
| Monto máximo | number | Optional |
| Canales | checkbox | Email only; WhatsApp grayed out ("próximamente") |
| Activo | toggle | Default true |

### Server Actions (`app/alertas/actions.ts`)
- `createAlerta(data)` — INSERT
- `updateAlerta(id, data)` — UPDATE
- `deleteAlerta(id)` — DELETE
- `toggleAlerta(id, activo)` — UPDATE activo

### Nav update
Add "Alertas" link to `nav.tsx` with Bell icon.

---

## Email Template Design
- Dark background `#1a1f1a`
- Header with SICOP Health logo text
- Green accent divider `#84a584`
- Alert name + matching tender details
- CTA button "Ver Licitación" linking to `/licitaciones/[instcartelno]`
- Footer with unsubscribe note

---

## Setup Steps (Manual)
1. Create Resend account at resend.com — get API key
2. Add `RESEND_API_KEY` to Supabase Edge Function Secrets
3. Deploy both edge functions via `supabase functions deploy`
4. Configure Supabase Database Webhook in Dashboard:
   - Table: `licitaciones_medicas`, Event: INSERT
   - URL: `https://[project-ref].supabase.co/functions/v1/match-alerts`
   - HTTP headers: `Authorization: Bearer [service_role_key]`

---

## Out of Scope (deferred)
- WhatsApp notifications
- Alert history/log view in UI
- Rate limiting per user on alerts created
- Digest emails (immediate only)
