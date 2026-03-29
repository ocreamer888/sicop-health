# G8 — WhatsAppButton: prefer presupuesto_estimado

**Date:** 2026-03-27
**Scope:** Single component + one callsite

## Problem

`WhatsAppButton` shows `monto_colones` (awarded amount, post-adjudication) as "Monto estimado". At offer time the right figure is `presupuesto_estimado` (from DA SC report), which is populated for ~4,664 procedures.

## Design

Add two props to `WhatsAppButton`:
- `presupuestoEstimado: number | null`
- `monedaPresupuesto: string | null`

Amount line resolves as: `presupuestoEstimado ?? montoColones`, currency as: `monedaPresupuesto ?? currencyType`. Label stays "Monto estimado".

Callsite (`apps/web/src/app/licitaciones/[id]/page.tsx`) passes `presupuestoEstimado={l.presupuesto_estimado}` and `monedaPresupuesto={l.moneda_presupuesto}`.

## Files changed

- `apps/web/src/components/workflow/WhatsAppButton.tsx` — new props + fallback logic
- `apps/web/src/app/licitaciones/[id]/page.tsx` — pass new props at callsite
