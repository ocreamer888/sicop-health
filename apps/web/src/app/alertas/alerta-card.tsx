"use client";

import { useState } from "react";
import { Bell, BellOff, Pencil, Trash2, Mail } from "lucide-react";
import type { AlertaConfig } from "@/lib/types";
import { deleteAlerta, toggleAlerta } from "./actions";

interface AlertaCardProps {
  alerta: AlertaConfig;
  onEdit: (alerta: AlertaConfig) => void;
}

export function AlertaCard({ alerta, onEdit }: AlertaCardProps) {
  const [deleting, setDeleting] = useState(false);
  const [toggling, setToggling] = useState(false);

  async function handleToggle() {
    setToggling(true);
    await toggleAlerta(alerta.id, !alerta.activo);
    setToggling(false);
  }

  async function handleDelete() {
    if (!confirm(`¿Eliminar alerta "${alerta.nombre}"?`)) return;
    setDeleting(true);
    await deleteAlerta(alerta.id);
  }

  return (
    <div className={`rounded-[24px] border p-5 transition-all ${
      alerta.activo
        ? "bg-[#2c3833] border-[#3d4d45]"
        : "bg-[#1e2820] border-[#2c3833] opacity-60"
    }`}>
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-2">
          {alerta.activo
            ? <Bell size={18} className="text-[#84a584]" />
            : <BellOff size={18} className="text-[#5a6a62]" />
          }
          <h3 className="font-semibold text-[#f9f5df] font-[family-name:var(--font-montserrat)]">
            {alerta.nombre}
          </h3>
        </div>
        <div className="flex items-center gap-1">
          <button
            onClick={() => onEdit(alerta)}
            className="p-2 rounded-[12px] text-[#5a6a62] hover:text-[#f2f5f9] hover:bg-[#3d4d45] transition-all"
          >
            <Pencil size={15} />
          </button>
          <button
            onClick={handleDelete}
            disabled={deleting}
            className="p-2 rounded-[12px] text-[#5a6a62] hover:text-[#a58484] hover:bg-[#a58484]/10 transition-all disabled:opacity-50"
          >
            <Trash2 size={15} />
          </button>
        </div>
      </div>

      {/* Tags */}
      <div className="space-y-2 mb-4">
        {alerta.keywords.length > 0 && (
          <div className="flex flex-wrap gap-1.5">
            {alerta.keywords.map((kw) => (
              <span key={kw} className="px-2.5 py-0.5 rounded-[60px] bg-[#84a584]/15 text-[#84a584] text-xs">
                {kw}
              </span>
            ))}
          </div>
        )}
        {alerta.categorias.length > 0 && (
          <div className="flex flex-wrap gap-1.5">
            {alerta.categorias.map((cat) => (
              <span key={cat} className="px-2.5 py-0.5 rounded-[60px] bg-[#898a7d]/15 text-[#898a7d] text-xs">
                {cat}
              </span>
            ))}
          </div>
        )}
        {alerta.instituciones.length > 0 && (
          <div className="flex flex-wrap gap-1.5">
            {alerta.instituciones.map((inst) => (
              <span key={inst} className="px-2.5 py-0.5 rounded-[60px] bg-[#5d6a85]/15 text-[#8a9bb5] text-xs">
                {inst}
              </span>
            ))}
          </div>
        )}
        {(alerta.monto_min || alerta.monto_max) && (
          <p className="text-xs text-[#5a6a62]">
            Monto: {alerta.monto_min ? `₡${alerta.monto_min.toLocaleString()}` : "0"} –{" "}
            {alerta.monto_max ? `₡${alerta.monto_max.toLocaleString()}` : "∞"}
          </p>
        )}
      </div>

      {/* Footer */}
      <div className="flex items-center justify-between pt-3 border-t border-[#3d4d45]">
        <div className="flex items-center gap-1.5 text-xs text-[#5a6a62]">
          <Mail size={13} />
          <span>Email</span>
        </div>
        <button
          onClick={handleToggle}
          disabled={toggling}
          className={`relative w-10 h-5 rounded-full transition-colors disabled:opacity-50 ${
            alerta.activo ? "bg-[#84a584]" : "bg-[#3d4d45]"
          }`}
        >
          <span className={`absolute top-0.5 w-4 h-4 rounded-full bg-white transition-transform ${
            alerta.activo ? "translate-x-5" : "translate-x-0.5"
          }`} />
        </button>
      </div>
    </div>
  );
}
