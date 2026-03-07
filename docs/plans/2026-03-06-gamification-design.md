# Gamification System Design
_Date: 2026-03-06_

## Overview

Full gamification layer for SICOP Health Intelligence. Grounded in dopamine psychology (Berridge), Zeigarnik Effect, IKEA Effect, and loss aversion. Every mechanic rewards behaviors aligned with the user's actual job: _find relevant bids before competitors do._

---

## Architecture Overview

```
User Action (visit /licitaciones/[id], load /notifications, complete quiz)
       │
       ▼
Server Action / Server Component
  ├─ Record activity (user_activity table)
  ├─ Evaluate badge triggers → insert into user_badges if earned
  ├─ Mark notifications read (notificaciones_leidas)
  └─ Return updated gamification state to client

Client (dashboard)
  ├─ Intel Score bar
  ├─ Vigilancia Streak counter
  ├─ Badge shelf
  └─ Notification badge on nav
```

---

## Database

All new tables. `notificaciones` table is preserved exactly as-is.

### `user_profiles`
Stores onboarding quiz answers and profile preferences.

```sql
CREATE TABLE user_profiles (
  user_id               UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  categorias            TEXT[],          -- ["MEDICAMENTO", "EQUIPAMIENTO"]
  instituciones         TEXT[],          -- ["CCSS", "Hospitales"]
  monto_min             NUMERIC,         -- NULL = no filter
  keywords              TEXT[],          -- additional user-added keywords
  onboarding_completed  BOOLEAN DEFAULT FALSE,
  created_at            TIMESTAMPTZ DEFAULT NOW(),
  updated_at            TIMESTAMPTZ DEFAULT NOW()
);

-- RLS: users can only see/edit their own profile
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
CREATE POLICY "user_profiles_self" ON user_profiles USING (auth.uid() = user_id);
```

### `notificaciones_leidas`
Per-user read state. `notificaciones` table is untouched.

```sql
CREATE TABLE notificaciones_leidas (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id         UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  notificacion_id UUID NOT NULL REFERENCES notificaciones(id) ON DELETE CASCADE,
  leido_at        TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(user_id, notificacion_id)
);

CREATE INDEX idx_nleidas_user ON notificaciones_leidas(user_id);

ALTER TABLE notificaciones_leidas ENABLE ROW LEVEL SECURITY;
CREATE POLICY "nleidas_self" ON notificaciones_leidas USING (auth.uid() = user_id);
```

### `user_activity`
One row per day per user who views a licitacion detail. Powers the Vigilancia Streak.

```sql
CREATE TABLE user_activity (
  user_id        UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  activity_date  DATE NOT NULL DEFAULT CURRENT_DATE,
  PRIMARY KEY (user_id, activity_date)
);

ALTER TABLE user_activity ENABLE ROW LEVEL SECURITY;
CREATE POLICY "activity_self" ON user_activity USING (auth.uid() = user_id);
```

### `user_badges`
Earned achievements. Badge evaluation is triggered by user actions, not a background job.

```sql
CREATE TABLE user_badges (
  user_id    UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  badge_id   TEXT NOT NULL,
  earned_at  TIMESTAMPTZ DEFAULT NOW(),
  PRIMARY KEY (user_id, badge_id)
);

ALTER TABLE user_badges ENABLE ROW LEVEL SECURITY;
CREATE POLICY "badges_self" ON user_badges USING (auth.uid() = user_id);
```

---

## Badge Catalog

| badge_id | Name | Trigger event | Condition |
|---|---|---|---|
| `first_look` | 👁️ Primera Vigilancia | View licitacion detail | First ever view |
| `streak_7` | 🔥 Semana de Vigilancia | Daily streak check | 7 consecutive days |
| `streak_30` | ⚡ Vigía Mensual | Daily streak check | 30 consecutive days |
| `fast_responder` | ⚡ Primera Respuesta | View licitacion detail | `biddoc_start_dt` < 1h ago |
| `ccss_specialist` | 🏥 Especialista CCSS | View licitacion detail | 20+ CCSS licitaciones viewed |
| `intel_pro` | 🎯 Intel Pro | Quiz / profile update | Intel Score reaches 100% |

---

## Intel Score Calculation

Computed client-side from `user_profiles` + `user_activity` + `user_badges` data. No separate DB column — derived on render.

| Condition | Points |
|---|---|
| `onboarding_completed = true` | 30 |
| `categorias.length > 0` | 20 |
| `instituciones.length > 0` | 20 |
| `monto_min IS NOT NULL` | 15 |
| Total `user_activity` rows ≥ 5 | 15 |
| **Max** | **100** |

---

## Vigilancia Streak Calculation

Computed server-side from `user_activity`. Run on dashboard load.

```typescript
// Pseudocode
const today = new Date().toISOString().split('T')[0];
const rows = await supabase
  .from('user_activity')
  .select('activity_date')
  .eq('user_id', userId)
  .order('activity_date', { ascending: false });

let streak = 0;
let checkDate = today;
for (const row of rows) {
  if (row.activity_date === checkDate) {
    streak++;
    checkDate = subtractOneDay(checkDate);
  } else break;
}
```

---

## Features by Page

### `/auth/onboarding` (new page)
- Full-screen overlay, 3-step quiz
- Step 1: Categorías (checkboxes)
- Step 2: Instituciones (multi-select pills)
- Step 3: Monto mínimo (radio pills)
- Completion → animated success state → redirect to `/dashboard`
- Triggered automatically on first login if `user_profiles.onboarding_completed = false`

### `/dashboard` (modified)
New gamification widgets added below existing stats:

1. **Intel Score bar** — `"Tu Intel Score: 65%"` with progress bar + next action hint
2. **Vigilancia Streak** — `"🔥 6 días de vigilancia"` with flame icon, loss warning at 5+ days
3. **Urgency widget** — `"⏳ 3 licitaciones cierran en 48h"` — links to filtered licitaciones
4. **Mis Logros** — badge shelf, collapsed by default. Shows earned (colored) + locked (greyed) badges. New badge earned → toast.

### `/notifications` (heavily modified)
- **Nav badge**: unread count `= total notificaciones - notificaciones_leidas` for current user
- **Empty state redesign**: "Tu radar está activo" framing with live stats
- **Unread cards**: pulsing `"nueva"` indicator. Click → marks read → badge decrements
- **New banner**: on load with unread items → `"🔔 X nuevas oportunidades detectadas"` (fades after 3s)
- Page title: "Notificaciones" (unchanged). Nav link: "Notificaciones" (unchanged).

### `/licitaciones/[id]` (modified)
- On mount: `recordActivity(userId, today)` — upsert into `user_activity`
- Evaluate and award badges: `first_look`, `fast_responder`, `ccss_specialist`
- **Urgency badge**: if `biddoc_end_dt < now + 72h` → `"🔥 Oportunidad Caliente"` badge on header
- **Countdown**: if `biddoc_end_dt < now + 24h` → `"⏳ Cierra en Xh"` in red

### `/licitaciones` list (modified)
- **Urgency badges** on cards: "🔥 Caliente" (≤72h) and "⏳ < 24h" (≤24h, red)

---

## Onboarding Quiz Flow (Existing Users)

For users who already have `user_profiles` rows (from the old alerts system, if any):
- Skip the quiz entirely — they're treated as onboarding-complete
- Show a one-time banner on dashboard: *"Actualiza tu perfil de monitoreo →"*

For users with no profile row at all:
- Quiz fires on next login

---

## Notification Badge (Nav)

The nav is a Client Component. It:
1. On mount, fetches `notificaciones` count and `notificaciones_leidas` count for current user
2. Sets up a Supabase real-time subscription on `notificaciones` inserts
3. Renders badge: red dot + number when unread > 0

```typescript
const unread = totalNotificaciones - leidasCount;
// Show badge if unread > 0
```

---

## Files Created / Modified

| File | Action |
|---|---|
| `supabase/migrations/006_gamification.sql` | Create — 4 new tables |
| `apps/web/src/app/auth/onboarding/page.tsx` | Create — quiz page |
| `apps/web/src/app/auth/onboarding/actions.ts` | Create — save profile action |
| `apps/web/src/lib/types.ts` | Modify — add UserProfile, Badge types |
| `apps/web/src/lib/gamification.ts` | Create — Intel Score + streak calculation logic |
| `apps/web/src/lib/badges.ts` | Create — badge definitions + evaluation |
| `apps/web/src/middleware.ts` | Modify — redirect to onboarding if profile incomplete |
| `apps/web/src/components/nav.tsx` | Modify — add unread badge counter |
| `apps/web/src/components/ui/intel-score.tsx` | Create — progress bar component |
| `apps/web/src/components/ui/streak-counter.tsx` | Create — streak display component |
| `apps/web/src/components/ui/badge-shelf.tsx` | Create — achievement badges component |
| `apps/web/src/components/ui/urgency-badge.tsx` | Create — "Caliente" / countdown badge |
| `apps/web/src/app/dashboard/page.tsx` | Modify — add gamification widgets |
| `apps/web/src/app/notifications/page.tsx` | Modify — unread state, new banner, empty state |
| `apps/web/src/app/notifications/actions.ts` | Modify — add markRead action |
| `apps/web/src/app/licitaciones/[id]/page.tsx` | Modify — record activity, urgency UI, badge eval |
| `apps/web/src/app/licitaciones/page.tsx` | Modify — urgency badges on cards |

---

## Out of Scope (Deferred)

- Weekly digest email (requires Resend — tackle with alert system later)
- WhatsApp notifications
- Profile editing UI beyond onboarding quiz (power user "Personalizar más" panel)
- Gamification leaderboard / social comparison
