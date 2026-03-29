# G8 — WhatsAppButton presupuesto_estimado Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** WhatsAppButton shows `presupuesto_estimado` (DA budget figure) when available, falling back to `monto_colones`.

**Architecture:** Add two optional props to the component; resolve amount + currency with `??` fallback; update the single callsite to pass the new props.

**Tech Stack:** Next.js 15, TypeScript, React (no state, pure props)

---

### Task 1: Update WhatsAppButton component

**Files:**
- Modify: `apps/web/src/components/workflow/WhatsAppButton.tsx`

**Step 1: Add new props to the interface**

Replace the existing `WhatsAppButtonProps` interface:

```typescript
interface WhatsAppButtonProps {
  instcartelno: string
  cartelnm: string | null
  instnm: string | null
  biddocEndDt: string | null
  montoColones: number | null
  currencyType: string | null
  presupuestoEstimado: number | null
  monedaPresupuesto: string | null
}
```

**Step 2: Update the function signature**

Add the two new params to the destructured props:

```typescript
export function WhatsAppButton({
  instcartelno,
  cartelnm,
  instnm,
  biddocEndDt,
  montoColones,
  currencyType,
  presupuestoEstimado,
  monedaPresupuesto,
}: WhatsAppButtonProps) {
```

**Step 3: Resolve amount and currency with fallback**

Replace the `if (montoColones)` block with:

```typescript
  const monto = presupuestoEstimado ?? montoColones
  const moneda = monedaPresupuesto ?? currencyType

  if (monto) {
    const symbol = moneda === "USD" ? "$" : "₡"
    lines.push(`💰 *Monto estimado:* ${symbol}${monto.toLocaleString("es-CR")}`)
  }
```

**Step 4: Verify TypeScript compiles**

```bash
cd apps/web && npx tsc --noEmit
```

Expected: no errors on WhatsAppButton.tsx

---

### Task 2: Update callsite in detail page

**Files:**
- Modify: `apps/web/src/app/licitaciones/[id]/page.tsx:238-245`

**Step 1: Pass new props**

Replace the `<WhatsAppButton` block (currently lines 238–245):

```tsx
<WhatsAppButton
  instcartelno={l.instcartelno}
  cartelnm={l.cartelnm}
  instnm={l.instnm}
  biddocEndDt={l.biddoc_end_dt}
  montoColones={l.monto_colones}
  currencyType={l.currency_type}
  presupuestoEstimado={l.presupuesto_estimado}
  monedaPresupuesto={l.moneda_presupuesto}
/>
```

**Step 2: Verify TypeScript compiles**

```bash
cd apps/web && npx tsc --noEmit
```

Expected: no errors

**Step 3: Commit**

```bash
git add apps/web/src/components/workflow/WhatsAppButton.tsx \
        apps/web/src/app/licitaciones/[id]/page.tsx
git commit -m "feat(g8): WhatsAppButton prefers presupuesto_estimado over monto_colones"
```
