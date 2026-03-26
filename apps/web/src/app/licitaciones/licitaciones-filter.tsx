// apps/web/src/app/licitaciones/licitaciones-filter.tsx
"use client"

import { useState, useMemo } from "react"
import { LicitacionesTable } from "@/components/licitaciones-table"
import { X } from "lucide-react"
import type { LicitacionPreview, Categoria } from "@/lib/types"

const CATEGORIAS: Categoria[] = ["MEDICAMENTO", "EQUIPAMIENTO", "INSUMO", "SERVICIO"]
const CATEGORIA_LABELS: Record<Categoria, string> = {
  MEDICAMENTO: "Medicamento",
  EQUIPAMIENTO: "Equipamiento",
  INSUMO: "Insumo",
  SERVICIO: "Servicio",
}

interface LicitacionesFilterProps {
  data: LicitacionPreview[]
}

export function LicitacionesFilter({ data }: LicitacionesFilterProps) {
  const [instFilter, setInstFilter] = useState("")
  const [fechaDesde, setFechaDesde] = useState("")
  const [fechaHasta, setFechaHasta] = useState("")
  const [catFilter, setCatFilter] = useState("")

  const instituciones = useMemo(() => {
    const set = new Set(data.map(l => l.instnm).filter(Boolean) as string[])
    return Array.from(set).sort()
  }, [data])

  const filtered = useMemo(() => {
    return data.filter(l => {
      if (instFilter && l.instnm !== instFilter) return false
      if (catFilter && l.categoria !== catFilter) return false
      if (fechaDesde && l.biddoc_start_dt && l.biddoc_start_dt < fechaDesde) return false
      if (fechaHasta && l.biddoc_start_dt && l.biddoc_start_dt > fechaHasta + "T23:59:59") return false
      return true
    })
  }, [data, instFilter, catFilter, fechaDesde, fechaHasta])

  const hasFilters = instFilter || catFilter || fechaDesde || fechaHasta

  function clear() {
    setInstFilter("")
    setCatFilter("")
    setFechaDesde("")
    setFechaHasta("")
  }

  return (
    <>
      {/* Filter bar */}
      <div className="mb-6 flex flex-wrap items-center gap-3">
        <select
          value={instFilter}
          onChange={e => setInstFilter(e.target.value)}
          className="rounded-[60px] bg-[#2c3833] px-4 py-2 text-sm text-[#f2f5f9] border-none outline-none focus:ring-1 focus:ring-[#84a584] cursor-pointer"
        >
          <option value="">Todas las instituciones</option>
          {instituciones.map(inst => (
            <option key={inst} value={inst}>{inst}</option>
          ))}
        </select>

        <select
          value={catFilter}
          onChange={e => setCatFilter(e.target.value)}
          className="rounded-[60px] bg-[#2c3833] px-4 py-2 text-sm text-[#f2f5f9] border-none outline-none focus:ring-1 focus:ring-[#84a584] cursor-pointer"
        >
          <option value="">Todas las categorías</option>
          {CATEGORIAS.map(cat => (
            <option key={cat} value={cat}>{CATEGORIA_LABELS[cat]}</option>
          ))}
        </select>

        <input
          type="date"
          value={fechaDesde}
          onChange={e => setFechaDesde(e.target.value)}
          placeholder="Desde"
          className="rounded-[60px] bg-[#2c3833] px-4 py-2 text-sm text-[#f2f5f9] border-none outline-none focus:ring-1 focus:ring-[#84a584]"
        />

        <input
          type="date"
          value={fechaHasta}
          onChange={e => setFechaHasta(e.target.value)}
          placeholder="Hasta"
          className="rounded-[60px] bg-[#2c3833] px-4 py-2 text-sm text-[#f2f5f9] border-none outline-none focus:ring-1 focus:ring-[#84a584]"
        />

        {hasFilters && (
          <button
            onClick={clear}
            className="inline-flex items-center gap-1.5 rounded-[60px] bg-[#3d4d45] px-4 py-2 text-sm text-[var(--color-text-muted)] hover:text-[#f2f5f9] transition-colors"
          >
            <X size={14} />
            Limpiar
          </button>
        )}

        {hasFilters && (
          <span className="text-xs text-[var(--color-text-muted)]">
            {filtered.length} de {data.length}
          </span>
        )}
      </div>

      {/* Table — visually unchanged */}
      <div className="rounded-[32px] bg-[#1a1f1a] p-6">
        <LicitacionesTable data={filtered} />
      </div>
    </>
  )
}
