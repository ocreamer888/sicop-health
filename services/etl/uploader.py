# services/etl/uploader.py
"""
SICOP Uploader
Escribe datos en Supabase. Schema v2 — campos snake_case alineados al API real.
El parser ya entrega los campos con nombres correctos, no se necesita remapeo.
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


def _safe_categoria(item: dict) -> str:
    cat = item.get("categoria")
    if not cat or cat.strip() == "":
        return "OTRO_MEDICO"
    return cat


def upsert_licitaciones(rows: list[dict]):
    """
    Upsert de publicadas y adjudicadas en licitaciones_medicas.
    Conflict key: inst_cartel_no (UNIQUE en schema v2).
    """
    if not rows:
        return

    seen = {}
    for row in rows:
        key = row.get("inst_cartel_no")
        if key:
            seen[key] = row
    unique_rows = list(seen.values())

    duplicados = len(rows) - len(unique_rows)
    if duplicados > 0:
        print(f"[uploader] {duplicados} duplicados removidos")

    get_supabase_client() \
        .table("licitaciones_medicas") \
        .upsert(unique_rows, on_conflict="inst_cartel_no") \
        .execute()

    print(f"[uploader] {len(unique_rows)} licitaciones upserted")


def insert_modificaciones(rows: list[dict]):
    """
    INSERT de modificaciones en licitaciones_modificaciones.
    Siempre INSERT — el mismo cartel puede tener N modificaciones.
    """
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
        "raw_data":         row.get("raw_data")
    } for row in rows]

    get_supabase_client() \
        .table("licitaciones_modificaciones") \
        .insert(db_rows) \
        .execute()

    print(f"[uploader] {len(db_rows)} modificaciones insertadas")
