# Workflow-Driven Detail Page Refactor — Design
**Date:** 2026-03-25
**Scope:** Frontend only. ETL and DB schema unchanged.

---

## 1. Goal

Restructure the tender detail page (`/licitaciones/[id]`) to mirror the team's 12-node decision-making workflow. The list page gains a filter bar. Visual design language is preserved throughout.

---

## 2. Architecture

### What changes
- `apps/web/src/app/licitaciones/[id]/page.tsx` — full rebuild
- `apps/web/src/app/licitaciones/page.tsx` — add filter bar above existing table
- New components:
  - `src/components/workflow/WorkflowProgress.tsx`
  - `src/components/workflow/WorkflowNode.tsx`
  - `src/components/workflow/DeadlineCountdown.tsx`
  - `src/components/workflow/WhatsAppButton.tsx`
- `src/lib/types.ts` — add `WorkflowNodeStatus` type

### What stays untouched
- `LicitacionesTable` component — zero changes, visual style preserved
- Dashboard, Alertas, Notifications pages
- ETL pipeline (`services/etl/`)
- DB schema and Supabase queries

---

## 3. Detail Page Layout

```
┌─────────────────────────────────────────────────────┐
│  ← Volver   [INSTCARTELNO]  [CATEGORIA]  [ESTADO]   │
│  TITLE (cartelnm, truncated with ellipsis)           │
├─────────────────────────────────────────────────────┤
│  WorkflowProgress bar                               │
│  "Nodos con datos: ██████░░░░░░  3 / 6"             │
│  (turns red + "Oportunidad descartada" if blocked)  │
├────────────────────────┬────────────────────────────┤
│  LEFT col-span-2       │  RIGHT sidebar             │
│                        │                            │
│  Node 1  Institución   │  Institución card          │
│  Node 2  Presupuesto   │  DeadlineCountdown         │
│  Node 3  Participación │  "Purseguir" toggle        │
│  Node 4  Elegibilidad  │                            │
│  Node 5  Tiempo fabric │                            │
│  Node 6  Cant./Precios │                            │
│  Node 7  Contacto      │                            │
│  Node 8-9 Margen       │                            │
│  Node 10 Riesgo dossier│                            │
│  Node 11 Registro      │                            │
│  Node 12 Historial     │                            │
└────────────────────────┴────────────────────────────┘
```

---

## 4. WorkflowNode Component

### Visual design
- Card: `rounded-[24px] bg-[#1a1f1a] p-6` (existing pattern)
- Status indicator: 10px filled circle, **top-right corner** of card
- No border changes — circle is the sole status signal

### Circle colors (existing palette)
| Status | Color | Hex |
|---|---|---|
| `active` | sage green | `#84a584` |
| `partial` | warm amber | `#b5a88a` |
| `blocked` | muted red | `#a58484` |
| `pendiente` | dim | `#3d4d45` |

### Node states
- **active** — data fully available, populated
- **partial** — data exists but incomplete (e.g. deadline known but no quantities)
- **blocked** — pre-qualified gate triggered (Node 3 = pre-qualified only)
- **pendiente** — data gap, shows gap message with lock icon

---

## 5. Node-by-Node Specification

| Node | Label | State | Data source | Display |
|---|---|---|---|---|
| 1 | Institución + Fecha | active | `instnm`, `biddoc_start_dt` | Institution name, publication date |
| 2 | Presupuesto estimado | pendiente | Gap — JSP only | "Pendiente: dato no disponible en API" |
| 3 | Tipo de participación | pendiente | Gap — JSP only | "Pendiente: requiere Datos Abiertos" |
| 4 | Elegibilidad | pendiente | Depends on Node 3 | "No aplica" if Node 3 = open; "¿Estás pre-calificado?" if Node 3 = pre-qualified |
| 5 | Tiempo para fabricar | partial | `biddoc_end_dt` | Deadline date + DeadlineCountdown |
| 6 | Cantidades y precios | pendiente | Gap — JSP only | "Pendiente: líneas de cartel" |
| 7 | Contactar fabricante | partial | All available fields | WhatsAppButton pre-filled with spec |
| 8-9 | Margen / Dossier | pendiente | External process | "Proceso externo — 15-22 días estimados" |
| 10 | Riesgo dossier | partial | `biddoc_end_dt` | DeadlineCountdown with ⚠️ if < 22 days |
| 11 | Registro | pendiente | External | Placeholder + link |
| 12 | Historial precios | pendiente | `precioshistoricos` empty | "Pendiente: datos históricos" |

### Node 3 gate logic
```
Node 3: Tipo participación
  ├── Abierto     → Node 4: "No aplica — participación abierta"  → continue
  └── Pre-calificado → Node 4: "¿Estás pre-calificado?"
                          ├── Sí → continue
                          └── No → BLOCKED: red banner + progress bar turns red
                                   "Oportunidad descartada"
  └── Pendiente   → Node 4: greyed out, locked
```

---

## 6. WorkflowProgress Component

- Horizontal bar below the page header
- Progress counts nodes 1–6 (pre-decision nodes only)
- A node counts as "complete" if state is `active` or `partial`
- Currently every tender scores **3/6** (nodes 1, 5, 7 have data — node 7 is treated as partial)
- If Node 3 = pre-qualified AND user not qualified: bar turns red, label = "Oportunidad descartada"

---

## 7. DeadlineCountdown Component

Used in Node 5 (time to manufacture) and Node 10 (dossier risk):

| Days remaining | Color | Label |
|---|---|---|
| > 22 | `#84a584` green | "X días restantes" |
| 8–22 | `#b5a88a` amber | "⚠️ X días — riesgo dossier" |
| < 8 | `#a58484` red | "🔴 X días — crítico" |
| Past | `#a58484` red | "Vencida" |

---

## 8. WhatsAppButton Component (Node 7)

Pre-filled message template:
```
Licitación: {cartelnm}
Institución: {instnm}
Código: {instcartelno}
Deadline: {biddoc_end_dt formatted}
Monto: {monto_colones} {currency_type}  ← omitted if null
```

Opens `https://wa.me/?text=...` with URL-encoded message.

---

## 9. List Page Filter Bar

Added above the existing `LicitacionesTable` (zero changes to table):

```
[Institución ▾]  [Fecha desde]  [Fecha hasta]  [Categoría ▾]  [Limpiar]
```

- Institution dropdown: distinct `instnm` values from loaded data
- Date range filters on `biddoc_start_dt`
- Categoria dropdown: MEDICAMENTO / EQUIPAMIENTO / INSUMO / SERVICIO
- Client-side filtering — no new API routes or DB queries
- Filter state in component `useState` — no URL params needed

---

## 10. Confirmed Gaps (Pending)

These nodes show "Pendiente" until the following data sources are implemented:

| Node | Blocking gap | Future source |
|---|---|---|
| 2 | No `PRESUPUESTO` on RPT_PUB | `EP_REJ_COQ717.jsp` or `TP_CTJ_POQ001.jsp` scraper |
| 3 | No participation type in REST API | `RE_DatosAbiertosConcursosView.jsp` scraper |
| 6 | No line-item quantities in REST API | `CE_MOD_DATOSABIERTOSVIEW.jsp` CSV download |
| 12 | `precioshistoricos` table empty | `EP_REJ_COQ716.jsp` + Datos Abiertos Reports 5/6 |

---

## 11. Out of Scope

- ETL pipeline changes
- DB schema migrations
- Auth / user profile for Node 4 eligibility check
- Actual WhatsApp API integration (button opens wa.me link only)
- "Pursuing this" toggle persistence (UI only for now, no DB write)
