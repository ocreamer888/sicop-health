// apps/web/src/lib/eligibility.test.ts
// Run with: npx tsx --test src/lib/eligibility.test.ts

import { test, describe } from "node:test"
import assert from "node:assert/strict"
import { checkEligibility } from "./eligibility"
import type { Licitacion, UserProfile } from "./types"

// ─── Minimal fixture builders ──────────────────────────────────────────────

function makeLic(overrides: Partial<Licitacion> = {}): Licitacion {
  return {
    id: "test-id",
    instcartelno: "2026XE-000001-0001",
    cartelno: null,
    cartelnm: "Test licitación",
    instnm: "CAJA COSTARRICENSE DE SEGURO SOCIAL",
    inst_code: "0001",
    estado: "Publicado",
    es_medica: true,
    categoria: "MEDICAMENTO",
    procetype: null,
    tipo_procedimiento: "XE",
    typekey: "RPT_PUB",
    modalidad: null,
    excepcion_cd: null,
    cartel_cate: null,
    mod_reason: null,
    unspsc_cd: null,
    supplier_nm: null,
    supplier_cd: null,
    monto_colones: null,
    currency_type: null,
    detalle: null,
    biddoc_start_dt: null,
    biddoc_end_dt: null,
    openbid_dt: null,
    adj_firme_dt: null,
    vigencia_contrato: null,
    unidad_vigencia: null,
    presupuesto_estimado: 100_000_000,
    moneda_presupuesto: "CRC",
    modalidad_participacion: "Según demanda",
    fecha_adj_firme: null,
    desierto: false,
    raw_data: {},
    created_at: "2026-01-01T00:00:00Z",
    updated_at: "2026-01-01T00:00:00Z",
    ...overrides,
  }
}

function makeProfile(overrides: Partial<UserProfile> = {}): UserProfile {
  return {
    user_id: "user-1",
    categorias: ["MEDICAMENTO"],
    instituciones: ["CCSS"],
    monto_min: null,
    keywords: [],
    onboarding_completed: true,
    created_at: "2026-01-01T00:00:00Z",
    updated_at: "2026-01-01T00:00:00Z",
    ...overrides,
  }
}

// ─── No profile ────────────────────────────────────────────────────────────

describe("no profile", () => {
  test("returns no_profile when profile is null", () => {
    const result = checkEligibility(makeLic(), null)
    assert.deepEqual(result, { ok: null, reason: "no_profile" })
  })

  test("no_profile takes precedence over precal", () => {
    const l = makeLic({ modalidad_participacion: "Precalificación" })
    const result = checkEligibility(l, null)
    assert.deepEqual(result, { ok: null, reason: "no_profile" })
  })
})

// ─── Precalificación ───────────────────────────────────────────────────────

describe("precalificación", () => {
  test("returns precal when modalidad is Precalificación", () => {
    const l = makeLic({ modalidad_participacion: "Precalificación" })
    const result = checkEligibility(l, makeProfile())
    assert.deepEqual(result, { ok: null, reason: "precal" })
  })

  test("non-precal modalidad does not trigger precal", () => {
    const l = makeLic({ modalidad_participacion: "Según demanda" })
    const result = checkEligibility(l, makeProfile())
    assert.equal(result.ok, true)
  })

  test("null modalidad does not trigger precal", () => {
    const l = makeLic({ modalidad_participacion: null })
    const result = checkEligibility(l, makeProfile())
    assert.equal(result.ok, true)
  })
})

// ─── Category check ────────────────────────────────────────────────────────

describe("category check", () => {
  test("eligible when profile categoria matches", () => {
    const result = checkEligibility(
      makeLic({ categoria: "MEDICAMENTO" }),
      makeProfile({ categorias: ["MEDICAMENTO"] })
    )
    assert.equal(result.ok, true)
  })

  test("ineligible when profile categoria does not match", () => {
    const result = checkEligibility(
      makeLic({ categoria: "MEDICAMENTO" }),
      makeProfile({ categorias: ["EQUIPAMIENTO"] })
    )
    assert.equal(result.ok, false)
    assert.ok(result.ok === false && result.reasons[0].includes("Medicamento"))
  })

  test("skips category check when profile.categorias is empty", () => {
    const result = checkEligibility(
      makeLic({ categoria: "MEDICAMENTO" }),
      makeProfile({ categorias: [] })
    )
    assert.equal(result.ok, true)
  })

  test("skips category check when l.categoria is null", () => {
    const result = checkEligibility(
      makeLic({ categoria: null }),
      makeProfile({ categorias: ["MEDICAMENTO"] })
    )
    assert.equal(result.ok, true)
  })

  test("eligible when profile has multiple categories including the right one", () => {
    const result = checkEligibility(
      makeLic({ categoria: "INSUMO" }),
      makeProfile({ categorias: ["MEDICAMENTO", "INSUMO"] })
    )
    assert.equal(result.ok, true)
  })
})

// ─── Institution check ─────────────────────────────────────────────────────

describe("institution check", () => {
  test("CCSS matches CAJA COSTARRICENSE DE SEGURO SOCIAL", () => {
    const result = checkEligibility(
      makeLic({ instnm: "CAJA COSTARRICENSE DE SEGURO SOCIAL" }),
      makeProfile({ instituciones: ["CCSS"] })
    )
    assert.equal(result.ok, true)
  })

  test("Hospitales matches hospital name", () => {
    const result = checkEligibility(
      makeLic({ instnm: "HOSPITAL DR. RAFAEL ÁNGEL CALDERÓN GUARDIA" }),
      makeProfile({ instituciones: ["Hospitales"] })
    )
    assert.equal(result.ok, true)
  })

  test("INS matches INSTITUTO NACIONAL DE SEGUROS", () => {
    const result = checkEligibility(
      makeLic({ instnm: "INSTITUTO NACIONAL DE SEGUROS" }),
      makeProfile({ instituciones: ["INS"] })
    )
    assert.equal(result.ok, true)
  })

  test("MS matches MINISTERIO DE SALUD", () => {
    const result = checkEligibility(
      makeLic({ instnm: "MINISTERIO DE SALUD" }),
      makeProfile({ instituciones: ["MS"] })
    )
    assert.equal(result.ok, true)
  })

  test("Todas wildcard matches any institution", () => {
    const result = checkEligibility(
      makeLic({ instnm: "MUNICIPALIDAD DE SAN JOSÉ" }),
      makeProfile({ instituciones: ["Todas"] })
    )
    assert.equal(result.ok, true)
  })

  test("Todas wildcard skips check even alongside other codes", () => {
    const result = checkEligibility(
      makeLic({ instnm: "MUNICIPALIDAD DE SAN JOSÉ" }),
      makeProfile({ instituciones: ["CCSS", "Todas"] })
    )
    assert.equal(result.ok, true)
  })

  test("ineligible when institution does not match any code", () => {
    const result = checkEligibility(
      makeLic({ instnm: "CAJA COSTARRICENSE DE SEGURO SOCIAL" }),
      makeProfile({ instituciones: ["INS"] })
    )
    assert.equal(result.ok, false)
    assert.ok(result.ok === false && result.reasons[0].includes("instituciones objetivo"))
  })

  test("eligible when one of multiple codes matches", () => {
    const result = checkEligibility(
      makeLic({ instnm: "HOSPITAL DR. CALDERÓN GUARDIA" }),
      makeProfile({ instituciones: ["CCSS", "Hospitales"] })
    )
    assert.equal(result.ok, true)
  })

  test("skips institution check when profile.instituciones is empty", () => {
    const result = checkEligibility(
      makeLic({ instnm: "MUNICIPALIDAD DE SAN JOSÉ" }),
      makeProfile({ instituciones: [] })
    )
    assert.equal(result.ok, true)
  })

  test("skips institution check when l.instnm is null", () => {
    const result = checkEligibility(
      makeLic({ instnm: null }),
      makeProfile({ instituciones: ["CCSS"] })
    )
    assert.equal(result.ok, true)
  })

  test("unknown institution code does not match", () => {
    const result = checkEligibility(
      makeLic({ instnm: "CAJA COSTARRICENSE DE SEGURO SOCIAL" }),
      makeProfile({ instituciones: ["UNKNOWN_CODE"] })
    )
    assert.equal(result.ok, false)
  })
})

// ─── Monto check ───────────────────────────────────────────────────────────

describe("monto check", () => {
  test("eligible when presupuesto is above monto_min", () => {
    const result = checkEligibility(
      makeLic({ presupuesto_estimado: 100_000_000 }),
      makeProfile({ monto_min: 50_000_000 })
    )
    assert.equal(result.ok, true)
  })

  test("eligible when presupuesto equals monto_min exactly", () => {
    const result = checkEligibility(
      makeLic({ presupuesto_estimado: 50_000_000 }),
      makeProfile({ monto_min: 50_000_000 })
    )
    assert.equal(result.ok, true)
  })

  test("ineligible when presupuesto is below monto_min", () => {
    const result = checkEligibility(
      makeLic({ presupuesto_estimado: 10_000_000 }),
      makeProfile({ monto_min: 50_000_000 })
    )
    assert.equal(result.ok, false)
    assert.ok(result.ok === false && result.reasons[0].includes("mínimo configurado"))
  })

  test("skips monto check when profile.monto_min is null", () => {
    const result = checkEligibility(
      makeLic({ presupuesto_estimado: 1_000 }),
      makeProfile({ monto_min: null })
    )
    assert.equal(result.ok, true)
  })

  test("skips monto check when l.presupuesto_estimado is null", () => {
    const result = checkEligibility(
      makeLic({ presupuesto_estimado: null }),
      makeProfile({ monto_min: 50_000_000 })
    )
    assert.equal(result.ok, true)
  })
})

// ─── Multiple reasons ──────────────────────────────────────────────────────

describe("multiple reasons", () => {
  test("accumulates all failing checks into reasons array", () => {
    const result = checkEligibility(
      makeLic({ categoria: "EQUIPAMIENTO", presupuesto_estimado: 1_000_000 }),
      makeProfile({ categorias: ["MEDICAMENTO"], instituciones: ["INS"], monto_min: 50_000_000 })
    )
    assert.equal(result.ok, false)
    assert.ok(result.ok === false && result.reasons.length === 3)
  })

  test("two failures produces two reasons", () => {
    const result = checkEligibility(
      makeLic({ categoria: "EQUIPAMIENTO", presupuesto_estimado: 1_000_000 }),
      makeProfile({ categorias: ["MEDICAMENTO"], monto_min: 50_000_000 })
    )
    assert.equal(result.ok, false)
    assert.ok(result.ok === false && result.reasons.length === 2)
  })
})

// ─── Fully eligible ────────────────────────────────────────────────────────

describe("fully eligible", () => {
  test("eligible when all checks pass", () => {
    const result = checkEligibility(makeLic(), makeProfile())
    assert.deepEqual(result, { ok: true })
  })

  test("eligible with null modalidad (not precal)", () => {
    const result = checkEligibility(
      makeLic({ modalidad_participacion: null }),
      makeProfile()
    )
    assert.deepEqual(result, { ok: true })
  })
})
