"use client";

import { useEffect, useState, useCallback } from "react";
import { Bell, Plus, X } from "lucide-react";
import type { AlertaConfig, AlertaFormData } from "@/lib/types";
import { getAlertas, createAlerta, updateAlerta } from "./actions";
import { AlertaForm } from "./alerta-form";
import { AlertaCard } from "./alerta-card";

export default function AlertasPage() {
  const [alertas, setAlertas] = useState<AlertaConfig[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingAlerta, setEditingAlerta] = useState<AlertaConfig | null>(null);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    const data = await getAlertas();
    setAlertas(data);
    setLoading(false);
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  async function handleSubmit(data: AlertaFormData) {
    setSaving(true);
    setError(null);
    
    const result = editingAlerta 
      ? await updateAlerta(editingAlerta.id, data)
      : await createAlerta(data);
    
    setSaving(false);
    
    if (result?.error) {
      setError(result.error);
      return;
    }
    
    closeForm();
    await load();
  }

  function handleDuplicate(alerta: AlertaConfig) {
    const duplicated: AlertaFormData = {
      nombre: `${alerta.nombre} (copia)`,
      keywords: alerta.keywords ?? [],
      categorias: alerta.categorias ?? [],
      instituciones: alerta.instituciones ?? [],
      monto_min: alerta.monto_min ?? null,
      monto_max: alerta.monto_max ?? null,
      canales: alerta.canales ?? ["email"],
      activo: true,
    };
    
    // Pre-fill form with duplicated data
    setEditingAlerta({
      ...alerta,
      id: "", // Clear ID so it's treated as new
      nombre: duplicated.nombre,
      activo: true,
    } as AlertaConfig);
    setShowForm(true);
  }

  function openEdit(alerta: AlertaConfig) {
    setEditingAlerta(alerta);
    setShowForm(true);
  }

  function openCreate() {
    setEditingAlerta(null);
    setShowForm(true);
  }

  function closeForm() {
    setShowForm(false);
    setEditingAlerta(null);
    setError(null);
  }

  return (
    <div className="min-h-screen bg-[#1a1f1a]">
      <div className="max-w-[1393px] mx-auto px-6 py-8">

        {/* Header */}
        <div className="flex items-start justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-[#f9f5df] font-[family-name:var(--font-montserrat)]">
              Mis Alertas
            </h1>
            <p className="text-[var(--color-text-muted)] mt-1 font-[family-name:var(--font-plus-jakarta)]">
              Recibe notificaciones cuando aparezcan licitaciones que coincidan con tus criterios.
            </p>
          </div>
          <button
            onClick={openCreate}
            className="flex items-center gap-2 rounded-[60px] bg-[#84a584] px-6 py-3 text-sm font-medium text-white hover:bg-[#6d8f6d] transition-colors shrink-0"
          >
            <Plus size={16} />
            Nueva Alerta
          </button>
        </div>

        <div className={`grid gap-6 ${showForm ? "grid-cols-1 lg:grid-cols-3" : "grid-cols-1"}`}>

          {/* Alert list */}
          <div className={showForm ? "lg:col-span-2" : ""}>
            {loading ? (
              <div className="text-center py-24 text-[var(--color-text-muted)] font-[family-name:var(--font-plus-jakarta)]">
                Cargando alertas...
              </div>
            ) : alertas.length === 0 ? (
              <div className="rounded-[24px] bg-[#2c3833] border border-[#3d4d45] p-16 text-center">
                <Bell size={48} className="mx-auto mb-4 text-[#3d4d45]" />
                <p className="text-[#f9f5df] font-semibold mb-2 font-[family-name:var(--font-montserrat)]">
                  Sin alertas configuradas
                </p>
                <p className="text-[var(--color-text-muted)] text-sm mb-6 font-[family-name:var(--font-plus-jakarta)]">
                  Crea tu primera alerta para recibir notificaciones de nuevas licitaciones.
                </p>
                <button
                  onClick={openCreate}
                  className="inline-flex items-center gap-2 rounded-[60px] bg-[#84a584] px-6 py-2.5 text-sm font-medium text-white hover:bg-[#6d8f6d] transition-colors"
                >
                  <Plus size={16} />
                  Crear primera alerta
                </button>
              </div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {alertas.map((alerta) => (
                  <AlertaCard
                    key={alerta.id}
                    alerta={alerta}
                    onEdit={openEdit}
                    onDuplicate={handleDuplicate}
                  />
                ))}
              </div>
            )}
          </div>

          {/* Form panel */}
          {showForm && (
            <div className="lg:col-span-1">
              <div className="rounded-[24px] bg-[#2c3833] border border-[#3d4d45] p-6 sticky top-6">
                <div className="flex items-center justify-between mb-5">
                  <h2 className="font-semibold text-[#f9f5df] font-[family-name:var(--font-montserrat)]">
                    {editingAlerta ? "Editar alerta" : "Nueva alerta"}
                  </h2>
                  <button
                    onClick={closeForm}
                    className="p-1.5 rounded-[8px] text-[#5a6a62] hover:text-[#f2f5f9] hover:bg-[#3d4d45] transition-all"
                  >
                    <X size={16} />
                  </button>
                </div>
                
                {error && (
                  <div className="mb-4 p-3 rounded-[12px] bg-[#a58484]/20 border border-[#a58484]/40 text-[#e09090] text-sm">
                    ⚠️ {error}
                  </div>
                )}
                
                <AlertaForm
                  initial={editingAlerta ?? undefined}
                  onSubmit={handleSubmit}
                  onCancel={closeForm}
                  loading={saving}
                />
              </div>
            </div>
          )}

        </div>
      </div>
    </div>
  );
}
