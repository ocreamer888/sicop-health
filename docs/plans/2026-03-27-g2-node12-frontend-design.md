# G2 — Node 12 Frontend Design

**Date:** 2026-03-27
**Scope:** `types.ts` + `page.tsx` (Node 12 section)

## Problem

Node 12 is a placeholder stub. Two data sources are now populated:
- `licitaciones_medicas.fecha_adj_firme` + `desierto` (migration 010, AF report)
- `da_ofertas` table (384 rows, 60-day backfill, O report)

## Approach: Separate fetch, inline render (Option B)

- `getLicitacion` already does `select("*")` — new columns come automatically
- Add `getOfertas(instcartelno)` as a second server fetch
- Fetch both with `Promise.all` in the page component
- Render competitor table inline in Node 12 JSX (no new component file)
- Keep `Licitacion` type flat — `da_ofertas` is a page-only concern

## Types

Add to `Licitacion` interface in `types.ts`:
```typescript
fecha_adj_firme: string | null
desierto: boolean
```

Add local type in `page.tsx`:
```typescript
interface DaOferta {
  suppliernm: string | null
  suppliercd: string | null
  elegible: boolean | null
  orden_merito: number | null
  fecha_apertura: string | null
}
```

## Data Fetching

```typescript
async function getOfertas(instcartelno: string): Promise<DaOferta[]> {
  const supabase = await createClient()
  const { data } = await supabase
    .from("da_ofertas")
    .select("suppliernm, suppliercd, elegible, orden_merito, fecha_apertura")
    .eq("instcartelno", instcartelno)
    .order("orden_merito", { ascending: true, nullsFirst: false })
  return (data ?? []) as DaOferta[]
}
```

Both fetched concurrently:
```typescript
const [l, ofertas] = await Promise.all([getLicitacion(id), getOfertas(id)])
```

## Node 12 Status Logic

```
desierto === true              → "blocked"
fecha_adj_firme || ofertas.length > 0 → "active"
otherwise                     → "pendiente"
```

## Node 12 Content

1. **Desierto badge** — when `desierto === true`, show warning label before any other content
2. **Adj. firme date** — when `fecha_adj_firme` is set, show "Adj. firme: [formatted date]"
3. **Competitor table** — when `ofertas.length > 0`:
   - Columns: Proveedor | Cédula | Elegible | Orden de Mérito | Fecha Apertura
   - `elegible`: green "Sí" / red "No" / grey "–"
   - `orden_merito`: number or "–"
   - `fecha_apertura`: formatted date or "–"
4. **Fallback** — "Sin datos de participación disponibles" when nothing

## Files Changed

- `apps/web/src/lib/types.ts` — two new fields on `Licitacion`
- `apps/web/src/app/licitaciones/[id]/page.tsx` — `DaOferta` type, `getOfertas`, `Promise.all`, Node 12 JSX
