// apps/web/src/lib/types.ts

export type Categoria =
  | "MEDICAMENTO"
  | "EQUIPAMIENTO"
  | "INSUMO"
  | "SERVICIO"

export type Estado =
  | "Publicado"
  | "Adjudicado"
  | "Modificado"
  | "Desierto"
  | "Cancelado"
  | (string & {})

export type WorkflowNodeStatus = "active" | "partial" | "pendiente" | "blocked"

export type TypeKey = "RPT_PUB" | "RPT_ADJ" | "RPT_MOD"

export type TipoProcedimiento =
  | "LD" // Licitación Directa
  | "LY" // Licitación Abreviada
  | "LE" // Licitación por Registro
  | "LG" // Licitación de Mayor Cuantía
  | "LP" // Licitación Pública
  | "PX" // Procedimiento Excepcional
  | "PE" // Procedimiento Especial
  | "XE" // Contratación Directa
  | "CD" // Contratación Directa (alias)
  | (string & {})

// Labels para display — espejo de TIPO_PROCEDIMIENTO_LABELS en parser.py
export const TIPO_LABELS: Record<string, string> = {
  LD: "Licitación Directa",
  LY: "Licitación Abreviada",
  LE: "Licitación por Registro",
  LG: "Licitación Mayor Cuantía",
  LP: "Licitación Pública",
  PX: "Procedimiento Excepcional",
  PE: "Procedimiento Especial",
  XE: "Contratación Directa",
  CD: "Contratación Directa",
}

// ─────────────────────────────────────────────
// LICITACION — schema v2.9 (alineado a DB post-migration 003)
// Columnas removidas: numero_procedimiento, descripcion, institucion,
//   adjudicatario, clasificacion_unspsc, fecha_tramite, fecha_limite_oferta
// ─────────────────────────────────────────────

export interface Licitacion {
  id: string

  // — Identidad v2 —
  instcartelno: string           // PK lógica — UNIQUE NOT NULL en DB
  cartelno: string | null

  // — Descripción —
  cartelnm: string | null        // título de la licitación (era "descripcion")
  instnm: string | null          // nombre institución (era "institucion")
  inst_code: string | null

  // — Estado —
  estado: Estado | null
  es_medica: boolean
  categoria: Categoria | null

  // — Procedimiento —
  procetype: string | null       // label largo del API ("LICITACIÓN MENOR")
  tipo_procedimiento: TipoProcedimiento | null  // código corto extraído ("LD", "XE"…)
  typekey: TypeKey | null        // RPT_PUB | RPT_ADJ | RPT_MOD
  modalidad: string | null
  excepcion_cd: string | null
  cartel_cate: string | null
  mod_reason: string | null

  // — Clasificación —
  unspsc_cd: string | null       // 8 dígitos familia UNSPSC (era "clasificacion_unspsc")

  // — Proveedor —
  supplier_nm: string | null     // (era "adjudicatario")
  supplier_cd: string | null

  // — Montos —
  monto_colones: number | null
  currency_type: string | null
  detalle: string | null

  // — Fechas —
  biddoc_start_dt: string | null  // fecha publicación (era "fecha_tramite")
  biddoc_end_dt: string | null    // deadline ofertas (era "fecha_limite_oferta")
  openbid_dt: string | null
  adj_firme_dt: string | null

  // — Contrato —
  vigencia_contrato: string | null
  unidad_vigencia: string | null

  // — Datos Abiertos enrichment —
  presupuesto_estimado:    number | null
  moneda_presupuesto:      string | null
  modalidad_participacion: string | null
  fecha_adj_firme:         string | null
  desierto:                boolean

  // — Meta —
  raw_data: Record<string, unknown>
  created_at: string
  updated_at: string
}

// ─────────────────────────────────────────────
// DASHBOARD STATS — columnas de resumen_por_categoria
// ─────────────────────────────────────────────

export interface DashboardStats {
  totalLicitaciones: number
  porCategoria: {
    categoria: Categoria
    total: number
    publicadas: number
    adjudicadas: number
    monto_crc: number | null
    monto_usd: number | null
  }[]
  porEstado: { estado: string; count: number }[]
  montoCRC: number
  montoUSD: number
}

// ─────────────────────────────────────────────
// LICITACION PREVIEW — subset para listas y tabla
// ─────────────────────────────────────────────

export type LicitacionPreview = Pick<
  Licitacion,
  | "id"
  | "instcartelno"       // era numero_procedimiento
  | "cartelnm"           // era descripcion
  | "instnm"             // era institucion
  | "categoria"
  | "tipo_procedimiento" // para TIPO_LABELS en list view
  | "monto_colones"
  | "currency_type"      // para formatCurrency
  | "biddoc_start_dt"    // era fecha_tramite
  | "biddoc_end_dt"      // deadline — útil para badges de vencimiento
  | "estado"
  | "es_medica"
>

// ─────────────────────────────────────────────
// ALERTAS CONFIG
// ─────────────────────────────────────────────

export interface AlertaConfig {
  id: string
  user_id: string
  nombre: string
  keywords: string[]
  categorias: string[]
  instituciones: string[]
  monto_min: number | null
  monto_max: number | null
  canales: string[]
  activo: boolean
  created_at: string
  updated_at: string
}

export type AlertaFormData = Omit<AlertaConfig, 'id' | 'user_id' | 'created_at' | 'updated_at'>

// ─────────────────────────────────────────────
// GAMIFICATION
// ─────────────────────────────────────────────

export interface UserProfile {
  user_id: string
  categorias: string[]
  instituciones: string[]
  monto_min: number | null
  keywords: string[]
  onboarding_completed: boolean
  created_at: string
  updated_at: string
}

export interface BadgeDefinition {
  id: string
  name: string
  description: string
  icon: string
}

export interface UserBadge {
  user_id: string
  badge_id: string
  earned_at: string
}

export interface GamificationState {
  intelScore: number          // 0–100
  streak: number              // days
  unreadCount: number
  earnedBadgeIds: string[]
  profile: UserProfile | null
}
