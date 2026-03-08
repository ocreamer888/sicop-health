"use client";

import { useState } from "react";
import { Bell, BellOff, Pencil, Trash2, Mail } from "lucide-react";
import type { AlertaConfig } from "@/lib/types";
import { deleteAlerta, toggleAlerta } from "./actions";

// Map institution IDs to display names (must match alerta-form.tsx)
const INSTITUCIONES_LABELS: Record<string, string> = {
  "CCSS": "CCSS",
  "INS": "INS",
  "Hospital": "Hospitales",
  "MSP": "Ministerio de Salud",
  "INCIENSA": "INCIENSA",
  "UCR": "UCR",
  "UNA": "UNA",
  "Tecnológico": "Tecnológicos",
  "CCSS-OTROS": "Otros CCSS",
};

interface AlertaCardProps {
  alerta: AlertaConfig;
  onEdit: (alerta: AlertaConfig) => void;
}

export function AlertaCard({ alerta, onEdit }: AlertaCardProps) {
  const [deleting, setDeleting] = useState(false);
  const [toggling, setToggling] = useState(false);
  const [active, setActive] = useState(alerta.activo);

  async function handleToggle() {
    setToggling(true);
    setActive(!active);
    await toggleAlerta(alerta.id, !active);
    setToggling(false);
  }

  async function handleDelete() {
    if (!confirm(`¿Eliminar alerta "${alerta.nombre}"?`)) return;
    setDeleting(true);
    await deleteAlerta(alerta.id);
  }

  return (
    <div
      className={`rounded-[24px] border p-5 transition-all ${
        active
          ? "bg-[#2c3833] border-[#3d4d45]"
          : "bg-[#1e2820] border-[#2c3833] opacity-60"
      }`}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-2">
          {active
            ? <Bell size={18} className="text-[#84a584] shrink-0" />
            : <BellOff size={18} className="text-[#5a6a62] shrink-0" />
          }
          <h3 className="font-semibold text-[#f9f5df] font-[family-name:var(--font-montserrat)] leading-tight">
            {alerta.nombre}
          </h3>
        </div>
        <div className="flex items-center gap-1 ml-2 shrink-0">
          <button
            onClick={() => onEdit(alerta)}
            className="p-1.5 rounded-[12px] text-[#5a6a62] hover:text-[#f2f5f9] hover:bg-[#3d4d45] transition-all"
          >
            <Pencil size={14} />
          </button>
          <button
            onClick={handleDelete}
            disabled={deleting}
            className="p-1.5 rounded-[12px] text-[#5a6a62] hover:text-[#a58484] hover:bg-[#a58484]/10 transition-all disabled:opacity-50"
          >
            <Trash2 size={14} />
          </button>
        </div>
      </div>

      {/* Tags */}
      <div className="space-y-2 mb-4">
        {alerta.keywords.length > 0 && (
          <div className="flex flex-wrap gap-1.5">
            {alerta.keywords.map((kw) => (
              <span
                key={kw}
                className="px-2.5 py-0.5 rounded-[60px] bg-[#84a584]/15 text-[#84a584] text-xs"
              >
                {kw}
              </span>
            ))}
          </div>
        )}
        {alerta.categorias.length > 0 && (
          <div className="flex flex-wrap gap-1.5">
            {alerta.categorias.map((cat) => (
              <span
                key={cat}
                className="px-2.5 py-0.5 rounded-[60px] bg-[#898a7d]/15 text-[#898a7d] text-xs"
              >
                {cat}
              </span>
            ))}
          </div>
        )}
        {alerta.instituciones.length > 0 && (
          <div className="flex flex-wrap gap-1.5">
            {alerta.instituciones.map((inst) => (
              <span
                key={inst}
                className="px-2.5 py-0.5 rounded-[60px] bg-[#5d6a85]/15 text-[#8a9bb5] text-xs"
              >
                {INSTITUCIONES_LABELS[inst] ?? inst}
              </span>
            ))}
          </div>
        )}
        {(alerta.monto_min || alerta.monto_max) && (
          <p className="text-xs text-[#5a6a62]">
            Monto:{" "}
            {alerta.monto_min ? `₡${alerta.monto_min.toLocaleString("es-CR")}` : "0"}{" "}
            –{" "}
            {alerta.monto_max ? `₡${alerta.monto_max.toLocaleString("es-CR")}` : "∞"}
          </p>
        )}
        {alerta.keywords.length === 0 &&
          alerta.categorias.length === 0 &&
          alerta.instituciones.length === 0 && (
            <p className="text-xs text-[#5a6a62] italic">Todas las licitaciones médicas</p>
          )}
      </div>

      {/* Footer */}
      <div className="flex items-center justify-between pt-3 border-t border-[#3d4d45]">
        <div className="flex items-center gap-1.5 text-xs text-[#5a6a62]">
          <Mail size={12} />
          <span>Email</span>
        </div>
        <button
          onClick={handleToggle}
          disabled={toggling}
          title={active ? "Desactivar alerta" : "Activar alerta"}
          className={`relative w-10 h-5 rounded-full transition-colors disabled:opacity-50 ${
            active ? "bg-[#84a584]" : "bg-[#3d4d45]"
          }`}
        >
          <span
            className={`absolute top-0.5 w-4 h-4 rounded-full bg-white transition-transform ${
              active ? "translate-x-5" : "translate-x-0.5"
            }`}
          />
        </button>
      </div>
    </div>
  );
}
