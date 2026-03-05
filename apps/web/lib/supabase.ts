import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!

export const supabase = createClient(supabaseUrl, supabaseKey, {
  auth: {
    persistSession: true,
    autoRefreshToken: true,
  },
})

// Tipo para las licitaciones
export type LicitacionMedica = {
  id: string
  numero_procedimiento: string
  descripcion: string | null
  institucion: string | null
  tipo_procedimiento: string | null
  clasificacion_unspsc: string | null
  categoria: string | null
  monto_colones: number | null
  adjudicatario: string | null
  estado: string | null
  fecha_tramite: string | null
  fecha_limite_oferta: string | null
  created_at: string
  updated_at: string
}

// Tipo para alertas
export type AlertaConfig = {
  id: string
  user_id: string
  keywords: string[] | null
  categorias: string[] | null
  unspsc: string[] | null
  canal: string[] | null
  activo: boolean
  created_at: string
  updated_at: string
}

// Helpers para queries
export async function getLicitacionesActivas(limit = 50) {
  const { data, error } = await supabase
    .from('licitaciones_medicas')
    .select('*')
    .not('estado', 'in', '(Desierto,Cancelado,Desistido)')
    .order('fecha_tramite', { ascending: false })
    .limit(limit)

  if (error) throw error
  return data as LicitacionMedica[]
}

export async function getLicitacionesPorCategoria(categoria: string) {
  const { data, error } = await supabase
    .from('licitaciones_medicas')
    .select('*')
    .eq('categoria', categoria)
    .order('fecha_tramite', { ascending: false })

  if (error) throw error
  return data as LicitacionMedica[]
}

export async function getLicitacionByNumero(numero: string) {
  const { data, error } = await supabase
    .from('licitaciones_medicas')
    .select('*')
    .eq('numero_procedimiento', numero)
    .single()

  if (error) throw error
  return data as LicitacionMedica
}

export async function searchLicitaciones(query: string) {
  const { data, error } = await supabase
    .from('licitaciones_medicas')
    .select('*')
    .ilike('descripcion', `%${query}%`)
    .order('fecha_tramite', { ascending: false })

  if (error) throw error
  return data as LicitacionMedica[]
}

export async function getResumenPorCategoria() {
  const { data, error } = await supabase
    .from('resumen_por_categoria')
    .select('*')

  if (error) throw error
  return data
}

export async function getLicitacionesPorVencer() {
  const { data, error } = await supabase
    .from('licitaciones_por_vencer')
    .select('*')

  if (error) throw error
  return data as LicitacionMedica[]
}

export async function getAlertasConfig() {
  const { data, error } = await supabase
    .from('alertas_config')
    .select('*')

  if (error) throw error
  return data as AlertaConfig[]
}

export async function upsertAlertaConfig(alerta: Partial<AlertaConfig>) {
  const { data, error } = await supabase
    .from('alertas_config')
    .upsert(alerta)
    .select()
    .single()

  if (error) throw error
  return data as AlertaConfig
}

export async function deleteAlertaConfig(id: string) {
  const { error } = await supabase
    .from('alertas_config')
    .delete()
    .eq('id', id)

  if (error) throw error
}
