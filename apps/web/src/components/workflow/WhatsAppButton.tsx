// apps/web/src/components/workflow/WhatsAppButton.tsx
import { MessageCircle } from "lucide-react"

interface WhatsAppButtonProps {
  instcartelno: string
  cartelnm: string | null
  instnm: string | null
  biddocEndDt: string | null
  montoColones: number | null
  currencyType: string | null
  presupuestoEstimado: number | null
  monedaPresupuesto: string | null
}

function formatDate(dateStr: string | null): string {
  if (!dateStr) return "N/A"
  return new Date(dateStr).toLocaleDateString("es-CR", {
    year: "numeric", month: "long", day: "numeric",
  })
}

export function WhatsAppButton({
  instcartelno,
  cartelnm,
  instnm,
  biddocEndDt,
  montoColones,
  currencyType,
  presupuestoEstimado,
  monedaPresupuesto,
}: WhatsAppButtonProps) {
  const lines = [
    `*Licitación SICOP*`,
    ``,
    `📋 *Descripción:* ${cartelnm ?? "N/A"}`,
    `🏛️ *Institución:* ${instnm ?? "N/A"}`,
    `🔑 *Código:* ${instcartelno}`,
    `📅 *Deadline:* ${formatDate(biddocEndDt)}`,
  ]

  const monto = presupuestoEstimado ?? montoColones
  const moneda = monedaPresupuesto ?? currencyType

  if (monto) {
    const symbol = moneda === "USD" ? "$" : "₡"
    lines.push(`💰 *Monto estimado:* ${symbol}${monto.toLocaleString("es-CR")}`)
  }

  lines.push(``, `¿Pueden cumplir con estas especificaciones?`)

  const text = encodeURIComponent(lines.join("\n"))
  const href = `https://wa.me/?text=${text}`

  return (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      className="inline-flex items-center gap-2 rounded-[60px] bg-[#84a584] px-5 py-2.5 text-sm font-semibold text-[#1c1a1f] transition-colors hover:bg-[#9ab89a]"
    >
      <MessageCircle size={16} />
      Contactar fabricante
    </a>
  )
}
