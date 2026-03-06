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
import { TIPO_LABELS } from "@/lib/types";
import type { LicitacionPreview, Categoria } from "@/lib/types";

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

export function LicitacionesTable({
  data,
  showPagination = true,
  pageSize = 10,
}: LicitacionesTableProps) {
  const [sorting, setSorting] = useState<SortingState>([]);
  const [globalFilter, setGlobalFilter] = useState("");

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
      cell: ({ row }) => (
        <span className="font-mono text-sm text-[#f9f5df]">
          {formatCurrency(
            row.getValue("monto_colones"),
            row.original.currency_type
          )}
        </span>
      ),
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
        <span className="text-xs text-[var(--color-text-muted)]">
          {row.getValue("estado") || "N/A"}
        </span>
      ),
    },
  ];

  const table = useReactTable({
    data,
    columns,
    state: { sorting, globalFilter },
    onSortingChange: setSorting,
    onGlobalFilterChange: setGlobalFilter,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    initialState: { pagination: { pageSize } },
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
