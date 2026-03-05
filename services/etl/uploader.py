# services/etl/uploader.py
"""
SICOP Uploader v2.3
Schema v2.1 — mapeo parser → DB con dedup y DO UPDATE SET explícito.
Fix v2.3: agrega es_medica al mapeo (_to_db_row).
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


def _to_db_row(row: dict) -> dict:
    """Mapea campos del parser al schema v2.1 de licitaciones_medicas."""
    return {
        # Core
        "numero_procedimiento": row.get("inst_cartel_no"),
        "descripcion":          row.get("cartel_nm"),
        "institucion":          row.get("inst_nm"),
        "estado":               ESTADO_MAP.get(row.get("type_key")),

        # Procedimiento
        "tipo_procedimiento":   row.get("tipo_procedimiento") or row.get("proce_type"),
        "modalidad":            row.get("modalidad"),
        "excepcion_cd":         row.get("excepcion_cd"),
        "cartel_cate":          row.get("cartel_cate"),

        # UNSPSC
        "unspsc_cd":            row.get("unspsc_cd"),
        "clasificacion_unspsc": row.get("unspsc_cd"),  # alias para vista legacy

        # Proveedor
        "adjudicatario":        row.get("supplier_nm"),
        "supplier_cd":          row.get("supplier_cd"),

        # Montos
        "monto_colones":        row.get("amt"),

        # Fechas
        "fecha_tramite":        row.get("biddoc_start_dt"),
        "fecha_limite_oferta":  row.get("biddoc_end_dt"),   # para vista licitaciones_por_vencer
        "biddoc_end_dt":        row.get("biddoc_end_dt"),   # campo real v2.1
        "adj_firme_dt":         row.get("adj_firme_dt"),

        # Contrato
        "vigencia_contrato":    row.get("vigencia_contrato"),
        "unidad_vigencia":      row.get("unidad_vigencia"),

        # Clasificación médica — v2.3: es_medica ahora incluido
        "es_medica":            row.get("es_medica", False),
        "categoria":            _safe_categoria(row),

        # Raw
        "raw_data":             row.get("raw_data"),
    }


def _dedup(rows: list[dict], key: str) -> tuple[list[dict], int]:
    """Deduplica por key, quedándose con el último. Retorna (unique_rows, n_dupes)."""
    seen = {}
    for row in rows:
        k = row.get(key)
        if k:
            seen[k] = row
    unique = list(seen.values())
    return unique, len(rows) - len(unique)


def upsert_licitaciones(rows: list[dict]):
    if not rows:
        return

    db_rows = []
    for row in rows:
        mapped = _to_db_row(row)
        # es_medica es booleano — False es un valor válido, no filtrar con "if v is not None"
        filtered = {
            k: v for k, v in mapped.items()
            if v is not None or k == "es_medica"
        }
        db_rows.append(filtered)

    unique_rows, dupes = _dedup(db_rows, "numero_procedimiento")
    if dupes > 0:
        logger.info(f"[uploader] {dupes} duplicados removidos")

    get_supabase_client() \
        .table("licitaciones_medicas") \
        .upsert(unique_rows, on_conflict="numero_procedimiento", ignore_duplicates=False) \
        .execute()

    logger.info(f"[uploader] {len(unique_rows)} licitaciones upserted")
    print(f"[uploader] {len(unique_rows)} licitaciones upserted")


def insert_modificaciones(rows: list[dict]):
    if not rows:
        return

    db_rows = [{
        "inst_cartel_no":   row.get("inst_cartel_no"),
        "cartel_no":        row.get("cartel_no"),
        "proce_type":       row.get("proce_type"),
        "inst_nm":          row.get("inst_nm"),
        "cartel_nm":        row.get("cartel_nm"),
        "openbid_dt":       row.get("openbid_dt"),
        "biddoc_start_dt":  row.get("biddoc_start_dt"),
        "mod_reason":       row.get("mod_reason"),
        "raw_data":         row.get("raw_data"),
    } for row in rows]

    db_rows = [{k: v for k, v in r.items() if v is not None} for r in db_rows]

    get_supabase_client() \
        .table("licitaciones_modificaciones") \
        .insert(db_rows) \
        .execute()

    logger.info(f"[uploader] {len(db_rows)} modificaciones insertadas")
    print(f"[uploader] {len(db_rows)} modificaciones insertadas")
