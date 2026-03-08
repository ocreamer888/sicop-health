"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { completeOnboarding } from "./actions";

const CATEGORIAS = [
  { id: "MEDICAMENTO", label: "Medicamentos" },
  { id: "EQUIPAMIENTO", label: "Equipamiento médico" },
  { id: "INSUMO", label: "Insumos" },
  { id: "SERVICIO", label: "Servicios" },
];

const INSTITUCIONES = [
  { id: "CCSS", label: "CCSS" },
  { id: "Hospitales", label: "Hospitales Nacionales" },
  { id: "INS", label: "INS" },
  { id: "MS", label: "Ministerio de Salud" },
  { id: "Todas", label: "Todas" },
];

const MONTOS = [
  { value: 5_000_000, label: "₡5M+" },
  { value: 20_000_000, label: "₡20M+" },
  { value: 50_000_000, label: "₡50M+" },
  { value: null, label: "Sin filtro" },
];

export default function OnboardingPage() {
  const router = useRouter();
  const [step, setStep] = useState(1);
  const [categorias, setCategorias] = useState<string[]>([]);
  const [instituciones, setInstituciones] = useState<string[]>([]);
  const [montoMin, setMontoMin] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);

  function toggleItem(value: string, list: string[], setList: (v: string[]) => void) {
    setList(list.includes(value) ? list.filter((v) => v !== value) : [...list, value]);
  }

  async function handleFinish() {
    setLoading(true);
    try {
      await completeOnboarding({ categorias, instituciones, monto_min: montoMin });
      router.push("/dashboard");
      router.refresh();
    } catch (error) {
      console.error("Onboarding failed:", error);
      setLoading(false);
    }
  }

  const pillCls = (selected: boolean) =>
    `px-5 py-2.5 rounded-[60px] border text-sm font-medium transition-all cursor-pointer ${
      selected
        ? "bg-[#84a584] border-[#84a584] text-white"
        : "border-[#3d4d45] text-[#f2f5f9] hover:border-[#84a584]/50"
    }`;

  return (
    <div className="min-h-screen bg-[#1a1f1a] flex items-center justify-center px-4">
      <div className="w-full max-w-lg">
        {/* Progress dots */}
        <div className="flex items-center justify-center gap-2 mb-8">
          {[1, 2, 3].map((s) => (
            <div
              key={s}
              className={`h-2 rounded-full transition-all ${
                s === step ? "w-8 bg-[#84a584]" : s < step ? "w-2 bg-[#84a584]/60" : "w-2 bg-[#3d4d45]"
              }`}
            />
          ))}
        </div>

        <div className="rounded-[24px] bg-[#2c3833] border border-[#3d4d45] p-8">
          <p className="text-xs text-[#84a584] font-medium uppercase tracking-wider mb-2">
            Paso {step} de 3
          </p>

          {step === 1 && (
            <>
              <h2 className="text-xl font-bold text-[#f9f5df] mb-1 font-[family-name:var(--font-montserrat)]">
                🎯 Personaliza tu radar de oportunidades
              </h2>
              <p className="text-[var(--color-text-muted)] text-sm mb-6 font-[family-name:var(--font-plus-jakarta)]">
                ¿Qué tipo de productos distribuyes o vendes?
              </p>
              <div className="flex flex-wrap gap-2 mb-8">
                {CATEGORIAS.map((c) => (
                  <button
                    key={c.id}
                    type="button"
                    className={pillCls(categorias.includes(c.id))}
                    onClick={() => toggleItem(c.id, categorias, setCategorias)}
                  >
                    {c.label}
                  </button>
                ))}
              </div>
              <button
                onClick={() => setStep(2)}
                disabled={categorias.length === 0}
                className="w-full rounded-[60px] bg-[#84a584] py-3 text-white font-medium disabled:opacity-40 hover:bg-[#6d8f6d] transition-colors"
              >
                Siguiente →
              </button>
            </>
          )}

          {step === 2 && (
            <>
              <h2 className="text-xl font-bold text-[#f9f5df] mb-1 font-[family-name:var(--font-montserrat)]">
                🏥 Instituciones objetivo
              </h2>
              <p className="text-[var(--color-text-muted)] text-sm mb-6 font-[family-name:var(--font-plus-jakarta)]">
                ¿A qué instituciones te interesa venderle?
              </p>
              <div className="flex flex-wrap gap-2 mb-8">
                {INSTITUCIONES.map((inst) => (
                  <button
                    key={inst.id}
                    type="button"
                    className={pillCls(instituciones.includes(inst.id))}
                    onClick={() => toggleItem(inst.id, instituciones, setInstituciones)}
                  >
                    {inst.label}
                  </button>
                ))}
              </div>
              <div className="flex gap-3">
                <button
                  onClick={() => setStep(1)}
                  className="px-6 py-3 rounded-[60px] border border-[#3d4d45] text-[#f2f5f9] text-sm hover:bg-[#3d4d45] transition-colors"
                >
                  ← Atrás
                </button>
                <button
                  onClick={() => setStep(3)}
                  disabled={instituciones.length === 0}
                  className="flex-1 rounded-[60px] bg-[#84a584] py-3 text-white font-medium disabled:opacity-40 hover:bg-[#6d8f6d] transition-colors"
                >
                  Siguiente →
                </button>
              </div>
            </>
          )}

          {step === 3 && (
            <>
              <h2 className="text-xl font-bold text-[#f9f5df] mb-1 font-[family-name:var(--font-montserrat)]">
                💰 Monto mínimo de interés
              </h2>
              <p className="text-[var(--color-text-muted)] text-sm mb-6 font-[family-name:var(--font-plus-jakarta)]">
                ¿Cuál es el valor mínimo de licitación que te interesa?
              </p>
              <div className="flex flex-wrap gap-2 mb-8">
                {MONTOS.map((m) => (
                  <button
                    key={String(m.value)}
                    type="button"
                    className={pillCls(montoMin === m.value)}
                    onClick={() => setMontoMin(m.value)}
                  >
                    {m.label}
                  </button>
                ))}
              </div>
              <div className="flex gap-3">
                <button
                  onClick={() => setStep(2)}
                  className="px-6 py-3 rounded-[60px] border border-[#3d4d45] text-[#f2f5f9] text-sm hover:bg-[#3d4d45] transition-colors"
                >
                  ← Atrás
                </button>
                <button
                  onClick={handleFinish}
                  disabled={loading || montoMin === undefined}
                  className="flex-1 rounded-[60px] bg-[#84a584] py-3 text-white font-medium disabled:opacity-40 hover:bg-[#6d8f6d] transition-colors"
                >
                  {loading ? "Configurando..." : "Activar radar →"}
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
