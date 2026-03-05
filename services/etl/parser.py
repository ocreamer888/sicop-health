# services/etl/parser.py
"""
SICOP Data Parser v2.1
Fixes:
- Captura campos faltantes: unspsc_cd, supplier_cd, modalidad, excepcion_cd,
  biddoc_end_dt, adj_firme_dt, vigencia_contrato
- Extrae tipo_procedimiento del inst_cartel_no como campo explícito
- _extract_monto_detalle: regex ampliado para formatos CR reales
- Fix: monto/currency colisión con falsy 0.0 y ""
- _clean_dataframe: procesa clasificacion_unspsc del CSV legacy
"""

import logging
import re
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────
# TIPO PROCEDIMIENTO — inferido del inst_cartel_no
# ─────────────────────────────────────────────

_TIPO_PROC_RE = re.compile(r'^\d{4}([A-Z]{2})-')

TIPO_PROCEDIMIENTO_LABELS = {
    "LD": "Licitación Directa",
    "LY": "Licitación Mayor",
    "LE": "Licitación Especial",
    "XE": "Contratación Excepción",
    "PX": "Procedimiento Menor",
    "PE": "Procedimiento Especial",
}


def _extract_tipo_procedimiento(inst_cartel_no: str | None) -> str | None:
    """Extrae el código de tipo de procedimiento del inst_cartel_no."""
    if not inst_cartel_no:
        return None
    m = _TIPO_PROC_RE.match(inst_cartel_no)
    return m.group(1) if m else None


# ─────────────────────────────────────────────
# MONTO — parser robusto para formatos CR
# ─────────────────────────────────────────────

# Cubre variaciones reales observadas en SICOP:
# "monto de USD 9,792.00"
# "monto de CRC 1.577.215,92"   ← puntos como miles, coma decimal (formato CR)
# "USD135.00"                    ← sin espacio
# "por ₡290,000,000"             ← símbolo colón
# "$95,500"                      ← símbolo dólar
_MONTO_PATTERN = re.compile(
    r'(?:'
    r'monto\s+(?:de\s+|total[:\s]+)?'   # "monto de", "monto total:"
    r'|por\s+(?:un\s+monto\s+(?:de\s+)?)?'  # "por un monto de"
    r')?'
    r'(?P<currency>USD|CRC|EUR|₡|\$|¢)'
    r'\s*'
    r'(?P<amount>[\d.,]+)',
    re.IGNORECASE
)

_CURRENCY_MAP = {
    '₡': 'CRC',
    '¢': 'CRC',
    '$': 'USD',
    'USD': 'USD',
    'CRC': 'CRC',
    'EUR': 'EUR',
}


def _parse_amount_str(amount_str: str, currency: str) -> float | None:
    """
    Parsea un string de monto considerando formato CR vs internacional.
    CR: 1.577.215,92  →  puntos=miles, coma=decimal
    INT: 9,792.00     →  comas=miles, punto=decimal
    """
    s = amount_str.strip()
    # Detectar formato CR: termina en ,XX con 2 dígitos → coma es decimal
    if re.search(r',\d{2}$', s) and '.' in s:
        # Formato CR: 1.577.215,92 → eliminar puntos, coma→punto
        s = s.replace('.', '').replace(',', '.')
    elif re.search(r'\.\d{2}$', s) and ',' in s:
        # Formato INT: 9,792.00 → eliminar comas
        s = s.replace(',', '')
    else:
        # Sin ambigüedad: eliminar separadores de miles comunes
        s = s.replace(',', '').replace('.', '') if s.count('.') > 1 or s.count(',') > 1 \
            else s.replace(',', '')
    try:
        return float(s)
    except ValueError:
        return None


def _extract_monto_detalle(detalle: str | None) -> tuple[float | None, str | None]:
    """
    Extrae monto y moneda del campo 'detalle'.
    Maneja formatos CR e internacionales. Retorna (monto, currency) o (None, None).
    """
    if not detalle:
        return None, None

    # Buscar todos los matches, tomar el de mayor monto (el principal)
    best_monto = None
    best_currency = None

    for match in _MONTO_PATTERN.finditer(detalle):
        currency_raw = match.group('currency').upper()
        currency = _CURRENCY_MAP.get(currency_raw, currency_raw)
        monto = _parse_amount_str(match.group('amount'), currency)
        if monto is not None:
            if best_monto is None or monto > best_monto:
                best_monto = monto
                best_currency = currency

    return best_monto, best_currency


# ─────────────────────────────────────────────
# API REST Parser (schema v2.1)
# ─────────────────────────────────────────────

def parse_item(item: dict, type_key: str) -> dict:
    """
    Normaliza un item del API REST al schema v2.1 de Supabase.
    """
    monto_detalle, currency_detalle = _extract_monto_detalle(item.get("detalle"))

    # Fix: usar `is not None` para evitar colisión con valores falsy (0.0, "")
    amt_raw = item.get("amt")
    currency_raw = item.get("currencyType")

    inst_cartel_no = item.get("instCartelNo")

    return {
        # — Identificadores —
        "inst_cartel_no":     inst_cartel_no,
        "cartel_no":          item.get("cartelNo"),

        # — Procedimiento —
        "proce_type":         item.get("proceType"),
        "tipo_procedimiento": _extract_tipo_procedimiento(inst_cartel_no),  # v2.1: explícito
        "modalidad":          item.get("modalidad"),       # v2.1: licitación pública/directa
        "excepcion_cd":       item.get("excepcionCd"),     # v2.1: Art. 55/60/66 LGCP

        # — Institución y descripción —
        "inst_nm":            item.get("instNm"),
        "cartel_nm":          item.get("cartelNm"),
        "cartel_cate":        item.get("cartelCate"),

        # — Clasificación UNSPSC — v2.1: señal primaria para classifier
        "unspsc_cd":          item.get("unspscCd"),        # v2.1: 8 dígitos familia UNSPSC

        # — Fechas —
        "biddoc_start_dt":    item.get("biddocStartDt"),   # fecha publicación
        "biddoc_end_dt":      item.get("biddocEndDt"),     # v2.1: deadline ofertas
        "openbid_dt":         item.get("openbidDt"),       # fecha apertura
        "adj_firme_dt":       item.get("adjFirmeDt"),      # v2.1: firmeza adjudicación

        # — Proveedor —
        "supplier_nm":        item.get("supplierNm"),
        "supplier_cd":        item.get("supplierCd"),      # v2.1: cédula proveedor

        # — Montos: detalle tiene precedencia, API como fallback —
        # Fix v2.1: `is not None` evita que 0.0 y "" sean falsy
        "currency_type":      currency_detalle if currency_detalle is not None else currency_raw,
        "amt":                monto_detalle if monto_detalle is not None else amt_raw,

        # — Vigencia contrato —
        "vigencia_contrato":  item.get("vigenciaContrato"),  # v2.1
        "unidad_vigencia":    item.get("unidadVigencia"),    # v2.1: años/meses

        # — Campos de control —
        "detalle":            item.get("detalle"),
        "mod_reason":         item.get("modReason"),
        "type_key":           type_key,
        "es_medica":          False,  # classifier.py sobreescribe
        "raw_data":           item,
    }


def parse_batch(items: list[dict], type_key: str) -> list[dict]:
    """
    Parsea un lote de items del API REST de SICOP.

    Args:
        items:    Lista de items crudos del API (content[] del response)
        type_key: RPT_PUB | RPT_ADJ | RPT_MOD

    Returns:
        Lista de dicts listos para upsert en Supabase (schema v2.1)
    """
    if not items:
        return []
    result = [parse_item(i, type_key) for i in items]
    logger.info(f"[parser] {len(result)} items parseados — type_key: {type_key}")
    return result


# ─────────────────────────────────────────────
# CSV Parser (legacy — fallback)
# ─────────────────────────────────────────────

COLUMNAS_SICOP_CSV = [
    "numero_procedimiento",
    "descripcion",
    "institucion",
    "tipo_procedimiento",
    "clasificacion_unspsc",   # mapea a unspsc_cd en schema v2.1
    "monto_colones",
    "adjudicatario",
    "estado",
    "fecha_tramite",
    "fecha_limite_oferta",
]

_DATE_COLS_CSV = [
    "fecha_tramite",
    "fecha_limite_oferta",
    "fecha_publicacion",
    "fecha_cierre_recepcion",
    "fecha_apertura",
]


def parse_csv(csv_path: "Path") -> "pd.DataFrame | None":
    """
    Parsea el CSV del portal viejo de SICOP.
    Fallback al pipeline REST principal.
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
    name = str(name).strip().lower()
    name = re.sub(r"[^\w\s]", "", name)
    name = re.sub(r"\s+", "_", name)
    return name


def _clean_dataframe(df: "pd.DataFrame") -> "pd.DataFrame":
    df = df.dropna(how="all")

    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = df[col].astype(str).str.strip()
        df[col] = df[col].replace(["nan", "None", "null", ""], None)

    for col in _DATE_COLS_CSV:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce", dayfirst=True)

    if "monto_colones" in df.columns:
        df["monto_colones"] = df["monto_colones"].apply(_parse_monto_csv)

    # v2.1: normalizar clasificacion_unspsc al nombre del schema REST
    if "clasificacion_unspsc" in df.columns:
        df = df.rename(columns={"clasificacion_unspsc": "unspsc_cd"})

    if "numero_procedimiento" in df.columns:
        df["numero_procedimiento"] = df["numero_procedimiento"].astype(str).str.strip()
        df = df[df["numero_procedimiento"].notna()]
        df = df[df["numero_procedimiento"] != ""]

    return df


def _parse_monto_csv(value) -> "float | None":
    """Parsea montos en colones del CSV (formato CR: puntos como miles)."""
    if pd.isna(value) or value is None:
        return None
    try:
        if isinstance(value, (int, float)):
            return float(value)
        # Formato CR: ₡1.577.215,92 → eliminar símbolo y espacios, luego aplicar lógica CR
        monto_str = re.sub(r"[₡\s¢]", "", str(value))
        return _parse_amount_str(monto_str, "CRC")
    except (ValueError, TypeError):
        return None
