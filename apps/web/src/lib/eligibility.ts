// apps/web/src/lib/eligibility.ts
// Pure eligibility logic — extracted from page.tsx to be testable

import type { Licitacion, UserProfile } from "./types"

const CATEGORIA_LABELS: Record<string, string> = {
  MEDICAMENTO: "Medicamento",
  EQUIPAMIENTO: "Equipamiento",
  INSUMO: "Insumo",
  SERVICIO: "Servicio",
}

// Maps onboarding institution codes → keywords to match against l.instnm
export const INST_KEYWORDS: Record<string, string[]> = {
  CCSS:       ["CAJA COSTARRICENSE"],
  Hospitales: ["HOSPITAL"],
  INS:        ["INSTITUTO NACIONAL DE SEGUROS"],
  MS:         ["MINISTERIO DE SALUD"],
  Todas:      [], // empty = wildcard
}

export type EligibilityResult =
  | { ok: true }
  | { ok: false; reasons: string[] }
  | { ok: null; reason: "no_profile" | "precal" }

function formatBudget(amount: number, currency: string | null): string {
  const symbol = currency === "USD" ? "$" : "₡"
  return `${symbol}${amount.toLocaleString("es-CR")}`
}

export function checkEligibility(l: Licitacion, profile: UserProfile | null): EligibilityResult {
  if (!profile) return { ok: null, reason: "no_profile" }
  if (l.modalidad_participacion === "Precalificación") return { ok: null, reason: "precal" }

  const reasons: string[] = []

  // Category check — skipped if profile has no categories or licitacion has no category
  if (l.categoria && profile.categorias.length > 0 && !profile.categorias.includes(l.categoria)) {
    reasons.push(`Categoría ${CATEGORIA_LABELS[l.categoria] ?? l.categoria} no está en tu perfil`)
  }

  // Institution check — skipped if "Todas", empty list, or no instnm
  const hasWildcard = profile.instituciones.includes("Todas")
  if (!hasWildcard && profile.instituciones.length > 0 && l.instnm) {
    const instUpper = l.instnm.toUpperCase()
    const matched = profile.instituciones.some(code => {
      const kws = INST_KEYWORDS[code]
      return kws !== undefined && (kws.length === 0 || kws.some(kw => instUpper.includes(kw)))
    })
    if (!matched) reasons.push(`${l.instnm} no está entre tus instituciones objetivo`)
  }

  // Budget check — skipped if either is null/zero
  if (profile.monto_min && l.presupuesto_estimado && l.presupuesto_estimado < profile.monto_min) {
    reasons.push(`Presupuesto ${formatBudget(l.presupuesto_estimado, l.moneda_presupuesto)} está por debajo de tu mínimo configurado`)
  }

  return reasons.length > 0 ? { ok: false, reasons } : { ok: true }
}
