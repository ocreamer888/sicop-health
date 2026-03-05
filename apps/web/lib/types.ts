export type Categoria =
  | 'MEDICAMENTO'
  | 'EQUIPAMIENTO'
  | 'INSUMO'
  | 'SERVICIO'

export type TypeKey = 'RPT_PUB' | 'RPT_ADJ' | 'RPT_MOD'

export interface Licitacion {
  id: string
  numero_procedimiento: string
  descripcion: string | null
  institucion: string | null
  tipo_procedimiento: string | null
  clasificacion_unspsc: string | null
  categoria: Categoria | null
  monto_colones: number | null
  adjudicatario: string | null
  estado: string | null
  fecha_tramite: string | null
  fecha_limite_oferta: string | null

  // v2.1 fields
  unspsc_cd: string | null
  supplier_cd: string | null
  modalidad: string | null
  excepcion_cd: string | null
  biddoc_end_dt: string | null
  adj_firme_dt: string | null
  vigencia_contrato: string | null
  unidad_vigencia: string | null
  cartel_cate: string | null

  // Internal fields
  es_medica: boolean
  type_key: TypeKey
  raw_data: Record<string, unknown>
  created_at: string
  updated_at: string
}
