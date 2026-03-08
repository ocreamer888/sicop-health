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
