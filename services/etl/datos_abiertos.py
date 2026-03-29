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
    "AF": {
        "controller": "CE_DA_AF_CONTROLLER_JSON",
        "date_from":  "bgnYmdAF",
        "date_to":    "endYmdAF",
        "inst_cd":    "instCdAF",
        "inst_nm":    "instNmAF",
    },
    "C": {
        "controller": "CE_DA_C_CONTROLLER_JSON",
        "date_from":  "bgnYmdC",
        "date_to":    "endYmdC",
        "inst_cd":    "instCdC",
        "inst_nm":    "instNmC",
    },
    "OP": {
        "controller": "CE_DA_OP_CONTROLLER_JSON",
        "date_from":  "bgnYmdOP",
        "date_to":    "endYmdOP",
        "inst_cd":    "instCdOP",
        "inst_nm":    "instNmOP",
    },
    "A": {
        "controller": "CE_DA_A_CONTROLLER_JSON",
        "date_from":  "bgnYmdA",
        "date_to":    "endYmdA",
        "inst_cd":    "instCdA",
        "inst_nm":    "instNmA",
    },
    "R": {
        "controller": "CE_DA_R_CONTROLLER_JSON",
        "date_from":  "bgnYmdR",
        "date_to":    "endYmdR",
        "inst_cd":    "instCdR",
        "inst_nm":    "instNmR",
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


# ─── AF (adjudication) parser ─────────────────────────────────────────────────

def parse_af_record(r: dict) -> dict | None:
    """
    AF report → fecha_adj_firme + desierto for licitaciones_medicas upsert.

    The AF flat array contains 3 interleaved schemas:
      HEADER   — has NUMERO_PROCEDIMIENTO  (we parse these)
      PARTIDA  — has NUMERO_PARTIDA        (skip)
      PRICING  — has CEDULA_PROVEEDOR/NRO_ACTO but no NUMERO_PROCEDIMIENTO (skip)
    """
    key = r.get("NUMERO_PROCEDIMIENTO")
    if not key:
        return None
    fecha = r.get("FECHA_ADJ_FIRME") or None
    desierto_raw = (r.get("DESIERTO") or "N").strip().upper()
    desierto = desierto_raw != "N"
    return {
        "instcartelno":   key,
        "fecha_adj_firme": fecha,
        "desierto":        desierto,
    }


def parse_af_pricing_record(r: dict, current_instcartelno: str | None) -> dict | None:
    """
    AF report → precios_historicos row.

    PRICING records have CEDULA_PROVEEDOR or PRECIO_UNITARIO_ADJUDICADO but
    no NUMERO_PROCEDIMIENTO and no NUMERO_PARTIDA. The caller is responsible
    for passing the most recently seen HEADER's instcartelno.

    Returns None if:
      - current_instcartelno is None (no parent HEADER seen yet)
      - row does not look like a PRICING record
      - both precio_unitario and cantidad are None (no useful data)
    """
    if current_instcartelno is None:
        return None
    # Must not be a HEADER (has NUMERO_PROCEDIMIENTO) or PARTIDA (has NUMERO_PARTIDA)
    if r.get("NUMERO_PROCEDIMIENTO") or r.get("NUMERO_PARTIDA"):
        return None
    # Must look like a PRICING record
    if not (r.get("CEDULA_PROVEEDOR") or r.get("PRECIO_UNITARIO_ADJUDICADO")):
        return None

    # precio_unitario
    raw_precio = r.get("PRECIO_UNITARIO_ADJUDICADO")
    try:
        precio_unitario = float(raw_precio) if raw_precio is not None else None
    except (ValueError, TypeError):
        precio_unitario = None

    # cantidad
    raw_cantidad = r.get("CANTIDAD_ADJUDICADA")
    try:
        cantidad = float(raw_cantidad) if raw_cantidad is not None else None
    except (ValueError, TypeError):
        cantidad = None

    # Skip rows with no useful numeric data
    if precio_unitario is None and cantidad is None:
        return None

    descripcion = (
        r.get("DESCRIPCION")
        or r.get("NOMBRE_PRODUCTO")
        or r.get("DESCRIPCION_LINEA")
        or ""
    )

    return {
        "instcartelno":        current_instcartelno,
        "descripcion_item":    descripcion,
        "clasificacion_unspsc": r.get("CODIGO_IDENTIFICACION") or r.get("CODIGO_PRODUCTO") or None,
        "proveedor":           r.get("NOMBRE_PROVEEDOR") or r.get("CEDULA_PROVEEDOR") or None,
        "precio_unitario":     precio_unitario,
        "cantidad":            cantidad,
        "unidad":              r.get("UNIDAD_MEDIDA") or None,
        "fuente":              "AF",
        "rawdata":             r,
    }


# ─── Contratos (C) parsers ────────────────────────────────────────────────────

def parse_c_record(r: dict) -> dict | None:
    """
    C report HEADER → instcartelno context for pricing sub-records.
    HEADER records have NUMERO_PROCEDIMIENTO. Returns minimal dict with key only.
    """
    key = r.get("NUMERO_PROCEDIMIENTO") or r.get("NRO_PROCEDIMIENTO")
    if not key:
        return None
    return {"instcartelno": key}


def parse_c_pricing_record(r: dict, current_instcartelno: str | None) -> dict | None:
    """
    C report line items (Report 7.2) → precios_historicos rows.

    Line records have PRECIO_UNITARIO / CANTIDADCONTRATADA but no NUMERO_PROCEDIMIENTO.
    The caller maintains current_instcartelno from the most-recent HEADER record.

    Returns None if:
      - current_instcartelno is None
      - record is a HEADER (has NUMERO_PROCEDIMIENTO)
      - no useful numeric data
    """
    if current_instcartelno is None:
        return None
    if r.get("NUMERO_PROCEDIMIENTO") or r.get("NRO_PROCEDIMIENTO"):
        return None  # Header row — not a pricing row

    raw_precio = (
        r.get("PRECIO_UNITARIO")
        or r.get("PRECIOUNITARIO")
        or r.get("precioUnitario")
    )
    try:
        precio_unitario = float(raw_precio) if raw_precio is not None else None
    except (ValueError, TypeError):
        precio_unitario = None

    raw_cantidad = (
        r.get("CANTIDAD_CONTRATADA")
        or r.get("CANTIDADCONTRATADA")
        or r.get("cantidadContratada")
    )
    try:
        cantidad = float(raw_cantidad) if raw_cantidad is not None else None
    except (ValueError, TypeError):
        cantidad = None

    if precio_unitario is None and cantidad is None:
        return None

    descripcion = (
        r.get("DESCRIPCION")
        or r.get("NOMBRE_PRODUCTO")
        or r.get("DESCRIPCION_LINEA")
        or ""
    )

    return {
        "instcartelno":        current_instcartelno,
        "descripcion_item":    descripcion,
        "clasificacion_unspsc": (
            r.get("CODIGO_IDENTIFICACION")
            or r.get("CODIGOIDENTIFICACION")
            or None
        ),
        "proveedor":   r.get("NOMBRE_PROVEEDOR") or r.get("CEDULA_PROVEEDOR") or None,
        "precio_unitario": precio_unitario,
        "cantidad":    cantidad,
        "unidad":      r.get("UNIDAD_MEDIDA") or r.get("UNIDAD") or None,
        "fuente":      "C",
        "rawdata":     r,
    }


# ─── Recursos (R) parser ──────────────────────────────────────────────────────

def parse_r_record(r: dict) -> dict | None:
    """R report → da_recursos row (appeals / protests per tender)."""
    key = r.get("NUMERO_PROCEDIMIENTO") or r.get("NRO_PROCEDIMIENTO")
    if not key:
        return None
    return {
        "instcartelno":    key,
        "asunto":          r.get("ASUNTO") or r.get("asunto"),
        "cedula_proveedor": (
            r.get("CEDULA_PROVEEDOR")
            or r.get("CEDULAPROVEEDOR")
            or r.get("cedulaProveedor")
        ),
        "tipo_recurso":    (
            r.get("TIPO_RECURSO")
            or r.get("TIPORECURSO")
            or r.get("tipoRecurso")
        ),
        "fecha_solicitud": (
            r.get("FECHA_SOLICITUD")
            or r.get("FECHASOLICITUD")
            or r.get("fechaSolicitud")
        ),
        "rawdata":         r,
    }


# ─── Aclaraciones (A) parser ──────────────────────────────────────────────────

def parse_a_record(r: dict) -> dict | None:
    """A report → da_aclaraciones row (clarifications per tender)."""
    key = r.get("NUMERO_PROCEDIMIENTO") or r.get("NRO_PROCEDIMIENTO")
    if not key:
        return None
    return {
        "instcartelno":    key,
        "titulo":          r.get("TITULO") or r.get("titulo"),
        "fecha_solicitud": (
            r.get("FECHA_SOLICITUD")
            or r.get("FECHASOLICITUD")
            or r.get("fechaSolicitud")
        ),
        "solicitante":     r.get("SOLICITANTE") or r.get("solicitante"),
        "rawdata":         r,
    }


# ─── Órdenes de Pedido (OP) parser ───────────────────────────────────────────

def parse_op_record(r: dict) -> dict | None:
    """OP report → da_ordenes_pedido row (purchase execution)."""
    numero_orden = (
        r.get("NUMERO_ORDEN_PEDIDO")
        or r.get("NUMEROORDENPEDIDO")
        or r.get("numeroOrdenPedido")
    )
    if not numero_orden:
        return None

    key = r.get("NUMERO_PROCEDIMIENTO") or r.get("NRO_PROCEDIMIENTO")

    raw_precio = r.get("PRECIO_UNITARIO") or r.get("PRECIOUNITARIO")
    try:
        precio_unitario = float(raw_precio) if raw_precio is not None else None
    except (ValueError, TypeError):
        precio_unitario = None

    raw_cantidad = r.get("CANTIDAD") or r.get("cantidad")
    try:
        cantidad = float(raw_cantidad) if raw_cantidad is not None else None
    except (ValueError, TypeError):
        cantidad = None

    raw_monto = r.get("MONTO_TOTAL") or r.get("MONTOTOTAL") or r.get("montoTotal")
    try:
        monto_total = float(raw_monto) if raw_monto is not None else None
    except (ValueError, TypeError):
        monto_total = None

    return {
        "instcartelno":    key,  # nullable — OP may reference contract, not procedure
        "numero_orden":    numero_orden,
        "cedula_proveedor": (
            r.get("CEDULA_PROVEEDOR")
            or r.get("CEDULAPROVEEDOR")
            or r.get("cedulaProveedor")
        ),
        "precio_unitario": precio_unitario,
        "cantidad":        cantidad,
        "unidad":          r.get("UNIDAD_MEDIDA") or r.get("UNIDAD") or None,
        "monto_total":     monto_total,
        "currencytype":    r.get("TIPO_MONEDA") or r.get("TIPOMONEDA") or None,
        "fecha_orden":     r.get("FECHA_ORDEN") or r.get("FECHAORDEN") or None,
        "rawdata":         r,
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
    # Deduplicate by (instcartelno, suppliercd) — O report can return dupes in same batch
    seen: dict[tuple, dict] = {}
    for r in valid:
        seen[(r["instcartelno"], r["suppliercd"])] = r
    valid = list(seen.values())
    if not valid:
        return 0
    (
        supabase_client.table("da_ofertas")
        .upsert(valid, on_conflict="instcartelno,suppliercd")
        .execute()
    )
    logger.info("DA ofertas: %d rows upserted", len(valid))
    return len(valid)


def upsert_adjudicaciones(rows: list[dict], supabase_client) -> int:
    """
    Patch fecha_adj_firme and desierto onto licitaciones_medicas via upsert.
    Returns count of rows written.
    """
    valid = [r for r in rows if r and r.get("instcartelno")]
    if not valid:
        return 0
    # Deduplicate by instcartelno — AF can return multiple HEADER rows per procedure
    seen: dict[str, dict] = {}
    for r in valid:
        seen[r["instcartelno"]] = r
    valid = list(seen.values())
    (
        supabase_client.table("licitaciones_medicas")
        .upsert(valid, on_conflict="instcartelno")
        .execute()
    )
    logger.info("DA adjudicaciones: %d rows patched", len(valid))
    return len(valid)


def upsert_precios_historicos(rows: list[dict], supabase_client) -> int:
    """
    Insert pricing rows into precios_historicos.
    Uses INSERT (not upsert) — no dedup unique key on the table.
    Skips rows where descripcion_item is "" AND precio_unitario is None.
    Returns count of rows inserted.
    """
    valid = [
        r for r in rows
        if r
        and r.get("instcartelno")
        and not (r.get("descripcion_item") == "" and r.get("precio_unitario") is None)
    ]
    if not valid:
        return 0
    supabase_client.table("precios_historicos").insert(valid).execute()
    logger.info("DA precios: %d rows inserted", len(valid))
    return len(valid)


def upsert_recursos(rows: list[dict], supabase_client) -> int:
    """Insert appeal/resource rows into da_recursos. Dedup by (instcartelno, cedula_proveedor, fecha_solicitud)."""
    valid = [r for r in rows if r and r.get("instcartelno")]
    if not valid:
        return 0
    seen: dict[tuple, dict] = {}
    for r in valid:
        key = (r["instcartelno"], r.get("cedula_proveedor"), r.get("fecha_solicitud"))
        seen[key] = r
    valid = list(seen.values())
    supabase_client.table("da_recursos").insert(valid).execute()
    logger.info("DA recursos: %d rows inserted", len(valid))
    return len(valid)


def upsert_aclaraciones(rows: list[dict], supabase_client) -> int:
    """Insert clarification rows into da_aclaraciones. Dedup by (instcartelno, fecha_solicitud, solicitante)."""
    valid = [r for r in rows if r and r.get("instcartelno")]
    if not valid:
        return 0
    seen: dict[tuple, dict] = {}
    for r in valid:
        key = (r["instcartelno"], r.get("fecha_solicitud"), r.get("solicitante"))
        seen[key] = r
    valid = list(seen.values())
    supabase_client.table("da_aclaraciones").insert(valid).execute()
    logger.info("DA aclaraciones: %d rows inserted", len(valid))
    return len(valid)


def upsert_ordenes_pedido(rows: list[dict], supabase_client) -> int:
    """Insert purchase order rows into da_ordenes_pedido. Dedup by numero_orden."""
    valid = [r for r in rows if r and r.get("numero_orden")]
    if not valid:
        return 0
    seen: dict[str, dict] = {}
    for r in valid:
        seen[r["numero_orden"]] = r
    valid = list(seen.values())
    supabase_client.table("da_ordenes_pedido").upsert(valid, on_conflict="numero_orden").execute()
    logger.info("DA ordenes_pedido: %d rows upserted", len(valid))
    return len(valid)


# ─── Catalog fetchers (no date range — static reference data) ────────────────

async def fetch_proveedores(supabase_client) -> int:
    """
    Fetch supplier catalog from CE_DA_P_CONTROLLER_JSON (Report 9).
    Uses tamano="" to fetch all suppliers. No date params.
    Upserts into `proveedores` table. Returns count upserted.
    """
    cfg = {
        "controller": "CE_DA_P_CONTROLLER_JSON",
        "inst_cd":    "tamano",
    }
    async with httpx.AsyncClient(follow_redirects=True) as client:
        url = f"{SERVLET_BASE}/{cfg['controller']}.java"
        params = {"tamano": "", "cmd": "create"}
        try:
            r = await client.post(url, data=params, headers=HEADERS, timeout=60)
            r.raise_for_status()
            token = r.text.strip()
            if not token:
                logger.warning("DA P: empty token")
                return 0
            await asyncio.sleep(1.5)
            dl_url = f"{SERVLET_BASE}/{cfg['controller']}.java"
            dl = await client.get(
                dl_url,
                params={"cmd": "download", "fileZipName": token},
                headers=HEADERS,
                timeout=120,
            )
            dl.raise_for_status()
            with zipfile.ZipFile(io.BytesIO(dl.content)) as zf:
                name = zf.namelist()[0]
                raw = json.loads(zf.read(name).decode("utf-8", errors="replace"))
            records = raw if isinstance(raw, list) else raw.get("lista", raw.get("data", []))
            logger.info("DA P: %d supplier records", len(records))
        except Exception as e:
            logger.error("DA P fetch failed: %s", e)
            return 0

    rows = []
    for rec in records:
        cedula = rec.get("CEDULA") or rec.get("CEDULA_PROVEEDOR") or rec.get("cedulaProveedor")
        nombre = rec.get("NOMBRE") or rec.get("NOMBRE_PROVEEDOR") or rec.get("nombreProveedor")
        if not cedula or not nombre:
            continue
        rows.append({
            "cedula":    cedula,
            "nombre":    nombre,
            "tamano":    rec.get("TAMANO") or rec.get("tamano"),
            "provincia": rec.get("PROVINCIA") or rec.get("provincia"),
            "canton":    rec.get("CANTON") or rec.get("canton"),
            "rawdata":   rec,
        })

    if not rows or supabase_client is None:
        return 0
    supabase_client.table("proveedores").upsert(rows, on_conflict="cedula").execute()
    logger.info("DA proveedores: %d rows upserted", len(rows))
    return len(rows)


async def fetch_catalogo_bienes(cate_id: str, supabase_client) -> int:
    """
    Fetch product catalog from CE_DA_CB_CONTROLLER_JSON (Report 10) for a given cateId.
    No date params. Returns count upserted into `catalogo_bienes`.
    """
    async with httpx.AsyncClient(follow_redirects=True) as client:
        url = f"{SERVLET_BASE}/CE_DA_CB_CONTROLLER_JSON.java"
        params = {"cateId": cate_id, "cmd": "create"}
        try:
            r = await client.post(url, data=params, headers=HEADERS, timeout=60)
            r.raise_for_status()
            token = r.text.strip()
            if not token:
                logger.warning("DA CB (cateId=%s): empty token", cate_id)
                return 0
            await asyncio.sleep(1.5)
            dl = await client.get(
                url,
                params={"cmd": "download", "fileZipName": token},
                headers=HEADERS,
                timeout=120,
            )
            dl.raise_for_status()
            with zipfile.ZipFile(io.BytesIO(dl.content)) as zf:
                name = zf.namelist()[0]
                raw = json.loads(zf.read(name).decode("utf-8", errors="replace"))
            records = raw if isinstance(raw, list) else raw.get("lista", raw.get("data", []))
            logger.info("DA CB (cateId=%s): %d records", cate_id, len(records))
        except Exception as e:
            logger.error("DA CB (cateId=%s) fetch failed: %s", cate_id, e)
            return 0

    rows = []
    for rec in records:
        cod_ident = (
            rec.get("CODIGO_IDENTIFICACION")
            or rec.get("CODIGOIDENTIFICACION")
            or rec.get("codigoIdentificacion")
        )
        if not cod_ident:
            continue
        rows.append({
            "codigo_clasificacion":       (
                rec.get("CODIGO_CLASIFICACION")
                or rec.get("CODIGOCLASIFICACION")
            ),
            "codigo_identificacion":      cod_ident,
            "codigo_producto":            (
                rec.get("CODIGO_PRODUCTO")
                or rec.get("CODIGOPRODUCTO")
                or None
            ),
            "descripcion_clasificacion":  (
                rec.get("DESCRIPCION_CLASIFICACION")
                or rec.get("DESCRIPCIONCLASIFICACION")
            ),
            "descripcion_identificacion": (
                rec.get("DESCRIPCION_IDENTIFICACION")
                or rec.get("DESCRIPCIONIDENTIFICACION")
            ),
            "descripcion_producto":       (
                rec.get("DESCRIPCION_PRODUCTO")
                or rec.get("DESCRIPCIONPRODUCTO")
                or None
            ),
            "rawdata": rec,
        })

    if not rows or supabase_client is None:
        return 0
    supabase_client.table("catalogo_bienes").upsert(
        rows, on_conflict="codigo_identificacion"
    ).execute()
    logger.info("DA catalogo_bienes (cateId=%s): %d rows upserted", cate_id, len(rows))
    return len(rows)


async def fetch_instituciones_compradoras(supabase_client) -> int:
    """
    Fetch buyer institution catalog from CE_DA_IC_CONTROLLER_JSON (Report 11).
    Params: instCdIC, provincias, cantones — all empty for full catalog.
    Upserts into `instituciones_salud` table.
    Returns count upserted.
    """
    async with httpx.AsyncClient(follow_redirects=True) as client:
        url = f"{SERVLET_BASE}/CE_DA_IC_CONTROLLER_JSON.java"
        params = {"instCdIC": "", "provincias": "", "cantones": "", "cmd": "create"}
        try:
            r = await client.post(url, data=params, headers=HEADERS, timeout=60)
            r.raise_for_status()
            token = r.text.strip()
            if not token:
                logger.warning("DA IC: empty token")
                return 0
            await asyncio.sleep(1.5)
            dl = await client.get(
                url,
                params={"cmd": "download", "fileZipName": token},
                headers=HEADERS,
                timeout=120,
            )
            dl.raise_for_status()
            with zipfile.ZipFile(io.BytesIO(dl.content)) as zf:
                name = zf.namelist()[0]
                raw = json.loads(zf.read(name).decode("utf-8", errors="replace"))
            records = raw if isinstance(raw, list) else raw.get("lista", raw.get("data", []))
            logger.info("DA IC: %d institution records", len(records))
        except Exception as e:
            logger.error("DA IC fetch failed: %s", e)
            return 0

    rows = []
    for rec in records:
        nombre = (
            rec.get("NOMBRE_INSTITUCION")
            or rec.get("NOMBREINSTITUCION")
            or rec.get("nombreInstitucion")
        )
        if not nombre:
            continue
        rows.append({
            "nombre":    nombre,
            "region":    rec.get("PROVINCIA") or rec.get("provincia"),
            "direccion": rec.get("CANTON") or rec.get("canton"),
        })

    if not rows or supabase_client is None:
        return 0
    # instituciones_salud has no unique key on nombre — use INSERT, not upsert
    supabase_client.table("instituciones_salud").insert(rows).execute()
    logger.info("DA instituciones: %d rows inserted", len(rows))
    return len(rows)


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

    Returns: {"scalar": int, "ofertas": int, "adjudicaciones": int}
    """
    import datetime as _dt
    today = _dt.date.today()
    d_to   = _fmt_date(today.strftime("%Y-%m-%d"))
    d_from = _fmt_date((today - _dt.timedelta(days=dias)).strftime("%Y-%m-%d"))

    stats = {
        "scalar": 0, "ofertas": 0, "adjudicaciones": 0,
        "precios": 0, "contratos": 0, "recursos": 0, "aclaraciones": 0, "ordenes": 0,
    }

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
        # Filter to instcartelnos we actually track — FK constraint on da_ofertas
        known_resp = supabase_client.table("licitaciones_medicas").select("instcartelno").limit(50000).execute()
        known_set = {r["instcartelno"] for r in (known_resp.data or [])}
        valid_o = [r for r in o_rows if r and r.get("instcartelno") in known_set]
        logger.info("DA O: %d total offers → %d match tracked procedures", len(o_rows), len(valid_o))
        stats["ofertas"] = upsert_ofertas(valid_o, supabase_client)

    # AF — adjudication dates + desierto (G2) + pricing rows (G9)
    af_raw = await fetch_report("AF", d_from, d_to)
    current_key: str | None = None
    af_rows: list[dict] = []
    af_pricing_rows: list[dict] = []
    for r in af_raw:
        header = parse_af_record(r)
        if header is not None:
            current_key = header["instcartelno"]
            af_rows.append(header)
        else:
            pricing = parse_af_pricing_record(r, current_key)
            if pricing is not None:
                af_pricing_rows.append(pricing)
    if supabase_client:
        valid_af = [r for r in af_rows if r]
        stats["adjudicaciones"] = upsert_adjudicaciones(valid_af, supabase_client)
        stats["precios"] = upsert_precios_historicos(af_pricing_rows, supabase_client)

    # C — contract line prices (G10)
    c_raw = await fetch_report("C", d_from, d_to)
    current_c_key: str | None = None
    c_pricing_rows: list[dict] = []
    for r in c_raw:
        header = parse_c_record(r)
        if header is not None:
            current_c_key = header["instcartelno"]
        else:
            pricing = parse_c_pricing_record(r, current_c_key)
            if pricing is not None:
                c_pricing_rows.append(pricing)
    if supabase_client:
        stats["contratos"] = upsert_precios_historicos(c_pricing_rows, supabase_client)

    # R — appeals / resources (G6)
    r_raw = await fetch_report("R", d_from, d_to)
    r_rows = [parse_r_record(r) for r in r_raw]
    if supabase_client:
        stats["recursos"] = upsert_recursos(r_rows, supabase_client)

    # A — clarifications (G5)
    a_raw = await fetch_report("A", d_from, d_to)
    a_rows = [parse_a_record(r) for r in a_raw]
    if supabase_client:
        stats["aclaraciones"] = upsert_aclaraciones(a_rows, supabase_client)

    # OP — purchase orders (G11)
    op_raw = await fetch_report("OP", d_from, d_to)
    op_rows = [parse_op_record(r) for r in op_raw]
    if supabase_client:
        stats["ordenes"] = upsert_ordenes_pedido(op_rows, supabase_client)

    logger.info("DA run complete: %s", stats)
    return stats
