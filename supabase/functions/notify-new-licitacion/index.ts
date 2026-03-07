import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const ALLOWED_ESTADOS = ["Publicado", "Modificado"];

Deno.serve(async (req) => {
  try {
    const payload = await req.json();
    const record = payload.record;

    if (!record) {
      return new Response(JSON.stringify({ error: "No record in payload" }), { status: 400 });
    }

    // Only process medical licitaciones in relevant states
    if (!record.es_medica) {
      return new Response(JSON.stringify({ skipped: "not medical" }), { status: 200 });
    }
    if (!ALLOWED_ESTADOS.includes(record.estado)) {
      return new Response(JSON.stringify({ skipped: `estado=${record.estado}` }), { status: 200 });
    }

    const supabase = createClient(
      Deno.env.get("SUPABASE_URL")!,
      Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!,
    );

    // Insert notification — UNIQUE constraint on instcartelno prevents duplicates
    const { error: insertError } = await supabase
      .from("notificaciones")
      .insert({ instcartelno: record.instcartelno });

    if (insertError?.code === "23505") {
      // Already notified for this licitacion — skip silently
      return new Response(JSON.stringify({ skipped: "duplicate" }), { status: 200 });
    }
    if (insertError) {
      throw new Error(`Insert notificacion: ${insertError.message}`);
    }

    // Fetch all authenticated users
    const { data: usersData, error: usersError } = await supabase.auth.admin.listUsers();
    if (usersError) throw new Error(`listUsers: ${usersError.message}`);

    const users = usersData?.users ?? [];
    const siteUrl = Deno.env.get("SITE_URL") ?? "https://sicop-health-web.vercel.app";
    const emailsSent: string[] = [];

    for (const user of users) {
      if (!user.email) continue;

      // Send email notification
      await fetch(`${Deno.env.get("SUPABASE_URL")}/functions/v1/send-email`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")}`,
        },
        body: JSON.stringify({
          user_email: user.email,
          licitacion: {
            instcartelno: record.instcartelno,
            cartelnm: record.cartelnm,
            instnm: record.instnm,
            categoria: record.categoria,
            monto_colones: record.monto_colones,
            currency_type: record.currency_type,
            biddoc_end_dt: record.biddoc_end_dt,
          },
          site_url: siteUrl,
        }),
      });

      // TODO: WhatsApp notification (provider TBD)
      // await sendWhatsApp(user.phone, record);

      emailsSent.push(user.email);
    }

    return new Response(
      JSON.stringify({ notified: emailsSent.length, users: emailsSent }),
      { status: 200 },
    );
  } catch (err) {
    console.error("notify-new-licitacion error:", err);
    return new Response(JSON.stringify({ error: String(err) }), { status: 500 });
  }
});
