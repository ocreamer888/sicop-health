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
} from "@tanstack/react-table";
import { useState } from "react";
import Link from "next/link";
import { ArrowUpDown, ArrowUp, ArrowDown, ChevronLeft, ChevronRight } from "lucide-react";
import { Badge } from "./ui/badge";
import type { Licitacion, Categoria, TypeKey } from "@/lib/types";

// Allow partial Licitacion for dashboard preview (subset of fields)
type LicitacionLike = Pick<
  Licitacion,
  'id' | 'numero_procedimiento' | 'descripcion' | 'institucion' | 
  'categoria' | 'monto_colones' | 'fecha_tramite' | 'estado' | 'es_medica'
> & Partial<Pick<Licitacion, 'type_key' | 'raw_data'>>

interface LicitacionesTableProps {
  data: LicitacionLike[];
  showPagination?: boolean;
  pageSize?: number;
}

const categoriaLabels: Record<Categoria, string> = {
  MEDICAMENTO: "Medicamento",
  EQUIPAMIENTO: "Equipamiento",
  INSUMO: "Insumo",
  SERVICIO: "Servicio",
};

const fuenteLabels: Record<TypeKey, string> = {
  RPT_PUB: "Periódico Oficial",
  RPT_ADJ: "Adjudicación",
  RPT_MOD: "Modificación",
};

const categoriaVariants: Record<Categoria, "default" | "secondary" | "sage" | "olive"> = {
  MEDICAMENTO: "sage",
  EQUIPAMIENTO: "secondary",
  INSUMO: "olive",
  SERVICIO: "default",
};

function formatCurrency(amount: number | null): string {
  if (amount === null || amount === undefined) return "N/A";
  return `₡${amount.toLocaleString()}`;
}

function formatDate(dateStr: string | null): string {
  if (!dateStr) return "N/A";
  return new Date(dateStr).toLocaleDateString("es-CR", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

export function LicitacionesTable({
  data,
  showPagination = true,
  pageSize = 10,
}: LicitacionesTableProps) {
  const [sorting, setSorting] = useState<SortingState>([]);
  const [globalFilter, setGlobalFilter] = useState("");

  const columns: ColumnDef<LicitacionLike>[] = [
    {
      accessorKey: "numero_procedimiento",
      header: "ID",
      cell: ({ row }) => (
        <Link
          href={`/licitaciones/${row.original.id}`}
          className="font-mono text-sm text-[#84a584] hover:underline"
        >
          {row.getValue("numero_procedimiento")}
        </Link>
      ),
    },
    {
      accessorKey: "descripcion",
      header: "Título",
      cell: ({ row }) => (
        <div className="max-w-md">
          <p className="font-medium text-[#f2f5f9] line-clamp-2">
            {row.getValue("descripcion") || "Sin título"}
          </p>
        </div>
      ),
    },
    {
      accessorKey: "institucion",
      header: "Entidad",
      cell: ({ row }) => (
        <span className="text-sm text-[#e4e4e4]">
          {row.getValue("institucion") || "N/A"}
        </span>
      ),
    },
    {
      accessorKey: "categoria",
      header: "Categoría",
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
        const amount = row.getValue("monto_colones") as number | null;
        return (
          <span className="font-mono text-sm text-[#f9f5df]">
            {formatCurrency(amount)}
          </span>
        );
      },
    },
    {
      accessorKey: "fecha_tramite",
      header: "Fecha Trámite",
      cell: ({ row }) => (
        <span className="text-sm text-[#e4e4e4]">
          {formatDate(row.getValue("fecha_tramite"))}
        </span>
      ),
    },
    {
      accessorKey: "estado",
      header: "Estado",
      cell: ({ row }) => (
        <span className="text-xs text-[var(--color-text-muted)]">
          {row.getValue("estado") || "N/A"}
        </span>
      ),
    },
  ];

  const table = useReactTable({
    data,
    columns,
    state: {
      sorting,
      globalFilter,
    },
    onSortingChange: setSorting,
    onGlobalFilterChange: setGlobalFilter,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    initialState: {
      pagination: {
        pageSize,
      },
    },
  });

  return (
    <div className="space-y-4">
      {/* Search */}
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
      </div>

      {/* Table */}
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
                        {flexRender(
                          header.column.columnDef.header,
                          header.getContext()
                        )}
                        {header.column.getIsSorted() ? (
                          header.column.getIsSorted() === "asc" ? (
                            <ArrowUp size={14} />
                          ) : (
                            <ArrowDown size={14} />
                          )
                        ) : (
                          <ArrowUpDown size={14} />
                        )}
                      </button>
                    ) : (
                      flexRender(
                        header.column.columnDef.header,
                        header.getContext()
                      )
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
