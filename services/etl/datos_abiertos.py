"""
Datos Abiertos scraper — SICOP JSP servlet download layer.

Two-step protocol (confirmed via live probing 2026-03-26):
  1. POST {servlet}/{controller}.java  data={...params, cmd='create'}
     → response.text = plain-text ZIP filename, e.g. "Solicitud de contratac 1774514981965.zip"
  2. GET  {servlet}/{controller}.java?cmd=download&fileZipName={filename}
     → ZIP archive containing one JSON file (direct array, no wrapper)

Date format: DDMMYYYY  (e.g. "01032026" for 2026-03-01)

CCSS cédula in Datos Abiertos: 4000042147
CCSS inst_code in REST API:     0031700001   ← different systems, never mix
"""

import asyncio
import io
import json
import logging
import zipfile
from datetime import date, timedelta

import httpx

logger = logging.getLogger("datos_abiertos")

SERVLET_BASE = "https://www.sicop.go.cr/moduloPcont/servlet/cont/rp"

# Report configuration: maps report key → controller + per-report param suffixes.
REPORT_CONFIGS: dict[str, dict] = {
    "SC": {
        "controller": "CE_DA_SC_CONTROLLER_JSON",
        "date_from":  "bgnYmd",
        "date_to":    "endYmd",
        "inst_cd":    "instCdSC",
        "inst_nm":    "instNmSC",
    },
    "DC": {
        "controller": "CE_DA_DC_CONTROLLER_JSON",
        "date_from":  "bgnYmdDC",
        "date_to":    "endYmdDC",
        "inst_cd":    "instCdDC",
        "inst_nm":    "instNmDC",
    },
    "O": {
        "controller": "CE_DA_O_CONTROLLER_JSON",
        "date_from":  "bgnYmdO",
        "date_to":    "endYmdO",
        "inst_cd":    "instCdO",
        "inst_nm":    "instNmO",
    },
}

HEADERS = {
    "Content-Type": "application/x-www-form-urlencoded",
    "Accept": "*/*",
    "Origin": "https://www.sicop.go.cr",
    "Referer": "https://www.sicop.go.cr/moduloPcont/pcont/rp/CE_MOD_DATOSABIERTOSVIEW.jsp",
    "User-Agent": "Mozilla/5.0 (compatible; sicop-health-etl/1.0)",
}


def _fmt_date(iso: str) -> str:
    """Convert YYYY-MM-DD to DDMMYYYY for DA servlet params."""
    y, m, d = iso.split("-")
    return f"{d}{m}{y}"


async def _create_job(
    client: httpx.AsyncClient,
    cfg: dict,
    date_from: str,
    date_to: str,
    inst_cd: str,
) -> str | None:
    """POST cmd=create → plain-text ZIP filename token."""
    url = f"{SERVLET_BASE}/{cfg['controller']}.java"
    params = {
        cfg["date_from"]: date_from,
        cfg["date_to"]:   date_to,
        cfg["inst_cd"]:   inst_cd,
        cfg["inst_nm"]:   "",
        "cmd":            "create",
    }
    r = await client.post(url, data=params, headers=HEADERS, timeout=60)
    r.raise_for_status()
    token = r.text.strip()
    return token if token else None


async def _download_zip(
    client: httpx.AsyncClient,
    cfg: dict,
    token: str,
) -> list[dict]:
    """GET cmd=download → unzip → parse JSON array."""
    url = f"{SERVLET_BASE}/{cfg['controller']}.java"
    r = await client.get(
        url,
        params={"cmd": "download", "fileZipName": token},
        headers=HEADERS,
        timeout=120,
    )
    r.raise_for_status()
    with zipfile.ZipFile(io.BytesIO(r.content)) as zf:
        name = zf.namelist()[0]
        raw = json.loads(zf.read(name).decode("utf-8", errors="replace"))
    if isinstance(raw, list):
        return raw
    # Defensive: some SICOP endpoints wrap in {"lista": [...]}
    return raw.get("lista", raw.get("data", []))


async def fetch_report(
    report_key: str,
    date_from: str,
    date_to: str,
    inst_cd: str = "",
    retries: int = 3,
) -> list[dict]:
    """
    Fetch a Datos Abiertos report. Returns parsed records or [] on failure.

    Args:
        report_key:  "SC" | "DC" | "O"
        date_from:   DDMMYYYY string (use _fmt_date to convert from ISO)
        date_to:     DDMMYYYY string
        inst_cd:     institution cédula, e.g. "4000042147" for CCSS. "" = all.
        retries:     number of attempts on failure
    """
    cfg = REPORT_CONFIGS[report_key]
    async with httpx.AsyncClient(follow_redirects=True) as client:
        for attempt in range(retries):
            try:
                token = await _create_job(client, cfg, date_from, date_to, inst_cd)
                if not token:
                    logger.warning("DA %s: empty token (attempt %d)", report_key, attempt + 1)
                    await asyncio.sleep(2 ** attempt)
                    continue
                await asyncio.sleep(1.5)  # let server prepare ZIP
                records = await _download_zip(client, cfg, token)
                logger.info("DA %s (%s→%s): %d records", report_key, date_from, date_to, len(records))
                return records
            except Exception as e:
                logger.warning("DA %s attempt %d failed: %s", report_key, attempt + 1, e)
                await asyncio.sleep(2 ** attempt)
    return []


# ─── Parsers ─────────────────────────────────────────────────────────────────

_MODALIDAD_OPEN = {"Cantidad definida", "Según demanda", "Servicios",
                   "Servicios (más de un pedido)", "Cantidad Definida (más de un pedido)"}


def parse_sc_record(r: dict) -> dict | None:
    """SC report → presupuesto_estimado + moneda for licitaciones_medicas upsert."""
    key = r.get("NUMERO_PROCEDIMIENTO") or r.get("numeroProcedimiento")
    if not key:
        return None
    raw_monto = r.get("PRESUPUESTO") or r.get("presupuesto")
    try:
        monto = float(raw_monto) if raw_monto is not None else None
    except (ValueError, TypeError):
        monto = None
    moneda = (r.get("MONEDA") or r.get("moneda") or "CRC").upper().strip()
    return {
        "instcartelno":      key,
        "presupuesto_estimado": monto,
        "moneda_presupuesto":   moneda,
    }


def parse_dc_record(r: dict) -> dict | None:
    """DC report → modalidad_participacion for licitaciones_medicas upsert."""
    key = r.get("NRO_PROCEDIMIENTO") or r.get("nroProcedimiento")
    if not key:
        return None
    raw = (r.get("MODALIDAD_PROCEDIMIENTO") or "").strip()
    if raw == "Precalificación":
        modalidad = "Precalificación"
    elif raw in _MODALIDAD_OPEN:
        modalidad = raw
    else:
        modalidad = None  # unknown — do NOT write empty string to DB
    return {
        "instcartelno":          key,
        "modalidad_participacion": modalidad,
    }


# ─── Oferta parser ────────────────────────────────────────────────────────────

def parse_oferta_record(r: dict) -> dict | None:
    """O report → da_ofertas row."""
    key = r.get("NUMERO_PROCEDIMIENTO") or r.get("numeroProcedimiento")
    if not key:
        return None
    elegible_raw = str(r.get("ELEGIBLE") or r.get("elegible") or "").strip().lower()
    if elegible_raw in ("si", "sí", "s", "1", "true"):
        elegible = True
    elif elegible_raw in ("no", "n", "0", "false"):
        elegible = False
    else:
        elegible = None  # "No evaluada" and similar → unknown
    return {
        "instcartelno": key,
        "suppliernm":   r.get("NOMBRE_PROVEEDOR") or r.get("nombreProveedor"),
        "suppliercd":   r.get("CEDULA_PROVEEDOR")  or r.get("cedulaProveedor"),
        "monto_oferta": None,  # not available at offer header level
        "currencytype": None,
        "elegible":     elegible,
        "orden_merito": None,
        "fecha_apertura": r.get("FECHA_APERTURA") or r.get("fechaApertura"),
        "rawdata":      r,
    }


# ─── Upserters ────────────────────────────────────────────────────────────────

_SCALAR_FIELDS = {"presupuesto_estimado", "moneda_presupuesto", "modalidad_participacion"}


def upsert_scalar_enrichments(rows: list[dict], supabase_client) -> int:
    """
    Patch scalar DA fields onto licitaciones_medicas via upsert.
    Merges SC and DC rows by instcartelno; never writes None values.
    """
    if not rows:
        return 0

    merged: dict[str, dict] = {}
    for row in rows:
        key = row.get("instcartelno")
        if not key:
            continue
        patch = {k: v for k, v in row.items() if k in _SCALAR_FIELDS and v is not None}
        if patch:
            merged.setdefault(key, {"instcartelno": key}).update(patch)

    records = list(merged.values())
    if not records:
        return 0

    (
        supabase_client.table("licitaciones_medicas")
        .upsert(records, on_conflict="instcartelno")
        .execute()
    )
    logger.info("DA scalar: %d rows patched", len(records))
    return len(records)


def upsert_ofertas(rows: list[dict], supabase_client) -> int:
    """Insert offer rows into da_ofertas. Skips rows without suppliercd."""
    valid = [r for r in rows if r and r.get("instcartelno") and r.get("suppliercd")]
    if not valid:
        return 0
    (
        supabase_client.table("da_ofertas")
        .upsert(valid, on_conflict="instcartelno,suppliercd")
        .execute()
    )
    logger.info("DA ofertas: %d rows upserted", len(valid))
    return len(valid)


# ─── Main runner ──────────────────────────────────────────────────────────────

async def run_datos_abiertos(
    dias: int = 30,
    supabase_client=None,
) -> dict:
    """
    Fetch SC, DC, O reports and upsert enrichments.
    Call from main.py after the REST ETL phase.

    Args:
        dias:             rolling window in days (30 for daily runs, 60 for backfill)
        supabase_client:  live Supabase client from uploader.get_supabase_client()

    Returns: {"scalar": int, "ofertas": int}
    """
    import datetime as _dt
    today = _dt.date.today()
    d_to   = _fmt_date(today.strftime("%Y-%m-%d"))
    d_from = _fmt_date((today - _dt.timedelta(days=dias)).strftime("%Y-%m-%d"))

    stats = {"scalar": 0, "ofertas": 0}

    # SC — presupuesto_estimado + moneda_presupuesto
    sc_raw = await fetch_report("SC", d_from, d_to)
    sc_rows = [parse_sc_record(r) for r in sc_raw]

    # DC — modalidad_participacion
    dc_raw = await fetch_report("DC", d_from, d_to)
    dc_rows = [parse_dc_record(r) for r in dc_raw]

    if supabase_client:
        stats["scalar"] = upsert_scalar_enrichments(
            [r for r in sc_rows + dc_rows if r], supabase_client
        )

    # O — offer history (Node 12)
    o_raw = await fetch_report("O", d_from, d_to)
    o_rows = [parse_oferta_record(r) for r in o_raw]
    if supabase_client:
        stats["ofertas"] = upsert_ofertas([r for r in o_rows if r], supabase_client)

    logger.info("DA run complete: %s", stats)
    return stats
