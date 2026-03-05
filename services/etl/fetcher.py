# services/etl/fetcher.py
import httpx
import asyncio
import unicodedata
from datetime import datetime, timedelta


BASE_API = "https://prod-api.sicop.go.cr/bid/api/v1/public"

HEADERS = {
    "Origin": "https://www.sicop.go.cr",
    "Referer": "https://www.sicop.go.cr/",
    "Content-Type": "application/json",
    "Accept": "application/json"
}

ENDPOINTS = {
    "publicadas":  f"{BASE_API}/epCartelReleaseAdjuMod/listPageRelease",
    "adjudicadas": f"{BASE_API}/epCartelReleaseAdjuMod/listPageAwarded",
    "modificadas": f"{BASE_API}/epCartelReleaseAdjuMod/listPageModified"
}

TYPE_KEYS = {
    "publicadas":  "RPT_PUB",
    "adjudicadas": "RPT_ADJ",
    "modificadas": "RPT_MOD"
}

# ─────────────────────────────────────────────
# INSTITUCIONES TARGET — filtro post-fetch
# El API ignora instNm en formFilters — devuelve todo igual.
# Filtramos en Python después de traer todos los registros.
# ─────────────────────────────────────────────

INSTITUCIONES_TARGET = [
    "CAJA COSTARRICENSE DE SEGURO SOCIAL",
    "INSTITUTO NACIONAL DE SEGUROS",
    "MINISTERIO DE SALUD",
    "INSTITUTO COSTARRICENSE DE INVESTIGACION Y ENSENANZA EN NUTRICION Y SALUD",
    "UNIVERSIDAD DE COSTA RICA",
]


def _norm(texto: str) -> str:
    return unicodedata.normalize("NFD", texto.lower()).encode("ascii", "ignore").decode("ascii")


INSTITUCIONES_TARGET_NORM = [_norm(i) for i in INSTITUCIONES_TARGET]


def _es_institucion_target(inst_nm: str) -> bool:
    inst_norm = _norm(inst_nm or "")
    return any(target in inst_norm for target in INSTITUCIONES_TARGET_NORM)


# ─────────────────────────────────────────────
# PAYLOAD — sin instNm, el API lo ignora
# ─────────────────────────────────────────────

def build_payload(fecha_desde: datetime, fecha_hasta: datetime,
                  type_key: str, page: int = 0, page_size: int = 100) -> dict:
    return {
        "pageNumber": page,
        "pageSize": page_size,
        "tableSorter": {"sorter": "", "order": "desc"},
        "tableFilters": [],
        "formFilters": [
            {"field": "bgnYmd",  "value": fecha_desde.strftime("%Y-%m-%dT%H:%M:%S.000Z")},
            {"field": "endYmd",  "value": fecha_hasta.strftime("%Y-%m-%dT%H:%M:%S.000Z")},
            {"field": "typeKey", "value": type_key},
        ]
    }


async def post_with_retry(client: httpx.AsyncClient, url: str,
                          payload: dict, retries: int = 3) -> dict:
    """POST con reintentos y backoff exponencial."""
    for attempt in range(retries):
        try:
            r = await client.post(url, json=payload, headers=HEADERS)
            r.raise_for_status()
            return r.json()
        except (httpx.ConnectTimeout, httpx.ReadTimeout, httpx.HTTPStatusError) as e:
            if attempt == retries - 1:
                raise
            wait = 2 ** attempt
            print(f"[fetcher] Timeout en intento {attempt + 1}, reintentando en {wait}s...")
            await asyncio.sleep(wait)


async def fetch_all(tipo: str, fecha_desde: datetime, fecha_hasta: datetime) -> list[dict]:
    """1 fetch paginado de todo SICOP + filtro post-fetch por institución target."""
    endpoint  = ENDPOINTS[tipo]
    type_key  = TYPE_KEYS[tipo]
    all_items = []

    async with httpx.AsyncClient(timeout=45.0) as client:
        first = await post_with_retry(
            client, endpoint,
            build_payload(fecha_desde, fecha_hasta, type_key, 0)
        )
        all_items.extend(first["content"])
        total_pages = first["totalPages"]
        print(f"[fetcher:{tipo}] {first['totalElements']} registros / {total_pages} páginas")

        for page in range(1, total_pages):
            data = await post_with_retry(
                client, endpoint,
                build_payload(fecha_desde, fecha_hasta, type_key, page)
            )
            all_items.extend(data["content"])
            if page % 20 == 0:
                print(f"[fetcher:{tipo}] página {page}/{total_pages}")

    # Filtro post-fetch — solo instituciones target
    filtrados = [i for i in all_items if _es_institucion_target(i.get("instNm", ""))]
    print(f"[fetcher:{tipo}] {len(filtrados)} de {len(all_items)} son instituciones target")

    # Dedup por instCartelNo
    seen = {}
    for item in filtrados:
        key = item.get("instCartelNo")
        if key:
            seen[key] = item

    return list(seen.values())


async def fetch_sicop(dias_atras: int = 1) -> dict[str, list]:
    fecha_hasta = datetime.utcnow()
    fecha_desde = fecha_hasta - timedelta(days=dias_atras)

    publicadas  = await fetch_all("publicadas",  fecha_desde, fecha_hasta)
    adjudicadas = await fetch_all("adjudicadas", fecha_desde, fecha_hasta)
    modificadas = await fetch_all("modificadas", fecha_desde, fecha_hasta)

    print(f"[fetcher] ✓ {len(publicadas)} pub | {len(adjudicadas)} adj | {len(modificadas)} mod")
    return {
        "publicadas":  publicadas,
        "adjudicadas": adjudicadas,
        "modificadas": modificadas
    }
