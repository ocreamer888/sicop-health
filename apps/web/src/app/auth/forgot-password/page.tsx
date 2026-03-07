"use client";

import { useState } from "react";
import { createClient } from "@/lib/supabase/client";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    const supabase = createClient();
    const { error } = await supabase.auth.resetPasswordForEmail(email, {
      redirectTo: `${window.location.origin}/auth/reset-password`,
    });

    if (error) {
      setError(error.message);
      setLoading(false);
      return;
    }

    setSuccess(true);
    setLoading(false);
  };

  return (
    <div className="w-full max-w-sm">
      {/* Logo */}
      <div className="mb-8 text-center">
        <span className="text-3xl font-semibold text-[#f9f5df] font-[family-name:var(--font-montserrat)]">
          SICOP
        </span>
        <span className="ml-2 text-base text-[#84a584] font-[family-name:var(--font-raleway)]">
          Health Intelligence
        </span>
        <p className="mt-3 text-sm text-[var(--color-text-muted)] font-[family-name:var(--font-plus-jakarta)]">
          Recuperar acceso
        </p>
      </div>

      {/* Card */}
      <div className="rounded-[24px] bg-[#1a1f1a] p-8">
        {success ? (
          <div className="text-center">
            <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-[#84a584]/20">
              <svg
                className="h-8 w-8 text-[#84a584]"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
                />
              </svg>
            </div>
            <h2 className="mb-2 text-xl font-semibold text-[#f9f5df] font-[family-name:var(--font-montserrat)]">
              Revisa tu correo
            </h2>
            <p className="text-sm text-[var(--color-text-muted)]">
              Hemos enviado un enlace para restablecer tu contraseña a{" "}
              <strong className="text-[#f2f5f9]">{email}</strong>
            </p>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-5">
            <p className="text-sm text-[var(--color-text-muted)]">
              Ingresa tu correo electrónico y te enviaremos un enlace para
              restablecer tu contraseña.
            </p>

            <div className="space-y-2">
              <label
                htmlFor="email"
                className="block text-xs font-semibold uppercase tracking-wider text-[var(--color-text-muted)]"
              >
                Correo electrónico
              </label>
              <input
                id="email"
                type="email"
                required
                autoComplete="email"
                placeholder="tu@empresa.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full rounded-[16px] bg-[#2c3833] px-4 py-3 text-sm text-[#f2f5f9] placeholder:text-[var(--color-text-muted)] focus:outline-none focus:ring-2 focus:ring-[#84a584]"
              />
            </div>

            {error && (
              <div className="rounded-[12px] bg-[#a58484]/10 border border-[#a58484]/30 px-4 py-3">
                <p className="text-sm text-[#a58484]">{error}</p>
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-[60px] bg-[#84a584] px-6 py-3 text-sm font-semibold text-[#1a1f1a] transition-colors hover:bg-[#9ab89a] focus:outline-none focus:ring-2 focus:ring-[#84a584] focus:ring-offset-2 focus:ring-offset-[#1a1f1a] disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? "Enviando..." : "Enviar enlace"}
            </button>
          </form>
        )}
      </div>

      <p className="mt-6 text-center text-xs text-[var(--color-text-muted)]">
        ¿Recordaste tu contraseña?{" "}
        <a href="/auth/login" className="text-[#84a584] hover:underline">
          Iniciar sesión
        </a>
      </p>
    </div>
  );
}
