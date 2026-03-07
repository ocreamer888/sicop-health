interface LicitacionData {
  instcartelno: string;
  cartelnm: string | null;
  instnm: string | null;
  categoria: string | null;
  monto_colones: number | null;
  currency_type: string | null;
  biddoc_end_dt: string | null;
}

interface EmailPayload {
  user_email: string;
  licitacion: LicitacionData;
  site_url: string;
}

function formatMonto(monto: number | null, currency: string | null): string {
  if (!monto) return "—";
  const sym = currency === "USD" ? "$" : "₡";
  return `${sym}${monto.toLocaleString("es-CR")}`;
}

function formatDate(dt: string | null): string {
  if (!dt) return "—";
  return new Date(dt).toLocaleDateString("es-CR", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}

Deno.serve(async (req) => {
  try {
    const { user_email, licitacion, site_url }: EmailPayload = await req.json();

    const resendKey = Deno.env.get("RESEND_API_KEY");
    if (!resendKey) throw new Error("RESEND_API_KEY not set");

    const html = `
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Nueva licitación — SICOP Health</title>
</head>
<body style="margin:0;padding:0;background-color:#1a1f1a;font-family:'Helvetica Neue',Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#1a1f1a;padding:40px 16px;">
    <tr>
      <td align="center">
        <table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;">
          <!-- Header -->
          <tr>
            <td style="padding-bottom:24px;">
              <span style="font-size:22px;font-weight:700;color:#f9f5df;letter-spacing:-0.5px;">SICOP</span>
              <span style="font-size:13px;color:#84a584;margin-left:8px;">Health Intelligence</span>
            </td>
          </tr>
          <!-- Divider -->
          <tr><td style="height:1px;background-color:#84a584;"></td></tr>
          <!-- Body -->
          <tr>
            <td style="background-color:#2c3833;border-radius:24px;padding:32px;margin-top:24px;">
              <p style="margin:0 0 8px;font-size:12px;color:#84a584;text-transform:uppercase;letter-spacing:1px;">
                Nueva licitación médica detectada
              </p>
              <h1 style="margin:0 0 24px;font-size:20px;font-weight:700;color:#f9f5df;line-height:1.3;">
                ${licitacion.cartelnm ?? "Nueva licitación"}
              </h1>
              <table width="100%" cellpadding="0" cellspacing="0">
                <tr>
                  <td style="padding:10px 0;border-bottom:1px solid #3d4d45;">
                    <span style="font-size:11px;color:#5a6a62;text-transform:uppercase;">Institución</span><br>
                    <span style="font-size:14px;color:#f2f5f9;">${licitacion.instnm ?? "—"}</span>
                  </td>
                </tr>
                <tr>
                  <td style="padding:10px 0;border-bottom:1px solid #3d4d45;">
                    <span style="font-size:11px;color:#5a6a62;text-transform:uppercase;">Categoría</span><br>
                    <span style="font-size:14px;color:#f2f5f9;">${licitacion.categoria ?? "—"}</span>
                  </td>
                </tr>
                <tr>
                  <td style="padding:10px 0;border-bottom:1px solid #3d4d45;">
                    <span style="font-size:11px;color:#5a6a62;text-transform:uppercase;">Monto</span><br>
                    <span style="font-size:14px;color:#f2f5f9;">${formatMonto(licitacion.monto_colones, licitacion.currency_type)}</span>
                  </td>
                </tr>
                <tr>
                  <td style="padding:10px 0;">
                    <span style="font-size:11px;color:#5a6a62;text-transform:uppercase;">Cierre de ofertas</span><br>
                    <span style="font-size:14px;color:#f2f5f9;">${formatDate(licitacion.biddoc_end_dt)}</span>
                  </td>
                </tr>
              </table>
              <!-- CTA -->
              <div style="margin-top:28px;text-align:center;">
                <a href="${site_url}/licitaciones/${licitacion.instcartelno}"
                   style="display:inline-block;background-color:#84a584;color:#ffffff;text-decoration:none;padding:14px 32px;border-radius:60px;font-size:14px;font-weight:600;">
                  Ver Licitación
                </a>
              </div>
            </td>
          </tr>
          <!-- Footer -->
          <tr>
            <td style="padding:24px 0 0;text-align:center;">
              <p style="margin:0;font-size:11px;color:#3d4d45;">
                Recibiste este email porque tienes acceso a SICOP Health Intelligence.
              </p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>`;

    const res = await fetch("https://api.resend.com/emails", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${resendKey}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        from: "SICOP Health <alertas@sicop-health.com>",
        to: [user_email],
        subject: `Nueva licitación: ${licitacion.cartelnm ?? licitacion.instcartelno}`,
        html,
      }),
    });

    if (!res.ok) {
      const body = await res.text();
      throw new Error(`Resend error ${res.status}: ${body}`);
    }

    const data = await res.json();
    return new Response(JSON.stringify({ sent: true, id: data.id }), { status: 200 });
  } catch (err) {
    console.error("send-email error:", err);
    return new Response(JSON.stringify({ error: String(err) }), { status: 500 });
  }
});
