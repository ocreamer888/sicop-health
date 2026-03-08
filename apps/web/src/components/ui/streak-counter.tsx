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
