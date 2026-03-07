# Gamification System Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a full gamification layer to SICOP Health Intelligence — onboarding quiz, Intel Score, Vigilancia Streak, urgency UI, discovery animations, and achievement badges.

**Architecture:** 4 new Supabase tables (user_profiles, notificaciones_leidas, user_activity, user_badges) + middleware onboarding redirect + gamification logic lib + UI components layered onto existing dashboard, notifications, and licitaciones pages.

**Tech Stack:** Next.js 15 App Router, Supabase JS v2, TypeScript, Tailwind CSS, Lucide icons. No new npm packages required.

---

## Context: What Already Exists

- **Design system**: dark bg `#1a1f1a`, card `#2c3833`, accent `#84a584`, cream `#f9f5df`, `rounded-[24px]` cards, `rounded-[60px]` pills, Montserrat headings, Plus Jakarta body, text-muted via `var(--color-text-muted)`.
- **Auth**: Supabase auth, middleware at `apps/web/src/middleware.ts` (protects all routes except `/auth/*`).
- **Existing pages**: `/dashboard`, `/licitaciones`, `/licitaciones/[id]`, `/notifications`, `/auth/login`.
- **Key tables**: `licitaciones_medicas` (main data), `notificaciones` (global feed, do NOT modify), `alertas_config`, `alertas_enviadas`.
- **Server action pattern**: see `apps/web/src/app/auth/actions.ts`.
- **Supabase clients**: `@/lib/supabase/server` (server), `@/lib/supabase/client` (client components).
- **Types**: `apps/web/src/lib/types.ts`.

---

## Task 1: Database Migration

**Files:**
- Create: `supabase/migrations/006_gamification.sql`

**Step 1: Write the migration**

```sql
-- supabase/migrations/006_gamification.sql
-- Gamification tables: user_profiles, notificaciones_leidas, user_activity, user_badges

BEGIN;

-- ============================================
-- 1. user_profiles
-- ============================================
CREATE TABLE IF NOT EXISTS user_profiles (
  user_id               UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  categorias            TEXT[] DEFAULT '{}',
  instituciones         TEXT[] DEFAULT '{}',
  monto_min             NUMERIC,
  keywords              TEXT[] DEFAULT '{}',
  onboarding_completed  BOOLEAN DEFAULT FALSE,
  created_at            TIMESTAMPTZ DEFAULT NOW(),
  updated_at            TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "user_profiles_select_self" ON user_profiles
  FOR SELECT TO authenticated USING (auth.uid() = user_id);

CREATE POLICY "user_profiles_insert_self" ON user_profiles
  FOR INSERT TO authenticated WITH CHECK (auth.uid() = user_id);

CREATE POLICY "user_profiles_update_self" ON user_profiles
  FOR UPDATE TO authenticated USING (auth.uid() = user_id);

-- ============================================
-- 2. notificaciones_leidas
-- ============================================
CREATE TABLE IF NOT EXISTS notificaciones_leidas (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id         UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  notificacion_id UUID NOT NULL REFERENCES notificaciones(id) ON DELETE CASCADE,
  leido_at        TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(user_id, notificacion_id)
);

CREATE INDEX IF NOT EXISTS idx_nleidas_user ON notificaciones_leidas(user_id);
CREATE INDEX IF NOT EXISTS idx_nleidas_notif ON notificaciones_leidas(notificacion_id);

ALTER TABLE notificaciones_leidas ENABLE ROW LEVEL SECURITY;

CREATE POLICY "nleidas_self" ON notificaciones_leidas
  FOR ALL TO authenticated USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);

-- ============================================
-- 3. user_activity
-- ============================================
CREATE TABLE IF NOT EXISTS user_activity (
  user_id        UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  activity_date  DATE NOT NULL DEFAULT CURRENT_DATE,
  PRIMARY KEY (user_id, activity_date)
);

ALTER TABLE user_activity ENABLE ROW LEVEL SECURITY;

CREATE POLICY "activity_self" ON user_activity
  FOR ALL TO authenticated USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);

-- ============================================
-- 4. user_badges
-- ============================================
CREATE TABLE IF NOT EXISTS user_badges (
  user_id    UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  badge_id   TEXT NOT NULL,
  earned_at  TIMESTAMPTZ DEFAULT NOW(),
  PRIMARY KEY (user_id, badge_id)
);

ALTER TABLE user_badges ENABLE ROW LEVEL SECURITY;

CREATE POLICY "badges_self" ON user_badges
  FOR ALL TO authenticated USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);

COMMIT;
```

**Step 2: Deploy to Supabase**

```bash
# From repo root
supabase db push
```

Expected output: migration applied successfully, 4 new tables created.

**Step 3: Verify in Supabase Dashboard**

Open Table Editor and confirm: `user_profiles`, `notificaciones_leidas`, `user_activity`, `user_badges` all exist.

**Step 4: Commit**

```bash
git add supabase/migrations/006_gamification.sql
git commit -m "feat(gamification): add DB migration — 4 new tables"
```

---

## Task 2: Types + Gamification Logic Library

**Files:**
- Modify: `apps/web/src/lib/types.ts`
- Create: `apps/web/src/lib/gamification.ts`
- Create: `apps/web/src/lib/badges.ts`

**Step 1: Add types to `types.ts`**

Append to `apps/web/src/lib/types.ts`:

```typescript
// ─────────────────────────────────────────────
// GAMIFICATION
// ─────────────────────────────────────────────

export interface UserProfile {
  user_id: string
  categorias: string[]
  instituciones: string[]
  monto_min: number | null
  keywords: string[]
  onboarding_completed: boolean
  created_at: string
  updated_at: string
}

export interface BadgeDefinition {
  id: string
  name: string
  description: string
  icon: string
}

export interface UserBadge {
  user_id: string
  badge_id: string
  earned_at: string
}

export interface GamificationState {
  intelScore: number          // 0–100
  streak: number              // days
  unreadCount: number
  earnedBadgeIds: string[]
  profile: UserProfile | null
}
```

**Step 2: Create `apps/web/src/lib/gamification.ts`**

```typescript
import type { UserProfile } from "./types";

export function calcIntelScore(
  profile: UserProfile | null,
  activityCount: number,
): number {
  if (!profile) return 0;
  let score = 0;
  if (profile.onboarding_completed)       score += 30;
  if (profile.categorias.length > 0)      score += 20;
  if (profile.instituciones.length > 0)   score += 20;
  if (profile.monto_min !== null)         score += 15;
  if (activityCount >= 5)                 score += 15;
  return Math.min(score, 100);
}

export function calcStreak(activityDates: string[]): number {
  if (activityDates.length === 0) return 0;

  // activityDates: sorted DESC, format "YYYY-MM-DD"
  const sorted = [...activityDates].sort().reverse();
  const today = new Date().toISOString().split("T")[0];
  const yesterday = new Date(Date.now() - 86_400_000).toISOString().split("T")[0];

  // Streak must include today or yesterday to be "active"
  if (sorted[0] !== today && sorted[0] !== yesterday) return 0;

  let streak = 1;
  for (let i = 1; i < sorted.length; i++) {
    const expected = subtractDays(sorted[i - 1], 1);
    if (sorted[i] === expected) {
      streak++;
    } else {
      break;
    }
  }
  return streak;
}

function subtractDays(dateStr: string, days: number): string {
  const d = new Date(dateStr);
  d.setDate(d.getDate() - days);
  return d.toISOString().split("T")[0];
}

export function getIntelScoreNextAction(
  profile: UserProfile | null,
  activityCount: number,
): string | null {
  if (!profile || !profile.onboarding_completed) return "Completa tu perfil de monitoreo";
  if (profile.categorias.length === 0) return "Agrega las categorías que te interesan";
  if (profile.instituciones.length === 0) return "Selecciona las instituciones objetivo";
  if (profile.monto_min === null) return "Define el monto mínimo de oportunidades";
  if (activityCount < 5) return `Revisa ${5 - activityCount} licitaciones más para completar tu Intel Score`;
  return null;
}

export function getUrgencyLevel(biddocEndDt: string | null): "hot" | "urgent" | null {
  if (!biddocEndDt) return null;
  const ms = new Date(biddocEndDt).getTime() - Date.now();
  const hours = ms / 3_600_000;
  if (hours <= 0) return null;
  if (hours <= 24) return "urgent";
  if (hours <= 72) return "hot";
  return null;
}

export function hoursUntil(dt: string): number {
  return Math.max(0, (new Date(dt).getTime() - Date.now()) / 3_600_000);
}
```

**Step 3: Create `apps/web/src/lib/badges.ts`**

```typescript
import type { BadgeDefinition } from "./types";

export const BADGE_DEFINITIONS: BadgeDefinition[] = [
  {
    id: "first_look",
    name: "Primera Vigilancia",
    icon: "👁️",
    description: "Abriste tu primera licitación",
  },
  {
    id: "streak_7",
    name: "Semana de Vigilancia",
    icon: "🔥",
    description: "7 días consecutivos monitoreando",
  },
  {
    id: "streak_30",
    name: "Vigía Mensual",
    icon: "⚡",
    description: "30 días consecutivos de monitoreo",
  },
  {
    id: "fast_responder",
    name: "Primera Respuesta",
    icon: "⚡",
    description: "Abriste un bid dentro de 1h de su publicación",
  },
  {
    id: "ccss_specialist",
    name: "Especialista CCSS",
    icon: "🏥",
    description: "Revisaste 20+ licitaciones de la CCSS",
  },
  {
    id: "intel_pro",
    name: "Intel Pro",
    icon: "🎯",
    description: "Perfil de monitoreo 100% optimizado",
  },
];

export function getBadge(id: string): BadgeDefinition | undefined {
  return BADGE_DEFINITIONS.find((b) => b.id === id);
}
```

**Step 4: Commit**

```bash
git add apps/web/src/lib/types.ts apps/web/src/lib/gamification.ts apps/web/src/lib/badges.ts
git commit -m "feat(gamification): add types, Intel Score calc, streak calc, badge definitions"
```

---

## Task 3: Onboarding Quiz

**Files:**
- Create: `apps/web/src/app/auth/onboarding/page.tsx`
- Create: `apps/web/src/app/auth/onboarding/actions.ts`

**Step 1: Create `actions.ts`**

```typescript
"use server";

import { createClient } from "@/lib/supabase/server";
import { redirect } from "next/navigation";

export async function completeOnboarding(formData: {
  categorias: string[];
  instituciones: string[];
  monto_min: number | null;
}) {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) redirect("/auth/login");

  await supabase.from("user_profiles").upsert({
    user_id: user.id,
    categorias: formData.categorias,
    instituciones: formData.instituciones,
    monto_min: formData.monto_min,
    keywords: [],
    onboarding_completed: true,
    updated_at: new Date().toISOString(),
  });

  redirect("/dashboard");
}
```

**Step 2: Create `page.tsx`**

```tsx
"use client";

import { useState } from "react";
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
  const [step, setStep] = useState(1);
  const [categorias, setCategorias] = useState<string[]>([]);
  const [instituciones, setInstituciones] = useState<string[]>([]);
  const [montoMin, setMontoMin] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [done, setDone] = useState(false);

  function toggleItem(value: string, list: string[], setList: (v: string[]) => void) {
    setList(list.includes(value) ? list.filter((v) => v !== value) : [...list, value]);
  }

  async function handleFinish() {
    setLoading(true);
    setDone(true);
    setTimeout(async () => {
      await completeOnboarding({ categorias, instituciones, monto_min: montoMin });
    }, 1500);
  }

  const pillCls = (selected: boolean) =>
    `px-5 py-2.5 rounded-[60px] border text-sm font-medium transition-all cursor-pointer ${
      selected
        ? "bg-[#84a584] border-[#84a584] text-white"
        : "border-[#3d4d45] text-[#f2f5f9] hover:border-[#84a584]/50"
    }`;

  if (done) {
    return (
      <div className="min-h-screen bg-[#1a1f1a] flex items-center justify-center">
        <div className="text-center">
          <div className="text-5xl mb-4">✅</div>
          <h2 className="text-2xl font-bold text-[#f9f5df] font-[family-name:var(--font-montserrat)]">
            Tu radar está listo
          </h2>
          <p className="text-[var(--color-text-muted)] mt-2 font-[family-name:var(--font-plus-jakarta)]">
            Redirigiendo al dashboard...
          </p>
        </div>
      </div>
    );
  }

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
```

**Step 3: Commit**

```bash
git add apps/web/src/app/auth/onboarding/
git commit -m "feat(gamification): add onboarding quiz (3-step profile setup)"
```

---

## Task 4: Middleware — Redirect to Onboarding

**Files:**
- Modify: `apps/web/src/middleware.ts`

**Step 1: Read the current middleware first**

Read `apps/web/src/middleware.ts` before editing to understand current logic.

**Step 2: Add onboarding check**

After the existing auth check (user is authenticated), add:

```typescript
// If authenticated and NOT on onboarding page, check if onboarding is needed
if (user && !request.nextUrl.pathname.startsWith('/auth/onboarding')) {
  // Check user_profiles — if no row or onboarding_completed = false, redirect
  const supabase = createServerClient(/* existing args */);
  const { data: profile } = await supabase
    .from('user_profiles')
    .select('onboarding_completed')
    .eq('user_id', user.id)
    .single();

  if (!profile || !profile.onboarding_completed) {
    return NextResponse.redirect(new URL('/auth/onboarding', request.url));
  }
}
```

**IMPORTANT:** Place this check AFTER the existing auth redirect (unauthenticated users → login). Do not change any existing logic — only append.

**Step 3: Commit**

```bash
git add apps/web/src/middleware.ts
git commit -m "feat(gamification): redirect to onboarding if profile incomplete"
```

---

## Task 5: UI Components — Intel Score, Streak, Urgency Badge

**Files:**
- Create: `apps/web/src/components/ui/intel-score.tsx`
- Create: `apps/web/src/components/ui/streak-counter.tsx`
- Create: `apps/web/src/components/ui/urgency-badge.tsx`

**Step 1: `intel-score.tsx`**

```tsx
interface IntelScoreProps {
  score: number;       // 0–100
  nextAction?: string | null;
}

export function IntelScore({ score, nextAction }: IntelScoreProps) {
  const color = score >= 80 ? "#84a584" : score >= 50 ? "#b5a88a" : "#5d6a85";

  return (
    <div className="rounded-[24px] bg-[#2c3833] border border-[#3d4d45] p-5">
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs font-medium text-[var(--color-text-muted)] uppercase tracking-wide">
          Intel Score
        </span>
        <span className="text-lg font-bold font-[family-name:var(--font-montserrat)]" style={{ color }}>
          {score}%
        </span>
      </div>
      {/* Progress bar */}
      <div className="h-2 rounded-full bg-[#1a1f1a] overflow-hidden mb-3">
        <div
          className="h-full rounded-full transition-all duration-700"
          style={{ width: `${score}%`, backgroundColor: color }}
        />
      </div>
      {nextAction && (
        <p className="text-xs text-[#5a6a62] font-[family-name:var(--font-plus-jakarta)]">
          → {nextAction}
        </p>
      )}
      {score === 100 && (
        <p className="text-xs text-[#84a584] font-medium font-[family-name:var(--font-plus-jakarta)]">
          🎯 Perfil completamente optimizado
        </p>
      )}
    </div>
  );
}
```

**Step 2: `streak-counter.tsx`**

```tsx
interface StreakCounterProps {
  streak: number;
}

export function StreakCounter({ streak }: StreakCounterProps) {
  const showWarning = streak >= 5;

  return (
    <div className="rounded-[24px] bg-[#2c3833] border border-[#3d4d45] p-5">
      <div className="flex items-center gap-3">
        <span className="text-3xl">{streak >= 7 ? "🔥" : streak >= 3 ? "⚡" : "👁️"}</span>
        <div>
          <p className="text-xs text-[var(--color-text-muted)] uppercase tracking-wide mb-0.5">
            Vigilancia consecutiva
          </p>
          <p className="text-xl font-bold text-[#f9f5df] font-[family-name:var(--font-montserrat)]">
            {streak} {streak === 1 ? "día" : "días"}
          </p>
        </div>
      </div>
      {showWarning && streak < 7 && (
        <p className="text-xs text-[#b5a88a] mt-3 font-[family-name:var(--font-plus-jakarta)]">
          ¡Regresa mañana para no perder tu racha!
        </p>
      )}
      {streak >= 7 && (
        <p className="text-xs text-[#84a584] mt-3 font-[family-name:var(--font-plus-jakarta)]">
          🏆 Semana de vigilancia completada
        </p>
      )}
    </div>
  );
}
```

**Step 3: `urgency-badge.tsx`**

```tsx
import { hoursUntil } from "@/lib/gamification";

interface UrgencyBadgeProps {
  biddocEndDt: string | null;
}

export function UrgencyBadge({ biddocEndDt }: UrgencyBadgeProps) {
  if (!biddocEndDt) return null;
  const hours = hoursUntil(biddocEndDt);
  if (hours <= 0 || hours > 72) return null;

  if (hours <= 24) {
    return (
      <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-[60px] bg-[#a58484]/20 text-[#e09090] text-xs font-medium">
        ⏳ Cierra en {Math.round(hours)}h
      </span>
    );
  }

  return (
    <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-[60px] bg-[#84a584]/15 text-[#84a584] text-xs font-medium">
      🔥 Oportunidad Caliente
    </span>
  );
}
```

**Step 4: Commit**

```bash
git add apps/web/src/components/ui/intel-score.tsx apps/web/src/components/ui/streak-counter.tsx apps/web/src/components/ui/urgency-badge.tsx
git commit -m "feat(gamification): add IntelScore, StreakCounter, UrgencyBadge components"
```

---

## Task 6: Badge Shelf Component

**Files:**
- Create: `apps/web/src/components/ui/badge-shelf.tsx`

**Step 1: Create the component**

```tsx
"use client";

import { useState } from "react";
import { ChevronDown, ChevronUp } from "lucide-react";
import { BADGE_DEFINITIONS } from "@/lib/badges";

interface BadgeShelfProps {
  earnedBadgeIds: string[];
  newBadgeId?: string | null;
}

export function BadgeShelf({ earnedBadgeIds, newBadgeId }: BadgeShelfProps) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="rounded-[24px] bg-[#2c3833] border border-[#3d4d45] p-5">
      <button
        className="w-full flex items-center justify-between"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex items-center gap-2">
          <span className="text-sm font-semibold text-[#f9f5df] font-[family-name:var(--font-montserrat)]">
            Mis Logros
          </span>
          <span className="text-xs px-2 py-0.5 rounded-[60px] bg-[#84a584]/20 text-[#84a584]">
            {earnedBadgeIds.length}/{BADGE_DEFINITIONS.length}
          </span>
        </div>
        {expanded ? <ChevronUp size={16} className="text-[#5a6a62]" /> : <ChevronDown size={16} className="text-[#5a6a62]" />}
      </button>

      {expanded && (
        <div className="mt-4 grid grid-cols-2 sm:grid-cols-3 gap-3">
          {BADGE_DEFINITIONS.map((badge) => {
            const earned = earnedBadgeIds.includes(badge.id);
            const isNew = badge.id === newBadgeId;
            return (
              <div
                key={badge.id}
                className={`rounded-[16px] p-3 text-center transition-all ${
                  earned
                    ? isNew
                      ? "bg-[#84a584]/20 border border-[#84a584]/50 animate-pulse"
                      : "bg-[#1a1f1a] border border-[#3d4d45]"
                    : "bg-[#1a1f1a]/50 border border-[#2c3833] opacity-40"
                }`}
              >
                <div className="text-2xl mb-1">{badge.icon}</div>
                <p className="text-xs font-medium text-[#f9f5df] font-[family-name:var(--font-montserrat)] leading-tight">
                  {badge.name}
                </p>
                {earned && (
                  <p className="text-[10px] text-[#5a6a62] mt-0.5 font-[family-name:var(--font-plus-jakarta)]">
                    {badge.description}
                  </p>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
```

**Step 2: Commit**

```bash
git add apps/web/src/components/ui/badge-shelf.tsx
git commit -m "feat(gamification): add BadgeShelf component"
```

---

## Task 7: Nav — Unread Badge Counter

**Files:**
- Modify: `apps/web/src/components/nav.tsx`

**Step 1: Read current nav**

Read `apps/web/src/components/nav.tsx` before editing.

**Step 2: Add notification link with live unread badge**

The nav is `"use client"`. Add unread count state that fetches on mount via Supabase client.

Add to `navItems`:
```typescript
import { Home, Table2, Bell, LogOut } from "lucide-react";

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: Home },
  { href: "/licitaciones", label: "Licitaciones", icon: Table2 },
  { href: "/notifications", label: "Notificaciones", icon: Bell },
];
```

Add unread count state inside the `Nav` component (after imports and navItems):

```typescript
const [unread, setUnread] = useState(0);

useEffect(() => {
  async function fetchUnread() {
    const supabase = createClient(); // from @/lib/supabase/client
    const { data: { user } } = await supabase.auth.getUser();
    if (!user) return;

    const [{ count: total }, { count: read }] = await Promise.all([
      supabase.from("notificaciones").select("*", { count: "exact", head: true }),
      supabase.from("notificaciones_leidas").select("*", { count: "exact", head: true }).eq("user_id", user.id),
    ]);

    setUnread(Math.max(0, (total ?? 0) - (read ?? 0)));
  }
  fetchUnread();
}, []);
```

In the nav item render, for the Notificaciones link, add the badge:

```tsx
{item.href === "/notifications" && unread > 0 && (
  <span className="absolute -top-1 -right-1 w-4 h-4 rounded-full bg-[#84a584] text-white text-[10px] flex items-center justify-center font-bold">
    {unread > 9 ? "9+" : unread}
  </span>
)}
```

Wrap the Link in `relative` for badge positioning.

**Step 3: Commit**

```bash
git add apps/web/src/components/nav.tsx
git commit -m "feat(gamification): add unread notification badge to nav"
```

---

## Task 8: Dashboard — Add Gamification Widgets

**Files:**
- Modify: `apps/web/src/app/dashboard/page.tsx`

**Step 1: Read current dashboard**

Read `apps/web/src/app/dashboard/page.tsx` before editing.

**Step 2: Add gamification data fetching to `getDashboardData`**

Add to the existing server function:

```typescript
// Gamification data
const { data: profile } = await supabase
  .from("user_profiles")
  .select("*")
  .eq("user_id", user.id)
  .single();

const { data: activityRows } = await supabase
  .from("user_activity")
  .select("activity_date")
  .eq("user_id", user.id)
  .order("activity_date", { ascending: false });

const { data: badgeRows } = await supabase
  .from("user_badges")
  .select("badge_id")
  .eq("user_id", user.id);

// Urgency: tenders closing in next 48h
const now = new Date().toISOString();
const in48h = new Date(Date.now() + 48 * 3_600_000).toISOString();
const { count: urgentCount } = await supabase
  .from("licitaciones_medicas")
  .select("*", { count: "exact", head: true })
  .eq("es_medica", true)
  .gte("biddoc_end_dt", now)
  .lte("biddoc_end_dt", in48h);
```

**Step 3: Import and render gamification widgets**

Add these imports:
```typescript
import { IntelScore } from "@/components/ui/intel-score";
import { StreakCounter } from "@/components/ui/streak-counter";
import { BadgeShelf } from "@/components/ui/badge-shelf";
import { calcIntelScore, calcStreak, getIntelScoreNextAction } from "@/lib/gamification";
import Link from "next/link";
import { Clock } from "lucide-react";
```

Add a gamification row below the existing stats in the JSX:

```tsx
{/* Gamification widgets */}
<div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mt-6">
  <IntelScore
    score={calcIntelScore(profile, activityRows?.length ?? 0)}
    nextAction={getIntelScoreNextAction(profile, activityRows?.length ?? 0)}
  />
  <StreakCounter streak={calcStreak(activityRows?.map(r => r.activity_date) ?? [])} />
  {(urgentCount ?? 0) > 0 && (
    <Link href="/licitaciones?urgente=true">
      <div className="rounded-[24px] bg-[#2c3833] border border-[#3d4d45] p-5 hover:border-[#84a584]/50 transition-all cursor-pointer">
        <div className="flex items-center gap-2 mb-1">
          <Clock size={16} className="text-[#b5a88a]" />
          <span className="text-xs font-medium text-[var(--color-text-muted)] uppercase tracking-wide">Urgente</span>
        </div>
        <p className="text-xl font-bold text-[#f9f5df] font-[family-name:var(--font-montserrat)]">
          ⏳ {urgentCount}
        </p>
        <p className="text-xs text-[#5a6a62] mt-1 font-[family-name:var(--font-plus-jakarta)]">
          licitaciones cierran en 48h
        </p>
      </div>
    </Link>
  )}
</div>

{/* Badge shelf */}
<div className="mt-4">
  <BadgeShelf earnedBadgeIds={badgeRows?.map(b => b.badge_id) ?? []} />
</div>
```

**Step 4: Commit**

```bash
git add apps/web/src/app/dashboard/page.tsx
git commit -m "feat(gamification): add Intel Score, streak, urgency, badges to dashboard"
```

---

## Task 9: Licitacion Detail — Record Activity + Urgency UI + Badge Evaluation

**Files:**
- Modify: `apps/web/src/app/licitaciones/[id]/page.tsx`
- Create: `apps/web/src/app/licitaciones/[id]/record-activity.ts`

**Step 1: Create `record-activity.ts` (server action)**

```typescript
"use server";

import { createClient } from "@/lib/supabase/server";
import { calcStreak } from "@/lib/gamification";

const BADGE_CHECKS = [
  "first_look",
  "fast_responder",
  "ccss_specialist",
  "streak_7",
  "streak_30",
  "intel_pro",
] as const;

export async function recordLicitacionView(instcartelno: string, instCode: string | null, biddocStartDt: string | null) {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return null;

  const today = new Date().toISOString().split("T")[0];

  // 1. Record activity (upsert — ignore duplicate)
  await supabase.from("user_activity").upsert(
    { user_id: user.id, activity_date: today },
    { onConflict: "user_id,activity_date" }
  );

  // 2. Fetch data needed for badge evaluation
  const [
    { data: existingBadges },
    { data: activityRows },
    { count: totalViews },
    { count: ccssViews },
    { data: profile },
  ] = await Promise.all([
    supabase.from("user_badges").select("badge_id").eq("user_id", user.id),
    supabase.from("user_activity").select("activity_date").eq("user_id", user.id).order("activity_date", { ascending: false }),
    supabase.from("user_activity").select("*", { count: "exact", head: true }).eq("user_id", user.id),
    supabase.from("user_activity").select("*", { count: "exact", head: true }).eq("user_id", user.id), // simplified
    supabase.from("user_profiles").select("*").eq("user_id", user.id).single(),
  ]);

  const earnedIds = new Set(existingBadges?.map(b => b.badge_id) ?? []);
  const newBadges: string[] = [];

  // first_look
  if (!earnedIds.has("first_look") && (totalViews ?? 0) >= 1) {
    newBadges.push("first_look");
  }

  // fast_responder: licitacion published < 1h ago
  if (!earnedIds.has("fast_responder") && biddocStartDt) {
    const age = (Date.now() - new Date(biddocStartDt).getTime()) / 3_600_000;
    if (age <= 1) newBadges.push("fast_responder");
  }

  // streak_7 and streak_30
  const streak = calcStreak(activityRows?.map(r => r.activity_date) ?? []);
  if (!earnedIds.has("streak_7") && streak >= 7) newBadges.push("streak_7");
  if (!earnedIds.has("streak_30") && streak >= 30) newBadges.push("streak_30");

  // intel_pro: check if score is 100
  if (!earnedIds.has("intel_pro") && profile) {
    const { calcIntelScore } = await import("@/lib/gamification");
    const score = calcIntelScore(profile, totalViews ?? 0);
    if (score >= 100) newBadges.push("intel_pro");
  }

  // Insert new badges
  if (newBadges.length > 0) {
    await supabase.from("user_badges").insert(
      newBadges.map(badge_id => ({ user_id: user.id, badge_id }))
    );
  }

  return newBadges[0] ?? null; // return first new badge for toast display
}
```

**Step 2: Modify licitacion detail page**

Read `apps/web/src/app/licitaciones/[id]/page.tsx` before editing.

Add `UrgencyBadge` import:
```typescript
import { UrgencyBadge } from "@/components/ui/urgency-badge";
```

Near the top of the detail page component, add a Client Component wrapper that calls `recordLicitacionView` on mount. The simplest approach: add a `<ActivityRecorder>` client component that fires the server action.

Create `apps/web/src/app/licitaciones/[id]/activity-recorder.tsx`:

```tsx
"use client";

import { useEffect } from "react";
import { recordLicitacionView } from "./record-activity";

export function ActivityRecorder({
  instcartelno,
  instCode,
  biddocStartDt,
}: {
  instcartelno: string;
  instCode: string | null;
  biddocStartDt: string | null;
}) {
  useEffect(() => {
    recordLicitacionView(instcartelno, instCode, biddocStartDt);
  }, [instcartelno, instCode, biddocStartDt]);

  return null;
}
```

In the page, include `<ActivityRecorder>` and `<UrgencyBadge>` near the tender title.

**Step 3: Commit**

```bash
git add apps/web/src/app/licitaciones/[id]/
git commit -m "feat(gamification): record activity, evaluate badges, urgency UI on licitacion detail"
```

---

## Task 10: Notifications Page — Unread State + Redesigned Empty State

**Files:**
- Modify: `apps/web/src/app/notifications/page.tsx`
- Modify: `apps/web/src/app/notifications/actions.ts`
- Modify: `apps/web/src/app/notifications/notificacion-card.tsx`

**Step 1: Update `actions.ts`**

Read the file before editing. Add:

```typescript
export async function markNotificacionRead(notificacionId: string) {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return;

  await supabase.from("notificaciones_leidas").upsert(
    { user_id: user.id, notificacion_id: notificacionId },
    { onConflict: "user_id,notificacion_id" }
  );
}

export async function getReadIds(): Promise<string[]> {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return [];

  const { data } = await supabase
    .from("notificaciones_leidas")
    .select("notificacion_id")
    .eq("user_id", user.id);

  return data?.map(r => r.notificacion_id) ?? [];
}
```

**Step 2: Update `page.tsx`**

Replace the dead empty state with the active radar framing:

```tsx
// Empty state:
<div className="rounded-[24px] bg-[#2c3833] border border-[#3d4d45] p-12 text-center">
  <div className="text-4xl mb-4">🎯</div>
  <p className="text-[#f9f5df] font-semibold mb-1 font-[family-name:var(--font-montserrat)]">
    Tu radar está activo
  </p>
  <p className="text-[var(--color-text-muted)] text-sm mb-4 font-[family-name:var(--font-plus-jakarta)]">
    Monitoreando todas las licitaciones médicas de SICOP
  </p>
  <p className="text-xs text-[#5a6a62]">
    Las nuevas oportunidades aparecerán aquí en cuanto sean publicadas.
  </p>
</div>
```

Add unread detection: on load, fetch `readIds`. Pass to cards. Show `"🔔 X nuevas oportunidades"` banner if unread > 0.

**Step 3: Update `notificacion-card.tsx`**

Add `isUnread` prop. If true: show pulsing green dot + `"nueva"` label. On click of the card → call `markNotificacionRead`.

```tsx
// Add to props:
isUnread?: boolean;
onRead?: () => void;

// In JSX, add unread indicator:
{isUnread && (
  <span className="flex items-center gap-1 text-xs text-[#84a584] font-medium animate-pulse">
    <span className="w-1.5 h-1.5 rounded-full bg-[#84a584]" />
    nueva
  </span>
)}
```

**Step 4: Commit**

```bash
git add apps/web/src/app/notifications/
git commit -m "feat(gamification): unread state, active empty state, mark-read on notifications"
```

---

## Task 11: Licitaciones List — Urgency Badges on Cards

**Files:**
- Modify: `apps/web/src/app/licitaciones/page.tsx`

**Step 1: Read the file first**

Read `apps/web/src/app/licitaciones/page.tsx`.

**Step 2: Add UrgencyBadge to each licitacion row/card**

Import `UrgencyBadge` and add it alongside the existing `estado` badge where `biddoc_end_dt` is displayed.

```tsx
import { UrgencyBadge } from "@/components/ui/urgency-badge";

// In the card/row render:
<UrgencyBadge biddocEndDt={licitacion.biddoc_end_dt} />
```

**Step 3: Commit**

```bash
git add apps/web/src/app/licitaciones/page.tsx
git commit -m "feat(gamification): add urgency badges to licitaciones list"
```

---

## Task 12: End-to-End Verification

**Step 1: Test onboarding flow**

1. Open app in incognito (fresh session)
2. Log in
3. Should redirect to `/auth/onboarding`
4. Complete all 3 steps
5. Should see success animation → redirect to `/dashboard`
6. Verify row exists in `user_profiles` in Supabase Dashboard

**Step 2: Test Intel Score**

On dashboard: verify score shows 30% after onboarding (completed but no other criteria met).

**Step 3: Test streak**

Visit any `/licitaciones/[id]` page.
Check `user_activity` table — row for today should exist.
Dashboard streak counter should show 1.

**Step 4: Test badge award**

Visit a licitacion detail for the first time.
Check `user_badges` table — `first_look` badge should be inserted.
Dashboard badge shelf should show it as earned.

**Step 5: Test urgency badge**

In Supabase: find or insert a licitacion with `biddoc_end_dt` within 48h.
Verify "🔥 Oportunidad Caliente" badge appears on the list and detail page.

**Step 6: Test unread notifications**

- Check `/notifications` — unread count should be visible
- Click a notification card → should mark as read
- Nav badge should decrement

---

## Summary of All Files

| File | Action |
|---|---|
| `supabase/migrations/006_gamification.sql` | Create |
| `apps/web/src/lib/types.ts` | Modify |
| `apps/web/src/lib/gamification.ts` | Create |
| `apps/web/src/lib/badges.ts` | Create |
| `apps/web/src/app/auth/onboarding/page.tsx` | Create |
| `apps/web/src/app/auth/onboarding/actions.ts` | Create |
| `apps/web/src/middleware.ts` | Modify |
| `apps/web/src/components/ui/intel-score.tsx` | Create |
| `apps/web/src/components/ui/streak-counter.tsx` | Create |
| `apps/web/src/components/ui/urgency-badge.tsx` | Create |
| `apps/web/src/components/ui/badge-shelf.tsx` | Create |
| `apps/web/src/components/nav.tsx` | Modify |
| `apps/web/src/app/dashboard/page.tsx` | Modify |
| `apps/web/src/app/licitaciones/[id]/page.tsx` | Modify |
| `apps/web/src/app/licitaciones/[id]/record-activity.ts` | Create |
| `apps/web/src/app/licitaciones/[id]/activity-recorder.tsx` | Create |
| `apps/web/src/app/licitaciones/page.tsx` | Modify |
| `apps/web/src/app/notifications/page.tsx` | Modify |
| `apps/web/src/app/notifications/actions.ts` | Modify |
| `apps/web/src/app/notifications/notificacion-card.tsx` | Modify |
