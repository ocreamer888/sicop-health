#!/usr/bin/env python3
"""
Intenta encontrar endpoints adicionales de SICOP para estado de licitaciones electrónicas.
"""

import httpx
import asyncio

BASE_API = "https://prod-api.sicop.go.cr/bid/api/v1/public"

# Posibles endpoints relacionados con electronic contests
POSSIBLE_ENDPOINTS = [
    f"{BASE_API}/epCartelReleaseAdjuMod/listPageElectronicContests",
    f"{BASE_API}/epCartelReleaseAdjuMod/listPageBidStatus",
    f"{BASE_API}/epCartelBid/listPage",
    f"{BASE_API}/epCartelBid/list",
    f"{BASE_API}/bid/api/v1/public/epCartelBid/listPage",
    f"{BASE_API}/bid/api/v1/epCartelBid/listPage",
    "https://prod-api.sicop.go.cr/bid/api/v1/epCartelBid/listPage",
]

HEADERS = {
    "Origin": "https://www.sicop.go.cr",
    "Referer": "https://www.sicop.go.cr/",
    "Content-Type": "application/json",
    "Accept": "application/json"
}


async def test_endpoint(url: str):
    """Test if an endpoint exists."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Try with a simple POST (most SICOP endpoints use POST)
            payload = {
                "pageNumber": 0,
                "pageSize": 1,
                "tableSorter": {"sorter": "", "order": "desc"},
                "tableFilters": [],
                "formFilters": [
                    {"field": "bgnYmd", "value": "2026-03-01T00:00:00.000Z"},
                    {"field": "endYmd", "value": "2026-03-07T00:00:00.000Z"},
                ]
            }

            r = await client.post(url, json=payload, headers=HEADERS)

            if r.status_code == 200:
                data = r.json()
                if "content" in data:
                    print(f"✅ {url}")
                    print(f"   Found {len(data.get('content', []))} records")
                    if data.get("content"):
                        keys = list(data["content"][0].keys())
                        print(f"   Fields: {keys[:5]}...")
                    return True
            elif r.status_code == 404:
                print(f"❌ {url} - Not Found (404)")
            else:
                print(f"⚠️  {url} - Status {r.status_code}")

    except Exception as e:
        print(f"💥 {url} - Error: {e}")

    return False


async def main():
    print("🔍 Buscando endpoints adicionales de SICOP...\n")

    found = []
    for endpoint in POSSIBLE_ENDPOINTS:
        if await test_endpoint(endpoint):
            found.append(endpoint)

    print(f"\n{'='*60}")
    if found:
        print(f"✅ Endpoints encontrados: {len(found)}")
        for f in found:
            print(f"   - {f}")
    else:
        print("❌ No se encontraron endpoints adicionales")
        print("\n💡 Sugerencia: El estado electrónico puede estar:")
        print("   1. En una API interna/autenticada")
        print("   2. En un sistema separado de licitaciones electrónicas")
        print("   3. Solo disponible mediante scraping de la página web")


if __name__ == "__main__":
    asyncio.run(main())
