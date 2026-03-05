export type Categoria = 
  | 'MEDICAMENTO' 
  | 'EQUIPAMIENTO' 
  | 'INSUMO' 
  | 'SERVICIO_SALUD' 
  | 'TECNOLOGIA' 
  | 'OTRO_MEDICO'

export type TypeKey = 'RPT_PUB' | 'RPT_ADJ' | 'RPT_MOD'

export interface Licitacion {
  id: string
  inst_cartel_no: string
  cartel_no: string | null
  proce_type: string | null
  inst_nm: string | null
  cartel_nm: string | null
  openbid_dt: string | null
  biddoc_start_dt: string | null
  supplier_nm: string | null
  currency_type: string | null
  amt: number | null
  detalle: string | null
  es_medica: boolean
  categoria: Categoria | null
  type_key: TypeKey
  raw_data: Record<string, unknown>
  created_at: string
  updated_at: string
}

export interface DashboardStats {
  totalLicitaciones: number
  porCategoria: Record<Categoria, number>
  porFuente: Record<TypeKey, number>
  montoTotal: number
  tendenciaMensual: {
    mes: string
    cantidad: number
    monto: number
  }[]
}
