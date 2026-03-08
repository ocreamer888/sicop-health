"use client";

import { useState } from "react";
import { X, Plus } from "lucide-react";
import type { AlertaConfig, AlertaFormData } from "@/lib/types";

const CATEGORIAS = ["MEDICAMENTO", "EQUIPAMIENTO", "INSUMO", "SERVICIO"] as const;

interface AlertaFormProps {
  initial?: AlertaConfig;
  onSubmit: (data: AlertaFormData) => Promise<void>;
  onCancel: () => void;
  loading?: boolean;
}

export function AlertaForm({ initial, onSubmit, onCancel, loading }: AlertaFormProps) {
  const [nombre, setNombre] = useState(initial?.nombre ?? "");
  const [keywords, setKeywords] = useState<string[]>(initial?.keywords ?? []);
  const [kwInput, setKwInput] = useState("");
  const [categorias, setCategorias] = useState<string[]>(initial?.categorias ?? []);
  const [instituciones, setInstituciones] = useState<string[]>(initial?.instituciones ?? []);
  const [instInput, setInstInput] = useState("");
  const [montoMin, setMontoMin] = useState<string>(initial?.monto_min?.toString() ?? "");
  const [montoMax, setMontoMax] = useState<string>(initial?.monto_max?.toString() ?? "");
  const [activo, setActivo] = useState(initial?.activo ?? true);

  function addTag(value: string, list: string[], setList: (v: string[]) => void, setInput: (v: string) => void) {
    const trimmed = value.trim().toLowerCase();
    if (trimmed && !list.includes(trimmed)) setList([...list, trimmed]);
    setInput("");
  }

  function removeTag(value: string, list: string[], setList: (v: string[]) => void) {
    setList(list.filter((t) => t !== value));
  }

  function toggleCategoria(cat: string) {
    setCategorias((prev) =>
      prev.includes(cat) ? prev.filter((c) => c !== cat) : [...prev, cat]
    );
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    await onSubmit({
      nombre,
      keywords,
      categorias,
      instituciones,
      monto_min: montoMin ? parseFloat(montoMin) : null,
      monto_max: montoMax ? parseFloat(montoMax) : null,
      canales: ["email"],
      activo,
    });
  }

  const inputCls = "w-full rounded-[12px] bg-[#1a1f1a] border border-[#3d4d45] px-4 py-2.5 text-[#f2f5f9] text-sm placeholder:text-[#5a6a62] focus:outline-none focus:border-[#84a584]";
  const labelCls = "block text-xs font-medium text-[var(--color-text-muted)] mb-1.5 uppercase tracking-wide";

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      {/* Nombre */}
      <div>
        <label className={labelCls}>Nombre de la alerta *</label>
        <input
          className={inputCls}
          value={nombre}
          onChange={(e) => setNombre(e.target.value)}
          placeholder="Ej: Insulinas CCSS"
          required
        />
      </div>

      {/* Keywords */}
      <div>
        <label className={labelCls}>Palabras clave</label>
        <div className="flex flex-wrap gap-2 mb-2">
          {keywords.map((kw) => (
            <span key={kw} className="flex items-center gap-1 px-3 py-1 rounded-[60px] bg-[#84a584]/20 text-[#84a584] text-xs">
              {kw}
              <button type="button" onClick={() => removeTag(kw, keywords, setKeywords)}>
                <X size={12} />
              </button>
            </span>
          ))}
        </div>
        <div className="flex gap-2">
          <input
            className={inputCls}
            value={kwInput}
            onChange={(e) => setKwInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") { e.preventDefault(); addTag(kwInput, keywords, setKeywords, setKwInput); }
            }}
            placeholder="Escribe y presiona Enter"
          />
          <button
            type="button"
            onClick={() => addTag(kwInput, keywords, setKeywords, setKwInput)}
            className="px-3 rounded-[12px] border border-[#3d4d45] text-[#84a584] hover:bg-[#84a584]/10"
          >
            <Plus size={16} />
          </button>
        </div>
      </div>

      {/* Categorías */}
      <div>
        <label className={labelCls}>Categorías (vacío = todas)</label>
        <div className="flex flex-wrap gap-2">
          {CATEGORIAS.map((cat) => (
            <button
              key={cat}
              type="button"
              onClick={() => toggleCategoria(cat)}
              className={`px-4 py-1.5 rounded-[60px] text-xs font-medium border transition-all ${
                categorias.includes(cat)
                  ? "bg-[#84a584] border-[#84a584] text-white"
                  : "border-[#3d4d45] text-[#f2f5f9] hover:border-[#84a584]/50"
              }`}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      {/* Instituciones */}
      <div>
        <label className={labelCls}>Instituciones (código, vacío = todas)</label>
        <div className="flex flex-wrap gap-2 mb-2">
          {instituciones.map((inst) => (
            <span key={inst} className="flex items-center gap-1 px-3 py-1 rounded-[60px] bg-[#898a7d]/20 text-[#898a7d] text-xs">
              {inst}
              <button type="button" onClick={() => removeTag(inst, instituciones, setInstituciones)}>
                <X size={12} />
              </button>
            </span>
          ))}
        </div>
        <div className="flex gap-2">
          <input
            className={inputCls}
            value={instInput}
            onChange={(e) => setInstInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") { e.preventDefault(); addTag(instInput, instituciones, setInstituciones, setInstInput); }
            }}
            placeholder="Ej: 0001102555"
          />
          <button
            type="button"
            onClick={() => addTag(instInput, instituciones, setInstituciones, setInstInput)}
            className="px-3 rounded-[12px] border border-[#3d4d45] text-[#898a7d] hover:bg-[#898a7d]/10"
          >
            <Plus size={16} />
          </button>
        </div>
      </div>

      {/* Montos */}
      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className={labelCls}>Monto mínimo (₡)</label>
          <input
            className={inputCls}
            type="number"
            value={montoMin}
            onChange={(e) => setMontoMin(e.target.value)}
            placeholder="Opcional"
          />
        </div>
        <div>
          <label className={labelCls}>Monto máximo (₡)</label>
          <input
            className={inputCls}
            type="number"
            value={montoMax}
            onChange={(e) => setMontoMax(e.target.value)}
            placeholder="Opcional"
          />
        </div>
      </div>

      {/* Canales */}
      <div>
        <label className={labelCls}>Canales de notificación</label>
        <div className="flex gap-3">
          <label className="flex items-center gap-2 text-sm text-[#f2f5f9] cursor-pointer">
            <input type="checkbox" checked readOnly className="accent-[#84a584]" />
            Email
          </label>
          <label className="flex items-center gap-2 text-sm text-[#5a6a62] cursor-not-allowed">
            <input type="checkbox" disabled className="accent-[#84a584]" />
            WhatsApp <span className="text-xs">(próximamente)</span>
          </label>
        </div>
      </div>

      {/* Activo toggle */}
      <div className="flex items-center justify-between rounded-[16px] bg-[#1a1f1a] px-4 py-3">
        <span className="text-sm text-[#f2f5f9]">Alerta activa</span>
        <button
          type="button"
          onClick={() => setActivo(!activo)}
          className={`relative w-11 h-6 rounded-full transition-colors ${activo ? "bg-[#84a584]" : "bg-[#3d4d45]"}`}
        >
          <span className={`absolute top-1 w-4 h-4 rounded-full bg-white transition-transform ${activo ? "translate-x-6" : "translate-x-1"}`} />
        </button>
      </div>

      {/* Actions */}
      <div className="flex gap-3 pt-2">
        <button
          type="submit"
          disabled={loading || !nombre}
          className="flex-1 rounded-[60px] bg-[#84a584] px-6 py-2.5 text-sm font-medium text-white disabled:opacity-50 hover:bg-[#6d8f6d] transition-colors"
        >
          {loading ? "Guardando..." : initial ? "Guardar cambios" : "Crear alerta"}
        </button>
        <button
          type="button"
          onClick={onCancel}
          className="px-6 py-2.5 rounded-[60px] border border-[#3d4d45] text-sm text-[#f2f5f9] hover:bg-[#2c3833] transition-colors"
        >
          Cancelar
        </button>
      </div>
    </form>
  );
}
