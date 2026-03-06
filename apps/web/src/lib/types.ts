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

export type TypeKey = "RPT_PUB" | "RPT_ADJ" | "RPT_MOD"

// Issue G — códigos de tipo de procedimiento extraídos de instCartelNo
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

export interface Licitacion {
  id: string

  // Core
  numero_procedimiento: string
  descripcion: string | null
  institucion: string | null
  estado: Estado | null
  categoria: Categoria | null

  // Procedimiento
  tipo_procedimiento: TipoProcedimiento | null  // Issue G: tipado fuerte
  modalidad: string | null
  excepcion_cd: string | null
  cartel_cate: string | null

  // UNSPSC
  unspsc_cd: string | null
  clasificacion_unspsc: string | null

  // Proveedor
  adjudicatario: string | null
  supplier_nm: string | null  // Issue D: campo real en DB
  supplier_cd: string | null

  // Montos
  monto_colones: number | null
  currency_type: string | null  // Issue D: siempre presente, no optional

  // Fechas
  fecha_tramite: string | null
  fecha_limite_oferta: string | null
  biddoc_start_dt: string | null  // Issue D: campo en DB que faltaba
  biddoc_end_dt: string | null
  openbid_dt: string | null       // Issue D: campo en DB que faltaba
  adj_firme_dt: string | null

  // Contrato
  vigencia_contrato: string | null
  unidad_vigencia: string | null

  // Flags
  es_medica: boolean
  type_key: TypeKey | null  // Issue D: removido optional — siempre existe en DB

  // Raw / meta
  instcartelno: string | null     // Issue D: campo clave del ETL
  cartelno: string | null
  inst_code: string | null
  instnm: string | null
  cartelnm: string | null
  procetype: string | null
  typekey: TypeKey | null
  detalle: string | null
  mod_reason: string | null
  raw_data: Record<string, unknown>
  created_at: string
  updated_at: string
}

// Issue D fix — columnas reales de la view migration 004
export interface DashboardStats {
  totalLicitaciones: number
  porCategoria: {
    categoria: string
    total: number
    publicadas: number    // ← migration 004 (era "publicados")
    adjudicadas: number   // ← migration 004 (era "adjudicados")
    monto_crc: number | null  // ← migration 004 (era "monto_total")
    monto_usd: number | null  // ← migration 004 (nuevo campo)
  }[]
  porEstado: { estado: string; count: number }[]
  montoCRC: number
  montoUSD: number
}

// Subset para listas — incluye currency_type para formatCurrency
export type LicitacionPreview = Pick<
  Licitacion,
  | "id"
  | "numero_procedimiento"
  | "descripcion"
  | "institucion"
  | "categoria"
  | "tipo_procedimiento"   // Issue G: necesario para TIPO_LABELS en list view
  | "monto_colones"
  | "currency_type"        // necesario para formatCurrency
  | "fecha_tramite"
  | "estado"
  | "es_medica"
  | "raw_data"
>
