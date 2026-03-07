# Alert System Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build an end-to-end alert system: `/alertas` CRUD UI + `match-alerts` edge function + `send-email` edge function + Supabase Database Webhook trigger.

**Architecture:** Supabase Database Webhook fires on INSERT into `licitaciones_medicas` → calls `match-alerts` edge function which evaluates active alert rules → for each match inserts into `alertas_enviadas` (dedup) and calls `send-email` → Resend API delivers HTML email. Users manage alerts via full CRUD on `/alertas` page.

**Tech Stack:** Next.js 15 (App Router), Supabase JS v2, Deno (Supabase Edge Functions), Resend API, TypeScript, Tailwind CSS.

---

## Context: What Already Exists

- Tables `alertas_config` and `alertas_enviadas` are already deployed in production Supabase.
- Design system: dark bg `#1a1f1a`, card bg `#2c3833`, accent green `#84a584`, cream text `#f9f5df`, `rounded-[24px]` cards, Montserrat headings, Plus Jakarta body.
- Auth: Supabase auth with middleware protecting all routes except `/auth/*`.
- Server actions pattern: see `apps/web/src/app/auth/actions.ts` for reference.
- Types: `apps/web/src/lib/types.ts` — add `AlertaConfig` type here.
- Nav: `apps/web/src/components/nav.tsx` — add Alertas link.

---

## Task 1: Add `AlertaConfig` type to types.ts

**Files:**
- Modify: `apps/web/src/lib/types.ts`

**Step 1: Add the type**

Append to `apps/web/src/lib/types.ts`:

```typescript
// ─────────────────────────────────────────────
// ALERTAS CONFIG
// ─────────────────────────────────────────────

export interface AlertaConfig {
  id: string
  user_id: string
  nombre: string
  keywords: string[]
  categorias: string[]
  instituciones: string[]
  monto_min: number | null
  monto_max: number | null
  canales: string[]
  activo: boolean
  created_at: string
  updated_at: string
}

export type AlertaFormData = Omit<AlertaConfig, 'id' | 'user_id' | 'created_at' | 'updated_at'>
```

**Step 2: Commit**

```bash
git add apps/web/src/lib/types.ts
git commit -m "feat(alertas): add AlertaConfig type"
```

---

## Task 2: Server Actions for alertas CRUD

**Files:**
- Create: `apps/web/src/app/alertas/actions.ts`

**Step 1: Create the actions file**

```typescript
"use server";

import { createClient } from "@/lib/supabase/server";
import { revalidatePath } from "next/cache";
import type { AlertaFormData } from "@/lib/types";

export async function getAlertas() {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return [];

  const { data, error } = await supabase
    .from("alertas_config")
    .select("*")
    .eq("user_id", user.id)
    .order("created_at", { ascending: false });

  if (error) {
    console.error("[getAlertas]", error.message);
    return [];
  }
  return data ?? [];
}

export async function createAlerta(formData: AlertaFormData) {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return { error: "No autorizado" };

  const { error } = await supabase.from("alertas_config").insert({
    ...formData,
    user_id: user.id,
  });

  if (error) return { error: error.message };
  revalidatePath("/alertas");
  return { success: true };
}

export async function updateAlerta(id: string, formData: AlertaFormData) {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return { error: "No autorizado" };

  const { error } = await supabase
    .from("alertas_config")
    .update({ ...formData, updated_at: new Date().toISOString() })
    .eq("id", id)
    .eq("user_id", user.id);

  if (error) return { error: error.message };
  revalidatePath("/alertas");
  return { success: true };
}

export async function deleteAlerta(id: string) {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return { error: "No autorizado" };

  const { error } = await supabase
    .from("alertas_config")
    .delete()
    .eq("id", id)
    .eq("user_id", user.id);

  if (error) return { error: error.message };
  revalidatePath("/alertas");
  return { success: true };
}

export async function toggleAlerta(id: string, activo: boolean) {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return { error: "No autorizado" };

  const { error } = await supabase
    .from("alertas_config")
    .update({ activo, updated_at: new Date().toISOString() })
    .eq("id", id)
    .eq("user_id", user.id);

  if (error) return { error: error.message };
  revalidatePath("/alertas");
  return { success: true };
}
```

**Step 2: Commit**

```bash
git add apps/web/src/app/alertas/actions.ts
git commit -m "feat(alertas): add server actions for CRUD"
```

---

## Task 3: AlertaForm component

**Files:**
- Create: `apps/web/src/app/alertas/alerta-form.tsx`

**Step 1: Create the form component**

This is a controlled form with tag-input for keywords/institutions and multi-select checkboxes for categories. Uses design system tokens.

```tsx
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
```

**Step 2: Commit**

```bash
git add apps/web/src/app/alertas/alerta-form.tsx
git commit -m "feat(alertas): add AlertaForm component"
```

---

## Task 4: AlertaCard component

**Files:**
- Create: `apps/web/src/app/alertas/alerta-card.tsx`

**Step 1: Create the card component**

```tsx
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
```

**Step 2: Commit**

```bash
git add apps/web/src/app/alertas/alerta-card.tsx
git commit -m "feat(alertas): add AlertaCard component"
```

---

## Task 5: `/alertas` page

**Files:**
- Create: `apps/web/src/app/alertas/page.tsx`

**Step 1: Create the page**

```tsx
"use client";

import { useEffect, useState } from "react";
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

  async function load() {
    setLoading(true);
    const data = await getAlertas();
    setAlertas(data);
    setLoading(false);
  }

  useEffect(() => { load(); }, []);

  async function handleSubmit(data: AlertaFormData) {
    setSaving(true);
    if (editingAlerta) {
      await updateAlerta(editingAlerta.id, data);
    } else {
      await createAlerta(data);
    }
    setSaving(false);
    setShowForm(false);
    setEditingAlerta(null);
    await load();
  }

  function openEdit(alerta: AlertaConfig) {
    setEditingAlerta(alerta);
    setShowForm(true);
  }

  function closeForm() {
    setShowForm(false);
    setEditingAlerta(null);
  }

  return (
    <div className="min-h-screen bg-[#1a1f1a]">
      <div className="max-w-[1393px] mx-auto px-6 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-[#f9f5df] font-[family-name:var(--font-montserrat)]">
              Mis Alertas
            </h1>
            <p className="text-[var(--color-text-muted)] mt-1 font-[family-name:var(--font-plus-jakarta)]">
              Recibe notificaciones cuando aparezcan licitaciones que coincidan con tus criterios.
            </p>
          </div>
          <button
            onClick={() => { setEditingAlerta(null); setShowForm(true); }}
            className="flex items-center gap-2 rounded-[60px] bg-[#84a584] px-6 py-3 text-sm font-medium text-white hover:bg-[#6d8f6d] transition-colors"
          >
            <Plus size={18} />
            Nueva Alerta
          </button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Alert list — 2/3 width */}
          <div className="lg:col-span-2">
            {loading ? (
              <div className="text-center py-20 text-[var(--color-text-muted)]">Cargando alertas...</div>
            ) : alertas.length === 0 ? (
              <div className="rounded-[24px] bg-[#2c3833] border border-[#3d4d45] p-12 text-center">
                <Bell size={48} className="mx-auto mb-4 text-[#3d4d45]" />
                <p className="text-[#f9f5df] font-medium mb-2 font-[family-name:var(--font-montserrat)]">
                  Sin alertas configuradas
                </p>
                <p className="text-[var(--color-text-muted)] text-sm font-[family-name:var(--font-plus-jakarta)]">
                  Crea tu primera alerta para recibir notificaciones de nuevas licitaciones.
                </p>
              </div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {alertas.map((alerta) => (
                  <AlertaCard key={alerta.id} alerta={alerta} onEdit={openEdit} />
                ))}
              </div>
            )}
          </div>

          {/* Form panel — 1/3 width */}
          {showForm && (
            <div className="lg:col-span-1">
              <div className="rounded-[24px] bg-[#2c3833] border border-[#3d4d45] p-6 sticky top-6">
                <div className="flex items-center justify-between mb-5">
                  <h2 className="font-semibold text-[#f9f5df] font-[family-name:var(--font-montserrat)]">
                    {editingAlerta ? "Editar alerta" : "Nueva alerta"}
                  </h2>
                  <button
                    onClick={closeForm}
                    className="p-1.5 rounded-[8px] text-[#5a6a62] hover:text-[#f2f5f9] hover:bg-[#3d4d45]"
                  >
                    <X size={16} />
                  </button>
                </div>
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
```

**Step 2: Commit**

```bash
git add apps/web/src/app/alertas/page.tsx
git commit -m "feat(alertas): add /alertas page with full CRUD UI"
```

---

## Task 6: Add Alertas to Nav

**Files:**
- Modify: `apps/web/src/components/nav.tsx`

**Step 1: Add Bell icon and Alertas link**

In `nav.tsx`, modify the `navItems` array and import:

```typescript
import { Home, Table2, Bell, LogOut } from "lucide-react";

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: Home },
  { href: "/licitaciones", label: "Licitaciones", icon: Table2 },
  { href: "/alertas", label: "Alertas", icon: Bell },
];
```

Remove `Activity` from imports (no longer needed there, unless used elsewhere).

**Step 2: Commit**

```bash
git add apps/web/src/components/nav.tsx
git commit -m "feat(alertas): add Alertas link to nav"
```

---

## Task 7: `match-alerts` Edge Function

**Files:**
- Create: `supabase/functions/match-alerts/index.ts`

**Step 1: Create the function**

```typescript
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
};

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") {
    return new Response("ok", { headers: corsHeaders });
  }

  try {
    const payload = await req.json();
    // Supabase webhook payload: { type, table, schema, record, old_record }
    const record = payload.record;
    if (!record) {
      return new Response(JSON.stringify({ error: "No record in payload" }), { status: 400 });
    }

    const supabase = createClient(
      Deno.env.get("SUPABASE_URL")!,
      Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!,
    );

    // Fetch all active alerts
    const { data: alertas, error: alertasError } = await supabase
      .from("alertas_config")
      .select("*, auth_users:user_id(email)")
      .eq("activo", true);

    if (alertasError) throw alertasError;
    if (!alertas || alertas.length === 0) {
      return new Response(JSON.stringify({ matched: 0 }), { status: 200 });
    }

    const matches: { alerta_id: string; user_id: string; email: string }[] = [];

    for (const alerta of alertas) {
      if (!matchesAlerta(record, alerta)) continue;

      // Try to insert dedup record
      const { error: dupError } = await supabase
        .from("alertas_enviadas")
        .insert({
          alerta_id: alerta.id,
          instcartelno: record.instcartelno,
          user_id: alerta.user_id,
          canal: "email",
        });

      // If conflict (already sent), skip
      if (dupError?.code === "23505") continue;
      if (dupError) {
        console.error("Insert alertas_enviadas error:", dupError.message);
        continue;
      }

      const userEmail = alerta.auth_users?.email;
      if (!userEmail) continue;

      matches.push({ alerta_id: alerta.id, user_id: alerta.user_id, email: userEmail });

      // Call send-email function
      await fetch(`${Deno.env.get("SUPABASE_URL")}/functions/v1/send-email`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")}`,
        },
        body: JSON.stringify({
          user_email: userEmail,
          alerta_nombre: alerta.nombre,
          licitacion: {
            instcartelno: record.instcartelno,
            cartelnm: record.cartelnm,
            instnm: record.instnm,
            categoria: record.categoria,
            monto_colones: record.monto_colones,
            currency_type: record.currency_type,
            biddoc_end_dt: record.biddoc_end_dt,
          },
        }),
      });
    }

    return new Response(JSON.stringify({ matched: matches.length }), { status: 200 });
  } catch (err) {
    console.error("match-alerts error:", err);
    return new Response(JSON.stringify({ error: String(err) }), { status: 500 });
  }
});

interface TenderRecord {
  cartelnm: string | null;
  categoria: string | null;
  inst_code: string | null;
  monto_colones: number | null;
}

interface AlertaRule {
  keywords: string[];
  categorias: string[];
  instituciones: string[];
  monto_min: number | null;
  monto_max: number | null;
}

function matchesAlerta(record: TenderRecord, alerta: AlertaRule): boolean {
  // Keywords: any keyword found in cartelnm (OR logic)
  if (alerta.keywords.length > 0) {
    const title = (record.cartelnm ?? "").toLowerCase();
    const hasKeyword = alerta.keywords.some((kw) => title.includes(kw.toLowerCase()));
    if (!hasKeyword) return false;
  }

  // Categories: if filter set, must match
  if (alerta.categorias.length > 0 && record.categoria) {
    if (!alerta.categorias.includes(record.categoria)) return false;
  }

  // Institutions: if filter set, must match
  if (alerta.instituciones.length > 0 && record.inst_code) {
    if (!alerta.instituciones.includes(record.inst_code)) return false;
  }

  // Amount range
  if (alerta.monto_min !== null && record.monto_colones !== null) {
    if (record.monto_colones < alerta.monto_min) return false;
  }
  if (alerta.monto_max !== null && record.monto_colones !== null) {
    if (record.monto_colones > alerta.monto_max) return false;
  }

  return true;
}
```

**Note:** The join `.select("*, auth_users:user_id(email)")` won't work on `auth.users` via the JS client. Instead, after matching we need to look up the email separately. Replace the select with:

```typescript
const { data: alertas } = await supabase
  .from("alertas_config")
  .select("*")
  .eq("activo", true);
```

Then for each match, look up the user's email:

```typescript
const { data: userData } = await supabase.auth.admin.getUserById(alerta.user_id);
const userEmail = userData?.user?.email;
```

**Step 2: Commit**

```bash
git add supabase/functions/match-alerts/index.ts
git commit -m "feat(alertas): add match-alerts edge function"
```

---

## Task 8: `send-email` Edge Function

**Files:**
- Create: `supabase/functions/send-email/index.ts`

**Step 1: Create the function**

```typescript
const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
};

interface LicitacionData {
  instcartelno: string;
  cartelnm: string | null;
  instnm: string | null;
  categoria: string | null;
  monto_colones: number | null;
  currency_type: string | null;
  biddoc_end_dt: string | null;
}

interface EmailPayload {
  user_email: string;
  alerta_nombre: string;
  licitacion: LicitacionData;
}

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") {
    return new Response("ok", { headers: corsHeaders });
  }

  try {
    const { user_email, alerta_nombre, licitacion }: EmailPayload = await req.json();

    const siteUrl = Deno.env.get("SITE_URL") ?? "https://sicop-health-web.vercel.app";
    const resendKey = Deno.env.get("RESEND_API_KEY");
    if (!resendKey) throw new Error("RESEND_API_KEY not set");

    const formatMonto = (monto: number | null, currency: string | null) => {
      if (!monto) return "—";
      const sym = currency === "USD" ? "$" : "₡";
      return `${sym}${monto.toLocaleString("es-CR")}`;
    };

    const formatDate = (dt: string | null) => {
      if (!dt) return "—";
      return new Date(dt).toLocaleDateString("es-CR", { day: "2-digit", month: "short", year: "numeric" });
    };

    const html = `
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Nueva licitación — SICOP Health</title>
</head>
<body style="margin:0;padding:0;background-color:#1a1f1a;font-family:'Helvetica Neue',Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#1a1f1a;padding:40px 16px;">
    <tr>
      <td align="center">
        <table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;">
          <!-- Header -->
          <tr>
            <td style="padding-bottom:24px;">
              <span style="font-size:22px;font-weight:700;color:#f9f5df;letter-spacing:-0.5px;">SICOP</span>
              <span style="font-size:13px;color:#84a584;margin-left:8px;">Health Intelligence</span>
            </td>
          </tr>
          <!-- Divider -->
          <tr><td style="height:1px;background-color:#84a584;margin-bottom:24px;"></td></tr>
          <!-- Body -->
          <tr>
            <td style="background-color:#2c3833;border-radius:24px;padding:32px;margin-top:24px;">
              <p style="margin:0 0 8px;font-size:12px;color:#84a584;text-transform:uppercase;letter-spacing:1px;">Alerta: ${alerta_nombre}</p>
              <h1 style="margin:0 0 24px;font-size:20px;font-weight:700;color:#f9f5df;line-height:1.3;">
                ${licitacion.cartelnm ?? "Nueva licitación detectada"}
              </h1>
              <!-- Details table -->
              <table width="100%" cellpadding="0" cellspacing="0">
                <tr>
                  <td style="padding:10px 0;border-bottom:1px solid #3d4d45;">
                    <span style="font-size:11px;color:#5a6a62;text-transform:uppercase;">Institución</span><br>
                    <span style="font-size:14px;color:#f2f5f9;">${licitacion.instnm ?? "—"}</span>
                  </td>
                </tr>
                <tr>
                  <td style="padding:10px 0;border-bottom:1px solid #3d4d45;">
                    <span style="font-size:11px;color:#5a6a62;text-transform:uppercase;">Categoría</span><br>
                    <span style="font-size:14px;color:#f2f5f9;">${licitacion.categoria ?? "—"}</span>
                  </td>
                </tr>
                <tr>
                  <td style="padding:10px 0;border-bottom:1px solid #3d4d45;">
                    <span style="font-size:11px;color:#5a6a62;text-transform:uppercase;">Monto</span><br>
                    <span style="font-size:14px;color:#f2f5f9;">${formatMonto(licitacion.monto_colones, licitacion.currency_type)}</span>
                  </td>
                </tr>
                <tr>
                  <td style="padding:10px 0;">
                    <span style="font-size:11px;color:#5a6a62;text-transform:uppercase;">Cierre de ofertas</span><br>
                    <span style="font-size:14px;color:#f2f5f9;">${formatDate(licitacion.biddoc_end_dt)}</span>
                  </td>
                </tr>
              </table>
              <!-- CTA -->
              <div style="margin-top:28px;text-align:center;">
                <a href="${siteUrl}/licitaciones/${licitacion.instcartelno}"
                   style="display:inline-block;background-color:#84a584;color:#ffffff;text-decoration:none;padding:14px 32px;border-radius:60px;font-size:14px;font-weight:600;">
                  Ver Licitación
                </a>
              </div>
            </td>
          </tr>
          <!-- Footer -->
          <tr>
            <td style="padding:24px 0 0;text-align:center;">
              <p style="margin:0;font-size:11px;color:#3d4d45;">
                Recibiste este email porque tienes configurada la alerta "${alerta_nombre}" en SICOP Health Intelligence.
              </p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>`;

    const res = await fetch("https://api.resend.com/emails", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${resendKey}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        from: "SICOP Health <alertas@sicop-health.com>",
        to: [user_email],
        subject: `Nueva licitación: ${licitacion.cartelnm ?? licitacion.instcartelno}`,
        html,
      }),
    });

    if (!res.ok) {
      const body = await res.text();
      throw new Error(`Resend error ${res.status}: ${body}`);
    }

    const data = await res.json();
    return new Response(JSON.stringify({ sent: true, id: data.id }), { status: 200 });
  } catch (err) {
    console.error("send-email error:", err);
    return new Response(JSON.stringify({ error: String(err) }), { status: 500 });
  }
});
```

**Step 2: Commit**

```bash
git add supabase/functions/send-email/index.ts
git commit -m "feat(alertas): add send-email edge function with Resend"
```

---

## Task 9: Deploy Edge Functions + Configure Webhook

**Step 1: Install Supabase CLI (if not already)**

```bash
brew install supabase/tap/supabase
supabase login
supabase link --project-ref ofjsiatheyuhhdpxfaea
```

**Step 2: Set Resend secret**

First, create a Resend account at https://resend.com and get your API key.

```bash
supabase secrets set RESEND_API_KEY=re_xxxxxxxxxxxxx
supabase secrets set SITE_URL=https://sicop-health-web.vercel.app
```

**Step 3: Deploy functions**

```bash
supabase functions deploy match-alerts --no-verify-jwt
supabase functions deploy send-email --no-verify-jwt
```

`--no-verify-jwt` because the webhook call won't have a user JWT.

**Step 4: Configure Supabase Database Webhook**

In Supabase Dashboard → Database → Webhooks → Create:
- Name: `on-new-licitacion`
- Table: `licitaciones_medicas`
- Events: INSERT
- Type: HTTP Request
- URL: `https://ofjsiatheyuhhdpxfaea.supabase.co/functions/v1/match-alerts`
- Method: POST
- HTTP Headers:
  - `Content-Type: application/json`
  - `Authorization: Bearer <SUPABASE_SERVICE_ROLE_KEY>`

**Step 5: Verify**

Insert a test row manually in Supabase Dashboard → Table Editor into `licitaciones_medicas`, then check:
- Supabase Dashboard → Functions → Logs for `match-alerts`
- Your email inbox

---

## Task 10: End-to-end smoke test

**Step 1: Create a test alert via the UI**

1. Go to `/alertas`
2. Create alert: name "Test Insulina", keyword "test", category MEDICAMENTO, email channel
3. Verify card appears

**Step 2: Trigger a match**

Insert a test tender in Supabase Dashboard:
```sql
INSERT INTO licitaciones_medicas (instcartelno, cartelnm, instnm, categoria, es_medica, estado)
VALUES ('TEST-001', 'Compra de insulina test', 'CCSS', 'MEDICAMENTO', true, 'Publicado');
```

**Step 3: Check results**

- `alertas_enviadas` should have a row for this match
- Email should arrive within 30 seconds

**Step 4: Verify dedup**

Run the same INSERT again (will fail on UNIQUE constraint in `licitaciones_medicas` — correct behavior).
Try updating the record — no duplicate email sent (webhook is INSERT-only).

**Step 5: Clean up test data**

```sql
DELETE FROM alertas_enviadas WHERE instcartelno = 'TEST-001';
DELETE FROM licitaciones_medicas WHERE instcartelno = 'TEST-001';
```

---

## Summary of Files Created/Modified

| File | Action |
|------|--------|
| `apps/web/src/lib/types.ts` | Add `AlertaConfig`, `AlertaFormData` types |
| `apps/web/src/app/alertas/actions.ts` | Create — server actions |
| `apps/web/src/app/alertas/alerta-form.tsx` | Create — form component |
| `apps/web/src/app/alertas/alerta-card.tsx` | Create — card component |
| `apps/web/src/app/alertas/page.tsx` | Create — main page |
| `apps/web/src/components/nav.tsx` | Modify — add Alertas link |
| `supabase/functions/match-alerts/index.ts` | Create — edge function |
| `supabase/functions/send-email/index.ts` | Create — edge function |
| Supabase Dashboard | Manual — webhook + secrets |
