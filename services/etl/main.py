# services/etl/main.py — v2.4
"""
v2.4 fixes:
- enrich_batch: no-médicas se pasan a upsert_licitaciones igual que médicas
  (el uploader v2.5 hace upsert parcial para no-médicas — no toca categoria/es_medica)
- Elimina el append de no-médicas con es_medica=False/categoria=None al all_items_raw
  para que el catalog solo refleje instituciones con licitaciones médicas reales
"""
import asyncio
import logging
import os
import re
from dotenv import load_dotenv

load_dotenv()

from fetcher import fetch_sicop
from parser import parse_batch
from classifier import clasificar
from uploader import upsert_licitaciones, insert_modificaciones

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger("main")


# ── Extracción de institution_code ───────────────────────────────────────────
_INST_CODE_RE = re.compile(r"\d+[A-Z]{2}-\d+-(\d+)")


def extract_inst_code(inst_cartel_no: str) -> str | None:
    m = _INST_CODE_RE.match(inst_cartel_no or "")
    return m.group(1) if m else None


def _get_instcartelno(item: dict) -> str:
    return (
        item.get("instcartelno") or
        item.get("instCartelNo") or
        item.get("inst_cartel_no") or
        ""
    )


def _get_instnm(item: dict) -> str:
    return (
        item.get("instnm") or
        item.get("instNm") or
        item.get("inst_nm") or
        ""
    )


# ── Catálogo de instituciones activas ────────────────────────────────────────
def build_institution_catalog(all_items: list[dict]) -> dict[str, str]:
    catalog: dict[str, str] = {}
    for item in all_items:
        code = item.get("inst_code") or extract_inst_code(_get_instcartelno(item))
        name = _get_instnm(item)
        if code and name:
            catalog[code] = name
    return catalog


# ── Enriquecer + clasificar ───────────────────────────────────────────────────
def enrich_batch(parsed: list[dict]) -> tuple[list[dict], list[dict], int]:
    """
    Retorna (medicas, no_medicas, count_medicas).
    Separados para que upsert_licitaciones aplique estrategia distinta a cada grupo.
    """
    medicas: list[dict]    = []
    no_medicas: list[dict] = []

    for p in parsed:
        p["inst_code"] = extract_inst_code(_get_instcartelno(p))
        resultado = clasificar(p)
        if resultado:
            medicas.append(resultado)
        else:
            # Marca explícita para que uploader haga upsert parcial
            # (no sobreescribe categoria/es_medica de clasificaciones previas)
            no_medicas.append({**p, "es_medica": False, "categoria": None})

    return medicas, no_medicas, len(medicas)


# ── Runner principal ──────────────────────────────────────────────────────────
async def run(dias_atras: int = 90) -> None:
    logger.info("=== SICOP ETL — Iniciando (dias_atras=%d) ===", dias_atras)

    data = await fetch_sicop(dias_atras=dias_atras)

    # Solo médicas van al catalog — no-médicas no aportan signal útil
    all_medicas_raw: list[dict] = []
    stats: dict[str, dict] = {}

    # ── Publicadas + Adjudicadas ──────────────────────────────────────────────
    for tipo, type_key in [("publicadas", "RPT_PUB"), ("adjudicadas", "RPT_ADJ")]:
        raw = data[tipo]
        parsed = parse_batch(raw, type_key)
        medicas, no_medicas, n_medicas = enrich_batch(parsed)

        # Upsert completo para médicas, parcial para no-médicas
        upsert_licitaciones(medicas + no_medicas)

        stats[tipo] = {"total": len(parsed), "medicas": n_medicas}
        logger.info(
            "[%s] %d médicas de %d totales (%.0f%%)",
            tipo,
            n_medicas,
            len(parsed),
            (n_medicas / len(parsed) * 100) if parsed else 0,
        )
        all_medicas_raw.extend(medicas)

    # ── Modificadas — solo médicas ────────────────────────────────────────────
    mod_parsed = parse_batch(data["modificadas"], "RPT_MOD")
    mod_medicas = []
    for p in mod_parsed:
        p["inst_code"] = extract_inst_code(_get_instcartelno(p))
        resultado = clasificar(p)
        if resultado:
            mod_medicas.append(resultado)

    insert_modificaciones(mod_medicas)
    logger.info(
        "[modificadas] %d médicas insertadas de %d totales",
        len(mod_medicas),
        len(mod_parsed),
    )

    # ── Institution catalog ───────────────────────────────────────────────────
    catalog = build_institution_catalog(all_medicas_raw)
    logger.info("[catalog] %d institution_codes únicos detectados este run", len(catalog))
    if os.getenv("LOG_LEVEL") == "DEBUG":
        for code, name in sorted(catalog.items()):
            logger.debug("  %s → %s", code, name)

    # ── Resumen final ─────────────────────────────────────────────────────────
    total_medicas    = sum(s["medicas"] for s in stats.values()) + len(mod_medicas)
    total_procesados = sum(s["total"]   for s in stats.values()) + len(mod_parsed)
    logger.info(
        "=== ETL Completado — %d médicas de %d procesados (%.0f%%) ===",
        total_medicas,
        total_procesados,
        (total_medicas / total_procesados * 100) if total_procesados else 0,
    )


# ── Entrypoints ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    dias = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    asyncio.run(run(dias_atras=dias))
