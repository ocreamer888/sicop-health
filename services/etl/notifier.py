"""
Notification Service

Envía alertas por email (Resend) y WhatsApp cuando hay nuevas licitaciones
que coinciden con las preferencias del usuario.
"""

import logging
import os
from typing import List
from supabase import create_client, Client

logger = logging.getLogger(__name__)

# Cliente Supabase
_supabase_client: Client | None = None


def get_supabase_client() -> Client:
    """Obtiene o crea el cliente de Supabase."""
    global _supabase_client
    if _supabase_client is None:
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_SERVICE_KEY")

        if not url or not key:
            raise ValueError("SUPABASE_URL y SUPABASE_SERVICE_KEY son requeridos")

        _supabase_client = create_client(url, key)

    return _supabase_client


async def send_notifications(licitaciones: List[dict], tipo: str = "nueva"):
    """
    Envía notificaciones a usuarios que tienen alertas configuradas.

    Args:
        licitaciones: Lista de licitaciones nuevas/actualizadas
        tipo: 'nueva' o 'actualizada'
    """
    if not licitaciones:
        return

    try:
        supabase = get_supabase_client()

        # Obtener configuraciones de alertas activas
        alertas_result = supabase.table("alertas_config") \
            .select("*, user:auth.users(email)") \
            .eq("activo", True) \
            .execute()

        alertas = alertas_result.data
        logger.info(f"Procesando {len(alertas)} configuraciones de alerta")

        for alerta in alertas:
            matching_lics = filter_matching_licitaciones(licitaciones, alerta)

            if matching_lics:
                user_email = alerta.get('user', {}).get('email')
                canales = alerta.get('canal', ['email'])

                if 'email' in canales and user_email:
                    await send_email_notification(user_email, matching_lics, tipo)

                if 'whatsapp' in canales:
                    await send_whatsapp_notification(alerta, matching_lics, tipo)

    except Exception as e:
        logger.exception(f"Error enviando notificaciones: {e}")


def filter_matching_licitaciones(licitaciones: List[dict], alerta: dict) -> List[dict]:
    """Filtra licitaciones que coinciden con la configuración de alerta."""
    matching = []

    keywords = [k.lower() for k in (alerta.get('keywords') or [])]
    categorias = [c.upper() for c in (alerta.get('categorias') or [])]
    unspsc_codes = alerta.get('unspsc') or []

    for lic in licitaciones:
        descripcion = str(lic.get('descripcion', '')).lower()
        categoria = str(lic.get('categoria', '')).upper()
        unspsc = str(lic.get('clasificacion_unspsc', ''))

        # Check keywords
        keyword_match = any(kw in descripcion for kw in keywords)

        # Check categoría
        categoria_match = categoria in categorias if categorias else True

        # Check UNSPSC
        unspsc_match = any(unspsc.startswith(code) for code in unspsc_codes) if unspsc_codes else True

        if keyword_match or categoria_match or unspsc_match:
            matching.append(lic)

    return matching


async def send_email_notification(to_email: str, licitaciones: List[dict], tipo: str):
    """Envía notificación por email usando Resend."""
    try:
        import resend

        api_key = os.environ.get("RESEND_API_KEY")
        from_email = os.environ.get("RESEND_FROM_EMAIL", "noreply@sicop-health.com")

        if not api_key:
            logger.warning("RESEND_API_KEY no configurado, saltando email")
            return

        resend.api_key = api_key

        # Construir email
        subject = f"{'Nuevas' if tipo == 'nueva' else 'Actualizadas'} licitaciones médicas en SICOP"

        html_content = build_email_html(licitaciones, tipo)

        params = {
            "from": f"SICOP Health <{from_email}>",
            "to": [to_email],
            "subject": subject,
            "html": html_content,
        }

        result = resend.Emails.send(params)
        logger.info(f"Email enviado a {to_email}: {result}")

    except Exception as e:
        logger.error(f"Error enviando email a {to_email}: {e}")


def build_email_html(licitaciones: List[dict], tipo: str) -> str:
    """Construye el HTML del email."""
    rows = ""
    for lic in licitaciones[:10]:  # Máximo 10 en email
        rows += f"""
        <tr>
            <td style="padding: 10px; border-bottom: 1px solid #eee;">
                <strong>{lic.get('numero_procedimiento', 'N/A')}</strong><br>
                <small>{lic.get('descripcion', 'Sin descripción')[:100]}...</small>
            </td>
            <td style="padding: 10px; border-bottom: 1px solid #eee;">
                {lic.get('categoria', 'N/A')}
            </td>
            <td style="padding: 10px; border-bottom: 1px solid #eee;">
                {lic.get('estado', 'N/A')}
            </td>
        </tr>
        """

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>SICOP Health - Alertas</title>
    </head>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #2563eb;">SICOP Health Intelligence</h2>
            <p>Hay <strong>{len(licitaciones)}</strong> licitaciones {'nuevas' if tipo == 'nueva' else 'actualizadas'} que coinciden con tus alertas.</p>

            <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                <thead>
                    <tr style="background: #f3f4f6;">
                        <th style="padding: 10px; text-align: left;">Licitación</th>
                        <th style="padding: 10px; text-align: left;">Categoría</th>
                        <th style="padding: 10px; text-align: left;">Estado</th>
                    </tr>
                </thead>
                <tbody>
                    {rows}
                </tbody>
            </table>

            <p style="text-align: center;">
                <a href="https://sicop-health.com/licitaciones" style="background: #2563eb; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px;">
                    Ver todas en el dashboard
                </a>
            </p>

            <hr style="margin: 30px 0; border: none; border-top: 1px solid #e5e7eb;">
            <p style="font-size: 12px; color: #6b7280;">
                SICOP Health Intelligence - Plataforma de inteligencia de licitaciones médicas
            </p>
        </div>
    </body>
    </html>
    """
    return html


async def send_whatsapp_notification(alerta: dict, licitaciones: List[dict], tipo: str):
    """Envía notificación por WhatsApp (placeholder para implementación futura)."""
    # TODO: Implementar integración con WhatsApp Business API
    logger.info(f"WhatsApp notification not yet implemented for alerta {alerta.get('id')}")
