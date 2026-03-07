"use client";

import { useEffect, useState } from "react";
import { createClient } from "@/lib/supabase/client";
import { useRouter } from "next/navigation";

export default function ResetPasswordPage() {
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const router = useRouter();

  useEffect(() => {
    // Check if we have the recovery token in the URL hash
    const hash = window.location.hash.substring(1);
    const params = new URLSearchParams(hash);
    const access_token = params.get("access_token");
    const refresh_token = params.get("refresh_token");
    const type = params.get("type");

    if (!access_token || type !== "recovery") {
      setError("Enlace de restablecimiento inválido o expirado.");
      return;
    }

    // Set the session from the recovery token
    const supabase = createClient();
    supabase.auth
      .setSession({ access_token, refresh_token: refresh_token || "" })
      .then(({ error }) => {
        if (error) {
          setError("El enlace ha expirado. Solicita un nuevo restablecimiento.");
        }
      });
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    if (password !== confirmPassword) {
      setError("Las contraseñas no coinciden.");
      setLoading(false);
      return;
    }

    if (password.length < 6) {
      setError("La contraseña debe tener al menos 6 caracteres.");
      setLoading(false);
      return;
    }

    const supabase = createClient();
    const { error } = await supabase.auth.updateUser({ password });

    if (error) {
      setError(error.message);
      setLoading(false);
      return;
    }

    setSuccess(true);
    setTimeout(() => {
      router.push("/auth/login?message=" + encodeURIComponent("Contraseña actualizada exitosamente"));
    }, 2000);
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
          Restablecer contraseña
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
                  d="M5 13l4 4L19 7"
                />
              </svg>
            </div>
            <h2 className="mb-2 text-xl font-semibold text-[#f9f5df] font-[family-name:var(--font-montserrat)]">
              ¡Contraseña actualizada!
            </h2>
            <p className="text-sm text-[var(--color-text-muted)]">
              Redirigiendo al inicio de sesión...
            </p>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-5">
            <div className="space-y-2">
              <label
                htmlFor="password"
                className="block text-xs font-semibold uppercase tracking-wider text-[var(--color-text-muted)]"
              >
                Nueva contraseña
              </label>
              <input
                id="password"
                type="password"
                required
                minLength={6}
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full rounded-[16px] bg-[#2c3833] px-4 py-3 text-sm text-[#f2f5f9] placeholder:text-[var(--color-text-muted)] focus:outline-none focus:ring-2 focus:ring-[#84a584]"
              />
              <p className="text-xs text-[var(--color-text-muted)]">
                Mínimo 6 caracteres
              </p>
            </div>

            <div className="space-y-2">
              <label
                htmlFor="confirmPassword"
                className="block text-xs font-semibold uppercase tracking-wider text-[var(--color-text-muted)]"
              >
                Confirmar nueva contraseña
              </label>
              <input
                id="confirmPassword"
                type="password"
                required
                placeholder="••••••••"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
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
              {loading ? "Actualizando..." : "Actualizar contraseña"}
            </button>
          </form>
        )}
      </div>

      <p className="mt-6 text-center text-xs text-[var(--color-text-muted)]">
        <a
          href="/auth/login"
          className="text-[#84a584] hover:underline"
        >
          Volver al inicio de sesión
        </a>
      </p>
    </div>
  );
}
