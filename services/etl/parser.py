# services/etl/parser.py
"""
SICOP Data Parser

Normaliza datos del API REST de SICOP (prod-api.sicop.go.cr).
Schema target: v2 con campos snake_case alineados al JSON real del API.
"""

import logging
import re
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

# ============================================
# API REST Parser (schema v2)
# ============================================

MONTO_DETALLE_PATTERN = re.compile(
    r'monto de\s+(USD|CRC|EUR)\s+([\d,\.]+)',
    re.IGNORECASE
)


def _extract_monto_detalle(detalle: str | None) -> tuple[float | None, str | None]:
    """
    Extrae monto y moneda del campo 'detalle' de licitaciones adjudicadas.
    Ej: "Se adjudica LMG LANCO MEDICAL GROUP por un monto de USD 9792"
    """
    if not detalle:
        return None, None
    match = MONTO_DETALLE_PATTERN.search(detalle)
    if not match:
        return None, None
    currency = match.group(1).upper()
    try:
        monto = float(match.group(2).replace(",", ""))
    except ValueError:
        return None, None
    return monto, currency


def parse_item(item: dict, type_key: str) -> dict:
    """
    Normaliza un item del API REST al schema v2 de Supabase.
    Mapeo directo camelCase → snake_case según response real confirmado.
    """
    monto, currency = _extract_monto_detalle(item.get("detalle"))
    return {
        "inst_cartel_no":   item.get("instCartelNo"),   # ID único — UNIQUE KEY
        "cartel_no":        item.get("cartelNo"),
        "proce_type":       item.get("proceType"),
        "inst_nm":          item.get("instNm"),
        "cartel_nm":        item.get("cartelNm"),
        "openbid_dt":       item.get("openbidDt"),
        "biddoc_start_dt":  item.get("biddocStartDt"),
        "supplier_nm":      item.get("supplierNm"),
        "currency_type":    currency or item.get("currencyType"),
        "amt":              monto or item.get("amt"),
        "detalle":          item.get("detalle"),
        "mod_reason":       item.get("modReason"),
        "cartel_cate":      item.get("cartelCate"),
        "type_key":         type_key,
        "es_medica":        False,   # classifier.py lo sobreescribe
        "raw_data":         item
    }


def parse_batch(items: list[dict], type_key: str) -> list[dict]:
    """
    Parsea un lote de items del API REST de SICOP.

    Args:
        items:    Lista de items crudos del API (content[] del response)
        type_key: RPT_PUB | RPT_ADJ | RPT_MOD

    Returns:
        Lista de dicts listos para upsert en Supabase (schema v2)
    """
    if not items:
        return []
    result = [parse_item(i, type_key) for i in items]
    logger.info(f"[parser] {len(result)} items parseados — type_key: {type_key}")
    return result


# ============================================
# CSV Parser (legacy — por si se necesita)
# ============================================

COLUMNAS_SICOP_CSV = [
    "numero_procedimiento",
    "descripcion",
    "institucion",
    "tipo_procedimiento",
    "clasificacion_unspsc",
    "monto_colones",
    "adjudicatario",
    "estado",
    "fecha_tramite",
    "fecha_limite_oferta",
]


def parse_csv(csv_path: "Path") -> "pd.DataFrame | None":
    """
    Parsea y normaliza el CSV del portal viejo de SICOP.
    Mantenido como fallback — el pipeline principal usa parse_batch().
    """
    try:
        logger.info(f"Parseando CSV: {csv_path}")

        import chardet
        with open(csv_path, "rb") as f:
            encoding = chardet.detect(f.read()).get("encoding", "utf-8")
        logger.info(f"Encoding detectado: {encoding}")

        df = pd.read_csv(
            csv_path,
            encoding=encoding,
            sep=None,
            engine="python",
            skipinitialspace=True,
            on_bad_lines="skip",
            quoting=3,
        )

        logger.info(f"Columnas detectadas: {list(df.columns)}")
        df.columns = [_normalize_col(col) for col in df.columns]
        df = _clean_dataframe(df)
        logger.info(f"Registros limpios: {len(df)}")
        return df

    except Exception as e:
        logger.exception(f"Error parseando CSV: {e}")
        return None


def _normalize_col(name: str) -> str:
    """snake_case normalizer para columnas del CSV."""
    name = str(name).strip().lower()
    name = re.sub(r"[^\w\s]", "", name)
    name = re.sub(r"\s+", "_", name)
    return name


def _clean_dataframe(df: "pd.DataFrame") -> "pd.DataFrame":
    """Limpia y normaliza el DataFrame del CSV."""
    df = df.dropna(how="all")

    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = df[col].astype(str).str.strip()
        df[col] = df[col].replace(["nan", "None", "null", ""], None)

    for col in ["fecha_tramite", "fecha_limite_oferta", "fecha_publicacion"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce", dayfirst=True)

    if "monto_colones" in df.columns:
        df["monto_colones"] = df["monto_colones"].apply(_parse_monto_csv)

    if "numero_procedimiento" in df.columns:
        df["numero_procedimiento"] = df["numero_procedimiento"].astype(str).str.strip()
        df = df[df["numero_procedimiento"].notna()]
        df = df[df["numero_procedimiento"] != ""]

    return df


def _parse_monto_csv(value) -> "float | None":
    """Parsea montos en colones del CSV (formato CR con puntos como separador de miles)."""
    if pd.isna(value) or value is None:
        return None
    try:
        if isinstance(value, (int, float)):
            return float(value)
        monto_str = re.sub(r"[₡\s,]", "", str(value)).replace(".", "")
        return float(monto_str) if monto_str else None
    except (ValueError, TypeError):
        return None
