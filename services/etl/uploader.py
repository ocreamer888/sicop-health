# services/etl/uploader.py
"""
SICOP Uploader v2.9
Changes vs v2.8:
- _to_db_row: removidos aliases legacy (numero_procedimiento, descripcion,
  institucion, adjudicatario, clasificacion_unspsc, fecha_tramite,
  fecha_limite_oferta) — causaban 23505 UNIQUE violation en numero_procedimiento
- _CAMPOS_BASE: sincronizado con _to_db_row limpio
- Sin cambios en lógica de upsert, dedup, o insert_modificaciones
"""

import os
import logging
from supabase import create_client

logger = logging.getLogger(__name__)
_supabase_client = None


def get_supabase_client():
    global _supabase_client
    if _supabase_client is None:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY")
        if not url or not key:
            raise RuntimeError("SUPABASE_URL y SUPABASE_SERVICE_KEY deben estar definidos")
        _supabase_client = create_client(url, key)
    return _supabase_client


# ─────────────────────────────────────────────
# MAPEOS
# ─────────────────────────────────────────────

CATEGORIA_MAP = {
    "MEDICAMENTO":    "MEDICAMENTO",
    "EQUIPAMIENTO":   "EQUIPAMIENTO",
    "INSUMO":         "INSUMO",
    "SERVICIO_SALUD": "SERVICIO",
    "TECNOLOGIA":     "SERVICIO",
    "OTRO_MEDICO":    None,
}

ESTADO_MAP = {
    "RPT_PUB": "Publicado",
    "RPT_ADJ": "Adjudicado",
    "RPT_MOD": "Modificado",
}


def _safe_categoria(row: dict) -> str | None:
    cat = (row.get("categoria") or "").strip()
    return CATEGORIA_MAP.get(cat)


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def _f(row: dict, *keys):
    """Retorna el primer valor no-None entre los keys dados."""
    for k in keys:
        v = row.get(k)
        if v is not None:
            return v
    return None


def _dedup(rows: list[dict], key: str) -> tuple[list[dict], int]:
    seen = {}
    for row in rows:
        k = row.get(key)
        if k:
            seen[k] = row
    unique = list(seen.values())
    return unique, len(rows) - len(unique)


def _filter_none(row: dict, keep_false_keys: set[str]) -> dict:
    return {
        k: v for k, v in row.items()
        if v is not None or k in keep_false_keys
    }


_KEEP_FALSY = {"es_medica", "monto_colones"}

# Campos permitidos en el payload de no-médicas (parcial)
# No incluye es_medica ni categoria — no se persisten para no-médicas
_CAMPOS_BASE = {
    "instcartelno", "cartelno", "inst_code",
    "instnm", "cartelnm",
    "procetype", "tipo_procedimiento", "typekey", "estado",
    "modalidad", "excepcion_cd", "cartel_cate", "mod_reason",
    "unspsc_cd",
    "supplier_nm", "supplier_cd",
    "monto_colones", "currency_type", "detalle",
    "biddoc_start_dt", "biddoc_end_dt",
    "openbid_dt", "adj_firme_dt",
    "vigencia_contrato", "unidad_vigencia",
    "raw_data",
}


# ─────────────────────────────────────────────
# EXEC HELPER
# ─────────────────────────────────────────────

def _exec_upsert(
    client,
    rows: list[dict],
    label: str,
    on_conflict: str = "instcartelno",
) -> int:
    """
    Ejecuta upsert con manejo explícito de errores.
    supabase-py >= 2.5 lanza PostgrestAPIError en constraint violations.
    Retorna el número de rows confirmadas por la DB (0 en error).
    """
    try:
        response = (
            client
            .table("licitaciones_medicas")
            .upsert(rows, on_conflict=on_conflict, ignore_duplicates=False)
            .execute()
        )
    except Exception as e:
        logger.error(
            f"[uploader] {label}: excepción en upsert — {type(e).__name__}: {e}. "
            f"Primer instcartelno: {rows[0].get('instcartelno') if rows else 'N/A'}"
        )
        return 0

    if response.data is None:
        logger.error(
            f"[uploader] {label}: response.data=None — posible schema mismatch. "
            f"Primer row keys: {list(rows[0].keys()) if rows else '[]'}"
        )
        return 0

    confirmed = len(response.data)
    if confirmed != len(rows):
        logger.warning(
            f"[uploader] {label}: enviados={len(rows)} confirmados={confirmed} "
            f"— {len(rows) - confirmed} rows no procesadas"
        )

    logger.info(f"[uploader] {label}: {confirmed} rows confirmadas por DB")
    return confirmed


# ─────────────────────────────────────────────
# MAPEO PARSER → DB
# ─────────────────────────────────────────────

def _to_db_row(row: dict) -> dict:
    """
    Normaliza un row del parser (cualquier convención de keys) al schema v2.9.
    _f() resuelve camelCase, snake_case, y lowercase sin guiones.
    Aliases legacy (numero_procedimiento, descripcion, institucion, etc.)
    removidos en v2.9 — causaban UNIQUE violation en numero_procedimiento.
    """
    instcartelno = _f(row, "instcartelno", "instCartelNo", "inst_cartel_no")
    cartelnm     = _f(row, "cartelnm",     "cartelNm",     "cartel_nm")
    instnm       = _f(row, "instnm",       "instNm",       "inst_nm")
    cartelno     = _f(row, "cartelno",     "cartelNo",     "cartel_no")
    procetype    = _f(row, "procetype",    "proceType",    "proce_type")
    typekey      = _f(row, "typekey",      "typeKey",      "type_key")
    suppliernm   = _f(row, "suppliernm",   "supplierNm",   "supplier_nm")
    suppliercd   = _f(row, "suppliercd",   "supplierCd",   "supplier_cd")
    unspsccd     = _f(row, "unspsccd",     "unspscCd",     "unspsc_cd")
    currencytype = _f(row, "currencytype", "currencyType", "currency_type")
    rawdata      = _f(row, "rawdata",      "raw_data")
    biddocstart  = _f(row, "biddocstartdt",    "biddocStartDt",    "biddoc_start_dt")
    biddocend    = _f(row, "biddocenddt",      "biddocEndDt",      "biddoc_end_dt")
    openbiddt    = _f(row, "openbiddt",        "openbidDt",        "openbid_dt")
    adjfirmedt   = _f(row, "adjfirmedt",       "adjFirmeDt",       "adj_firme_dt")
    vigencia     = _f(row, "vigenciacontrato", "vigenciaContrato", "vigencia_contrato")
    unidadvig    = _f(row, "unidadvigencia",   "unidadVigencia",   "unidad_vigencia")
    excepcioncd  = _f(row, "excepcioncd",      "excepcionCd",      "excepcion_cd")
    cartelcate   = _f(row, "cartelcate",       "cartelCate",       "cartel_cate")
    modreason    = _f(row, "modreason",        "modReason",        "mod_reason")

    return {
        # — Identificadores —
        "instcartelno":       instcartelno,
        "cartelno":           cartelno,
        "inst_code":          row.get("inst_code"),

        # — Institución y descripción —
        "instnm":             instnm,
        "cartelnm":           cartelnm,

        # — Procedimiento —
        "procetype":          procetype,
        "tipo_procedimiento": row.get("tipo_procedimiento"),
        "typekey":            typekey,
        "estado":             ESTADO_MAP.get(typekey or ""),
        "modalidad":          row.get("modalidad"),
        "excepcion_cd":       excepcioncd,
        "cartel_cate":        cartelcate,
        "mod_reason":         modreason,

        # — Clasificación —
        "unspsc_cd":          unspsccd,

        # — Proveedor —
        "supplier_nm":        suppliernm,
        "supplier_cd":        suppliercd,

        # — Montos —
        "monto_colones":      row.get("amt"),
        "currency_type":      currencytype,
        "detalle":            row.get("detalle"),

        # — Fechas —
        "biddoc_start_dt":    biddocstart,
        "biddoc_end_dt":      biddocend,
        "openbid_dt":         openbiddt,
        "adj_firme_dt":       adjfirmedt,
        "vigencia_contrato":  vigencia,
        "unidad_vigencia":    unidadvig,

        # — Clasificación ETL —
        "es_medica":          row.get("es_medica", False),
        "categoria":          _safe_categoria(row),

        # — Raw —
        "raw_data":           rawdata,
    }


# ─────────────────────────────────────────────
# UPSERT LICITACIONES
# ─────────────────────────────────────────────

def upsert_licitaciones(rows: list[dict]):
    if not rows:
        return

    db_rows = [_filter_none(_to_db_row(row), _KEEP_FALSY) for row in rows]

    sin_key = [r for r in db_rows if not r.get("instcartelno")]
    if sin_key:
        logger.warning(f"[uploader] {len(sin_key)} rows sin instcartelno — descartadas")
        db_rows = [r for r in db_rows if r.get("instcartelno")]

    if not db_rows:
        logger.error("[uploader] 0 rows válidas — verificar parser output keys")
        return

    medicas = [r for r in db_rows if r.get("es_medica")]
    no_medicas = [
        {k: v for k, v in r.items() if k in _CAMPOS_BASE}
        for r in db_rows if not r.get("es_medica")
    ]

    client = get_supabase_client()
    total_confirmed = 0

    if medicas:
        medicas_u, dupes_m = _dedup(medicas, "instcartelno")
        if dupes_m:
            logger.info(f"[uploader] {dupes_m} duplicados removidos (médicas)")
        total_confirmed += _exec_upsert(client, medicas_u, "médicas (completo)")

    if no_medicas:
        no_medicas_u, dupes_nm = _dedup(no_medicas, "instcartelno")
        if dupes_nm:
            logger.info(f"[uploader] {dupes_nm} duplicados removidos (no-médicas)")
        total_confirmed += _exec_upsert(client, no_medicas_u, "no-médicas (parcial)")

    print(
        f"[uploader] {total_confirmed} confirmadas — "
        f"{len(medicas)} médicas + {len(no_medicas)} no-médicas enviadas"
    )


# ─────────────────────────────────────────────
# INSERT MODIFICACIONES
# ─────────────────────────────────────────────

def insert_modificaciones(rows: list[dict]):
    if not rows:
        return

    db_rows = []
    for row in rows:
        r = {
            "inst_cartel_no":  _f(row, "instcartelno",  "instCartelNo",  "inst_cartel_no"),
            "cartel_no":       _f(row, "cartelno",       "cartelNo",      "cartel_no"),
            "proce_type":      _f(row, "procetype",      "proceType",     "proce_type"),
            "inst_nm":         _f(row, "instnm",         "instNm",        "inst_nm"),
            "cartel_nm":       _f(row, "cartelnm",       "cartelNm",      "cartel_nm"),
            "inst_code":       row.get("inst_code"),
            "openbid_dt":      _f(row, "openbiddt",      "openbidDt",     "openbid_dt"),
            "biddoc_start_dt": _f(row, "biddocstartdt",  "biddocStartDt", "biddoc_start_dt"),
            "mod_reason":      _f(row, "modreason",      "modReason",     "mod_reason"),
            "es_medica":       row.get("es_medica", False),
            "categoria":       _safe_categoria(row),
            "raw_data":        _f(row, "rawdata", "raw_data"),
        }
        db_rows.append(_filter_none(r, {"es_medica"}))

    try:
        response = (
            get_supabase_client()
            .table("licitaciones_modificaciones")
            .insert(db_rows)
            .execute()
        )
        confirmed = len(response.data) if response.data is not None else 0
    except Exception as e:
        logger.error(
            f"[uploader] modificaciones: excepción en insert — {type(e).__name__}: {e}"
        )
        confirmed = 0

    if confirmed != len(db_rows):
        logger.error(
            f"[uploader] modificaciones: enviadas={len(db_rows)} confirmadas={confirmed}"
        )
    else:
        logger.info(f"[uploader] {confirmed} modificaciones insertadas")

    print(f"[uploader] {confirmed} modificaciones insertadas")
