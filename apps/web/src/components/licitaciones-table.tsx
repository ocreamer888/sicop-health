"use client";

import {
  useReactTable,
  getCoreRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  getFilteredRowModel,
  flexRender,
  type ColumnDef,
  type SortingState,
  type ColumnFiltersState,
} from "@tanstack/react-table";
import { useState, useMemo } from "react";
import Link from "next/link";
import { ArrowUpDown, ArrowUp, ArrowDown, ChevronLeft, ChevronRight, LayoutGrid, Table as TableIcon, Building2, Tag, CalendarClock, ArrowUpRight, X, SlidersHorizontal } from "lucide-react";
import { Badge } from "./ui/badge";
import { UrgencyBadge } from "./ui/urgency-badge";
import { TIPO_LABELS } from "@/lib/types";
import type { LicitacionPreview, Categoria } from "@/lib/types";

type ViewMode = "table" | "cards";
type SortOption = "newest" | "oldest" | "amount-high" | "amount-low" | "name";

interface LicitacionesTableProps {
  data: LicitacionPreview[];
  showPagination?: boolean;
  pageSize?: number;
}

const categoriaLabels: Record<Categoria, string> = {
  MEDICAMENTO: "Medicamento",
  EQUIPAMIENTO: "Equipamiento",
  INSUMO: "Insumo",
  SERVICIO: "Servicio",
};

const categoriaVariants: Record<Categoria, "default" | "secondary" | "sage" | "olive"> = {
  MEDICAMENTO: "sage",
  EQUIPAMIENTO: "secondary",
  INSUMO: "olive",
  SERVICIO: "default",
};

const CATEGORIA_COLORS: Record<string, string> = {
  MEDICAMENTO: "bg-[#84a584]/15 text-[#84a584]",
  EQUIPAMIENTO: "bg-[#8a9bb5]/15 text-[#8a9bb5]",
  INSUMO: "bg-[#b5a88a]/15 text-[#b5a88a]",
  SERVICIO: "bg-[#898a7d]/15 text-[#898a7d]",
};

function formatCurrency(amount: number | null, currency?: string | null): string {
  if (amount === null || amount === undefined) return "N/A";
  if (currency === "USD" || currency === "$") {
    return `$${amount.toLocaleString("en-US")}`;
  }
  return `₡${amount.toLocaleString("es-CR")}`;
}

function formatDate(dateStr: string | null): string {
  if (!dateStr) return "N/A";
  return new Date(dateStr).toLocaleDateString("es-CR", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

function timeAgo(iso: string) {
  const diff = Date.now() - new Date(iso).getTime();
  const h = Math.floor(diff / 3_600_000);
  const d = Math.floor(diff / 86_400_000);
  if (h < 1) return "Hace menos de 1h";
  if (h < 24) return `Hace ${h}h`;
  if (d === 1) return "Ayer";
  return `Hace ${d} días`;
}

// ─────────────────────────────────────────────
// CARD COMPONENT
// ─────────────────────────────────────────────

interface LicitacionCardProps {
  licitacion: LicitacionPreview;
}

function LicitacionCard({ licitacion }: LicitacionCardProps) {
  const catColor = licitacion.categoria
    ? (CATEGORIA_COLORS[licitacion.categoria] ?? "bg-[#898a7d]/15 text-[#898a7d]")
    : null;

  const cierre = licitacion.biddoc_end_dt
    ? new Date(licitacion.biddoc_end_dt).toLocaleDateString("es-CR", {
        day: "2-digit",
        month: "short",
        year: "numeric",
      })
    : null;

  return (
    <div className="rounded-[24px] bg-[#2c3833] border border-[#3d4d45] p-5 hover:border-[#84a584]/40 transition-all h-full flex flex-col">
      {/* Top row: time + estado + urgency */}
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs text-[#5a6a62]">
          {licitacion.biddoc_start_dt ? timeAgo(licitacion.biddoc_start_dt) : "N/A"}
        </span>
        <div className="flex items-center gap-1.5">
          {licitacion.estado && (
            <span className="text-xs px-2.5 py-0.5 rounded-[60px] bg-[#1a1f1a] text-[#5a6a62] border border-[#3d4d45]">
              {licitacion.estado}
            </span>
          )}
          <UrgencyBadge biddocEndDt={licitacion.biddoc_end_dt} />
        </div>
      </div>

      {/* Title */}
      <p className="text-[#f9f5df] font-medium text-sm leading-snug mb-3 font-[family-name:var(--font-montserrat)] line-clamp-2">
        {licitacion.cartelnm || licitacion.instcartelno}
      </p>

      {/* Meta */}
      <div className="space-y-1.5 mb-4 flex-1">
        {licitacion.instnm && (
          <div className="flex items-center gap-1.5 text-xs text-[#5a6a62]">
            <Building2 size={12} />
            <span className="truncate">{licitacion.instnm}</span>
          </div>
        )}
        {licitacion.categoria && (
          <div className="flex items-center gap-1.5">
            <Tag size={12} className="text-[#5a6a62]" />
            <span className={`text-xs px-2 py-0.5 rounded-[60px] ${catColor}`}>
              {licitacion.categoria}
            </span>
          </div>
        )}
        {licitacion.tipo_procedimiento && (
          <div className="flex items-center gap-1.5 text-xs text-[#5a6a62]">
            <span className="px-1.5 py-0.5 rounded bg-[#1a1f1a] border border-[#3d4d45]">
              {licitacion.tipo_procedimiento}
            </span>
            <span className="truncate" title={TIPO_LABELS[licitacion.tipo_procedimiento]}>
              {TIPO_LABELS[licitacion.tipo_procedimiento]}
            </span>
          </div>
        )}
        {cierre && (
          <div className="flex items-center gap-1.5 text-xs text-[#5a6a62]">
            <CalendarClock size={12} />
            <span>Cierre: {cierre}</span>
          </div>
        )}
        {(licitacion.presupuesto_estimado ?? licitacion.monto_colones) !== null && (
          <p className="text-xs text-[#f2f5f9] font-medium pl-0.5">
            {formatCurrency(
              licitacion.presupuesto_estimado ?? licitacion.monto_colones,
              licitacion.moneda_presupuesto ?? licitacion.currency_type
            )}
          </p>
        )}
      </div>

      {/* CTA */}
      <Link
        href={`/licitaciones/${licitacion.instcartelno}`}
        className="flex items-center gap-1.5 text-xs font-medium text-[#84a584] hover:text-[#a5c4a5] transition-colors mt-auto"
      >
        Ver licitación
        <ArrowUpRight size={13} />
      </Link>
    </div>
  );
}

export function LicitacionesTable({
  data,
  showPagination = true,
  pageSize = 10,
}: LicitacionesTableProps) {
  const [sorting, setSorting] = useState<SortingState>([{ id: "biddoc_start_dt", desc: true }]);
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
  const [globalFilter, setGlobalFilter] = useState("");
  const [viewMode, setViewMode] = useState<ViewMode>("table");

  // Get unique categories from data for filter pills
  const availableCategories = useMemo(() => {
    const cats = new Set(data.map((d) => d.categoria).filter(Boolean));
    return Array.from(cats) as Categoria[];
  }, [data]);

  // Get current category filter
  const activeCategory = useMemo(() => {
    const filter = columnFilters.find((f) => f.id === "categoria");
    return (filter?.value as Categoria) || null;
  }, [columnFilters]);

  // Derive sort option from current sorting state (for cards view dropdown)
  const currentSortOption: SortOption = useMemo(() => {
    const sort = sorting[0];
    if (!sort) return "newest";
    if (sort.id === "biddoc_start_dt") {
      return sort.desc ? "newest" : "oldest";
    }
    if (sort.id === "monto_colones") {
      return sort.desc ? "amount-high" : "amount-low";
    }
    if (sort.id === "cartelnm") {
      return "name";
    }
    return "newest";
  }, [sorting]);

  // Apply sort option from dropdown
  const handleSortChange = (option: SortOption) => {
    const sorts: Record<SortOption, SortingState> = {
      newest: [{ id: "biddoc_start_dt", desc: true }],
      oldest: [{ id: "biddoc_start_dt", desc: false }],
      "amount-high": [{ id: "monto_colones", desc: true }],
      "amount-low": [{ id: "monto_colones", desc: false }],
      name: [{ id: "cartelnm", desc: false }],
    };
    setSorting(sorts[option]);
  };

  const columns: ColumnDef<LicitacionPreview>[] = [
    {
      accessorKey: "instcartelno",
      header: "ID",
      cell: ({ row }) => (
        <Link
          href={`/licitaciones/${row.original.instcartelno}`}
          className="font-mono text-sm text-[#84a584] hover:underline"
        >
          {row.getValue("instcartelno")}
        </Link>
      ),
    },
    {
      accessorKey: "cartelnm",
      header: "Título",
      cell: ({ row }) => (
        <div className="max-w-md">
          <p className="font-medium text-[#f2f5f9] line-clamp-2">
            {row.getValue("cartelnm") || "Sin título"}
          </p>
        </div>
      ),
    },
    {
      accessorKey: "instnm",
      header: "Entidad",
      cell: ({ row }) => (
        <span className="text-sm text-[#e4e4e4]">
          {row.getValue("instnm") || "N/A"}
        </span>
      ),
    },
    {
      accessorKey: "tipo_procedimiento",
      header: "Tipo",
      cell: ({ row }) => {
        const tipo = row.getValue("tipo_procedimiento") as string | null;
        if (!tipo) return <span className="text-[var(--color-text-muted)]">-</span>;
        return (
          <span className="text-xs text-[#e4e4e4]" title={TIPO_LABELS[tipo] ?? tipo}>
            {tipo}
          </span>
        );
      },
    },
    {
      accessorKey: "categoria",
      header: "Categoría",
      filterFn: (row, columnId, filterValue) => {
        return row.getValue(columnId) === filterValue;
      },
      cell: ({ row }) => {
        const categoria = row.getValue("categoria") as Categoria | null;
        if (!categoria) return <span className="text-[var(--color-text-muted)]">-</span>;
        return (
          <Badge variant={categoriaVariants[categoria]}>
            {categoriaLabels[categoria]}
          </Badge>
        );
      },
    },
    {
      accessorKey: "monto_colones",
      header: "Monto",
      cell: ({ row }) => {
        const monto = row.original.presupuesto_estimado ?? row.getValue<number | null>("monto_colones")
        const moneda = row.original.moneda_presupuesto ?? row.original.currency_type
        if (!monto) return <span className="text-[var(--color-text-muted)]">–</span>
        return (
          <span className="font-mono text-sm text-[#f9f5df]">
            {formatCurrency(monto, moneda)}
          </span>
        )
      },
    },
    {
      accessorKey: "biddoc_start_dt",
      header: "Publicado",
      cell: ({ row }) => (
        <span className="text-sm text-[#e4e4e4]">
          {formatDate(row.getValue("biddoc_start_dt"))}
        </span>
      ),
    },
    {
      accessorKey: "estado",
      header: "Estado",
      cell: ({ row }) => (
        <div className="flex flex-wrap gap-1.5 items-center">
          <span className="text-xs text-[var(--color-text-muted)]">
            {row.getValue("estado") || "N/A"}
          </span>
          <UrgencyBadge biddocEndDt={row.original.biddoc_end_dt} />
        </div>
      ),
    },
  ];

  const table = useReactTable({
    data,
    columns,
    state: { sorting, globalFilter, columnFilters },
    onSortingChange: setSorting,
    onGlobalFilterChange: setGlobalFilter,
    onColumnFiltersChange: setColumnFilters,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    initialState: { pagination: { pageSize } },
  });

  // Helper to toggle category filter
  const toggleCategory = (cat: Categoria) => {
    if (activeCategory === cat) {
      setColumnFilters((prev) => prev.filter((f) => f.id !== "categoria"));
    } else {
      setColumnFilters((prev) => [
        ...prev.filter((f) => f.id !== "categoria"),
        { id: "categoria", value: cat },
      ]);
    }
  };

  // Clear all filters
  const clearFilters = () => {
    setColumnFilters([]);
    setGlobalFilter("");
  };

  const hasFilters = activeCategory || globalFilter;

  return (
    <div className="space-y-4">
      {/* Search + View Toggle */}
      <div className="flex items-center gap-4">
        <input
          type="text"
          placeholder="Buscar licitaciones..."
          value={globalFilter}
          onChange={(e) => setGlobalFilter(e.target.value)}
          className="w-full max-w-md rounded-[24px] bg-[#2c3833] px-4 py-3 text-sm text-[#f2f5f9] placeholder:text-[var(--color-text-muted)] focus:outline-none focus:ring-2 focus:ring-[#84a584]"
        />
        <span className="text-sm text-[var(--color-text-muted)]">
          {table.getFilteredRowModel().rows.length} resultados
        </span>
        <div className="flex items-center gap-1 ml-auto">
          <button
            onClick={() => setViewMode("table")}
            className={`flex h-9 w-9 items-center justify-center rounded-full transition-colors ${
              viewMode === "table"
                ? "bg-[#84a584] text-[#1a1f1a]"
                : "bg-[#2c3833] text-[#5a6a62] hover:bg-[#3d4d45]"
            }`}
            title="Vista tabla"
          >
            <TableIcon size={18} />
          </button>
          <button
            onClick={() => setViewMode("cards")}
            className={`flex h-9 w-9 items-center justify-center rounded-full transition-colors ${
              viewMode === "cards"
                ? "bg-[#84a584] text-[#1a1f1a]"
                : "bg-[#2c3833] text-[#5a6a62] hover:bg-[#3d4d45]"
            }`}
            title="Vista tarjetas"
          >
            <LayoutGrid size={18} />
          </button>
        </div>
      </div>

      {/* Shared Filter Bar */}
      {(availableCategories.length > 0 || hasFilters) && (
        <div className="flex flex-wrap items-center gap-3">
          {/* Category filter pills */}
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-xs text-[#5a6a62]">Categorías:</span>
            {availableCategories.map((cat) => {
              const isActive = activeCategory === cat;
              const colors = CATEGORIA_COLORS[cat] ?? "bg-[#898a7d]/15 text-[#898a7d]";
              return (
                <button
                  key={cat}
                  onClick={() => toggleCategory(cat)}
                  className={`text-xs px-3 py-1.5 rounded-full transition-all ${
                    isActive
                      ? `${colors} ring-1 ring-[#84a584]`
                      : "bg-[#2c3833] text-[#5a6a62] border border-[#3d4d45] hover:border-[#5a6a62]"
                  }`}
                >
                  {cat}
                </button>
              );
            })}
          </div>

          {/* Clear filters button */}
          {hasFilters && (
            <button
              onClick={clearFilters}
              className="flex items-center gap-1 text-xs text-[#84a584] hover:text-[#a5c4a5] transition-colors ml-auto"
            >
              <X size={12} />
              Limpiar filtros
            </button>
          )}
        </div>
      )}

      {/* Table View */}
      {viewMode === "table" && (
        <div className="rounded-[24px] bg-[#1a1f1a] overflow-hidden">
          <table className="w-full">
            <thead>
              {table.getHeaderGroups().map((headerGroup) => (
                <tr key={headerGroup.id} className="border-b border-[#2c3833]">
                  {headerGroup.headers.map((header) => (
                    <th
                      key={header.id}
                      className="px-4 py-4 text-left text-xs font-semibold uppercase tracking-wider text-[var(--color-text-muted)]"
                    >
                      {header.column.getCanSort() ? (
                        <button
                          onClick={header.column.getToggleSortingHandler()}
                          className="flex items-center gap-1 hover:text-[#f2f5f9]"
                        >
                          {flexRender(header.column.columnDef.header, header.getContext())}
                          {header.column.getIsSorted() === "asc" ? (
                            <ArrowUp size={14} />
                          ) : header.column.getIsSorted() === "desc" ? (
                            <ArrowDown size={14} />
                          ) : (
                            <ArrowUpDown size={14} />
                          )}
                        </button>
                      ) : (
                        flexRender(header.column.columnDef.header, header.getContext())
                      )}
                    </th>
                  ))}
                </tr>
              ))}
            </thead>
            <tbody>
              {table.getRowModel().rows.map((row) => (
                <tr
                  key={row.id}
                  className="border-b border-[#2c3833] transition-colors hover:bg-[#2c3833]/30"
                >
                  {row.getVisibleCells().map((cell) => (
                    <td key={cell.id} className="px-4 py-4">
                      {flexRender(cell.column.columnDef.cell, cell.getContext())}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Cards View */}
      {viewMode === "cards" && (
        <div className="space-y-4">
          {/* Sort dropdown - only for cards view (category filters are shared above) */}
          <div className="flex items-center gap-2">
            <SlidersHorizontal size={14} className="text-[#5a6a62]" />
            <select
              value={currentSortOption}
              onChange={(e) => handleSortChange(e.target.value as SortOption)}
              className="bg-[#2c3833] text-[#f2f5f9] text-sm rounded-full px-3 py-1.5 border border-[#3d4d45] focus:outline-none focus:ring-2 focus:ring-[#84a584]"
            >
              <option value="newest">Más recientes</option>
              <option value="oldest">Más antiguas</option>
              <option value="amount-high">Monto: Mayor a menor</option>
              <option value="amount-low">Monto: Menor a mayor</option>
              <option value="name">Nombre A-Z</option>
            </select>
          </div>

          {/* Cards grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {table.getRowModel().rows.map((row) => (
              <LicitacionCard key={row.id} licitacion={row.original} />
            ))}
          </div>
        </div>
      )}

      {/* Pagination */}
      {showPagination && (
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <button
              onClick={() => table.previousPage()}
              disabled={!table.getCanPreviousPage()}
              className="flex h-10 w-10 items-center justify-center rounded-full bg-[#2c3833] text-[#f2f5f9] transition-colors hover:bg-[#3d4d45] disabled:opacity-40"
            >
              <ChevronLeft size={20} />
            </button>
            <button
              onClick={() => table.nextPage()}
              disabled={!table.getCanNextPage()}
              className="flex h-10 w-10 items-center justify-center rounded-full bg-[#2c3833] text-[#f2f5f9] transition-colors hover:bg-[#3d4d45] disabled:opacity-40"
            >
              <ChevronRight size={20} />
            </button>
          </div>
          <span className="text-sm text-[var(--color-text-muted)]">
            Página {table.getState().pagination.pageIndex + 1} de{" "}
            {table.getPageCount()}
          </span>
        </div>
      )}
    </div>
  );
}
