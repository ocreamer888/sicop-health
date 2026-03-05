# services/etl/fetcher.py
import httpx
import asyncio
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


def build_payload(fecha_desde: datetime, fecha_hasta: datetime,
                  type_key: str, page: int = 0, page_size: int = 100) -> dict:
    return {
        "pageNumber": page,
        "pageSize": page_size,
        "tableSorter": {"sorter": "", "order": "desc"},
        "tableFilters": [],
        "formFilters": [
            {"field": "bgnYmd", "value": fecha_desde.strftime("%Y-%m-%dT%H:%M:%S.000Z")},
            {"field": "endYmd", "value": fecha_hasta.strftime("%Y-%m-%dT%H:%M:%S.000Z")},
            {"field": "typeKey", "value": type_key}
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
            wait = 2 ** attempt  # 1s, 2s, 4s
            print(f"[fetcher] Timeout en intento {attempt + 1}, reintentando en {wait}s...")
            await asyncio.sleep(wait)


async def fetch_all(tipo: str, fecha_desde: datetime, fecha_hasta: datetime) -> list[dict]:
    endpoint = ENDPOINTS[tipo]
    type_key  = TYPE_KEYS[tipo]
    all_items = []

    async with httpx.AsyncClient(timeout=45.0) as client:  # timeout aumentado a 45s
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
                print(f"[fetcher:{tipo}] {page}/{total_pages}")

    return all_items


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
