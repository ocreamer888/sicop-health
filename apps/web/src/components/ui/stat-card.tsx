"use client";

import { cn } from "@/lib/utils";

interface StatCardProps {
  title: string;
  value: string | number;
  description?: string;
  trend?: {
    value: number;
    isPositive: boolean;
  };
  icon?: React.ReactNode;
  variant?: "default" | "sage" | "dark";
  className?: string;
}

const variantStyles = {
  default: "bg-[#2c3833]",
  sage: "bg-[#84a584] text-[#1c1a1f]",
  dark: "bg-[#1a1f1a]",
};

export function StatCard({
  title,
  value,
  description,
  trend,
  icon,
  variant = "default",
  className,
}: StatCardProps) {
  return (
    <div
      className={cn(
        "rounded-[24px] p-6 transition-all duration-200 hover:scale-[1.02]",
        variantStyles[variant],
        className
      )}
    >
      <div className="flex items-start justify-between">
        <div>
          <h3 className="text-sm font-medium text-[#e4e4e4] font-[family-name:var(--font-plus-jakarta)]">
            {title}
          </h3>
          <p className="mt-2 text-4xl font-semibold text-[var(--color-text-cream)] font-[family-name:var(--font-montserrat)]">
            {value}
          </p>
          {description && (
            <p className="mt-1 text-sm text-[#e4e4e4] font-[family-name:var(--font-plus-jakarta)]">
              {description}
            </p>
          )}
          {trend && (
            <div className="mt-2 flex items-center gap-1">
              <span
                className={cn(
                  "text-sm font-medium",
                  trend.isPositive ? "text-[#84a584]" : "text-red-400"
                )}
              >
                {trend.isPositive ? "+" : "-"}{trend.value}%
              </span>
              <span className="text-sm text-[var(--color-text-muted)]">vs mes anterior</span>
            </div>
          )}
        </div>
        {icon && (
          <div className="flex h-12 w-12 items-center justify-center rounded-[16px] bg-[#1a1f1a]/50 text-[#f9f5df]">
            {icon}
          </div>
        )}
      </div>
    </div>
  );
}
