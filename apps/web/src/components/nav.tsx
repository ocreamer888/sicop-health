"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Home, Table2, Activity, LogOut } from "lucide-react";
import { signOut } from "@/app/auth/actions";

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: Home },
  { href: "/licitaciones", label: "Licitaciones", icon: Table2 },
];

export function Nav() {
  const pathname = usePathname();
  if (pathname.startsWith("/auth")) return null;

  return (
    <nav className="relative top-0 z-50 w-full px-6 py-4">
      <div className="mx-auto flex max-w-[1393px] items-center justify-between">
        {/* Logo */}
        <Link href="/dashboard" className="flex items-center gap-2">
          <span className="text-2xl font-semibold text-[#f9f5df] font-[family-name:var(--font-montserrat)]">
            SICOP
          </span>
          <span className="text-sm text-[#84a584] font-[family-name:var(--font-raleway)]">
            Health  Intelligence
          </span>
        </Link>

        {/* Navigation Pills - Figma style */}
        <div className="flex items-center gap-1 rounded-[156px] border border-[#cecece] px-2 py-2">
          {navItems.map((item) => {
            const isActive = pathname.startsWith(item.href);
            const Icon = item.icon;

            return (
              <Link
                key={item.href}
                href={item.href}
                className={`
                  flex items-center gap-2 px-5 py-2.5 text-sm font-medium transition-all duration-200
                  ${isActive
                    ? "bg-[#898a7d] text-white rounded-[108px]"
                    : "text-[#f9f5df] rounded-[22px] hover:bg-white/5"
                  }
                `}
              >
                <Icon size={18} />
                <span className="font-[family-name:var(--font-plus-jakarta)]">
                  {item.label}
                </span>
              </Link>
            );
          })}
        </div>

        {/* Right actions */}
        <div className="flex items-center gap-2">
          <button className="flex items-center gap-2 rounded-[37px] border border-[#898a7d] bg-[#1a1f1a] px-6 py-3 text-sm text-white transition-colors hover:bg-[#2c3833]">
            <Activity size={18} />
            <span className="font-[family-name:var(--font-plus-jakarta)]">
              Live Data
            </span>
          </button>
          <form action={signOut}>
            <button
              type="submit"
              className="flex items-center gap-2 rounded-[37px] border border-[#898a7d]/40 bg-transparent px-4 py-3 text-sm text-[var(--color-text-muted)] transition-colors hover:bg-[#2c3833] hover:text-[#f2f5f9]"
              title="Cerrar sesión"
            >
              <LogOut size={18} />
            </button>
          </form>
        </div>
      </div>
    </nav>
  );
}
