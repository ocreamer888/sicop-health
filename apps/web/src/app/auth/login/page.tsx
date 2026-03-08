import { signIn } from "../actions";

interface PageProps {
  searchParams: Promise<{ error?: string; message?: string }>;
}

export default async function LoginPage({ searchParams }: PageProps) {
  const { error, message } = await searchParams;

  return (
    <div className="w-full h-full flex flex-col items-center justify-center max-w-md">
      {/* Logo */}
      <div className="mb-8 absolute top-12 text-center">
        <span className="text-3xl font-semibold text-[#f9f5df] font-[family-name:var(--font-montserrat)]">
          SICOP
        </span>
        <span className="ml-2 text-base text-[#84a584] font-[family-name:var(--font-raleway)]">
          Health Intelligence
        </span>
      </div>

      <div className="my-4 text-center text-[var(--color-text-muted)] font-[family-name:var(--font-plus-jakarta)]">
      <p className="text-sm text-neutral-400 font-[family-name:var(--font-plus-jakarta)]">
        Inicia sesión en tu cuenta
        </p>
        </div>
        
      {/* Card */}
      <div className="rounded-[24px] bg-[#1a1f1a] p-8 w-full">
        
        <form action={signIn} className="space-y-5">
          <div className="space-y-2">
            <label
              htmlFor="email"
              className="block text-xs font-semibold uppercase tracking-wider text-[var(--color-text-muted)]"
            >
              Correo electrónico
            </label>
            <input
              id="email"
              name="email"
              type="email"
              required
              autoComplete="email"
              placeholder="tu@empresa.com"
              className="w-full rounded-[16px] bg-[#2c3833] px-4 py-3 text-sm text-[#f2f5f9] placeholder:text-[var(--color-text-muted)] focus:outline-none focus:ring-2 focus:ring-[#84a584]"
            />
          </div>

          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <label
                htmlFor="password"
                className="block text-xs font-semibold uppercase tracking-wider text-[var(--color-text-muted)]"
              >
                Contraseña
              </label>
              <a
                href="/auth/forgot-password"
                className="text-xs text-[#84a584] hover:underline"
              >
                ¿Olvidaste tu contraseña?
              </a>
            </div>
            <input
              id="password"
              name="password"
              type="password"
              required
              autoComplete="current-password"
              placeholder="••••••••"
              className="w-full rounded-[16px] bg-[#2c3833] px-4 py-3 text-sm text-[#f2f5f9] placeholder:text-[var(--color-text-muted)] focus:outline-none focus:ring-2 focus:ring-[#84a584]"
            />
          </div>

          {error && (
            <div className="rounded-[12px] bg-[#a58484]/10 border border-[#a58484]/30 px-4 py-3">
              <p className="text-sm text-[#a58484]">{decodeURIComponent(error)}</p>
            </div>
          )}

          {message && (
            <div className="rounded-[12px] bg-[#84a584]/10 border border-[#84a584]/30 px-4 py-3">
              <p className="text-sm text-[#84a584]">{decodeURIComponent(message)}</p>
            </div>
          )}

          <button
            type="submit"
            className="w-full rounded-[60px] bg-[#84a584] px-6 py-3 text-sm font-semibold text-[#1a1f1a] transition-colors hover:bg-[#9ab89a] focus:outline-none focus:ring-2 focus:ring-[#84a584] focus:ring-offset-2 focus:ring-offset-[#1a1f1a]"
          >
            Iniciar sesión
          </button>
        </form>
      </div>

      <p className="mt-6 text-center text-xs text-[var(--color-text-muted)]">
        ¿No tienes cuenta? Contacta al administrador.
      </p>
    </div>
  );
}
