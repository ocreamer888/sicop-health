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
