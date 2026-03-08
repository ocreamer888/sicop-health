#!/usr/bin/env python3
"""
Script para explorar la API real de SICOP y ver todos los campos disponibles.
Esto nos ayuda a identificar qué datos adicionales podemos extraer.
"""

import httpx
import asyncio
import json
from datetime import datetime, timedelta

BASE_API = "https://prod-api.sicop.go.cr/bid/api/v1/public"

ENDPOINTS = {
    "publicadas":  f"{BASE_API}/epCartelReleaseAdjuMod/listPageRelease",
    "adjudicadas": f"{BASE_API}/epCartelReleaseAdjuMod/listPageAwarded",
    "modificadas": f"{BASE_API}/epCartelReleaseAdjuMod/listPageModified"
}

HEADERS = {
    "Origin": "https://www.sicop.go.cr",
    "Referer": "https://www.sicop.go.cr/",
    "Content-Type": "application/json",
    "Accept": "application/json"
}


def build_payload(fecha_desde: datetime, fecha_hasta: datetime,
                  type_key: str, page: int = 0, page_size: int = 10) -> dict:
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


async def fetch_sample(tipo: str, dias_atras: int = 7):
    """Fetch a sample of records from SICOP API to analyze fields."""
    endpoint = ENDPOINTS[tipo]
    type_key = {"publicadas": "RPT_PUB", "adjudicadas": "RPT_ADJ", "modificadas": "RPT_MOD"}[tipo]

    fecha_hasta = datetime.utcnow()
    fecha_desde = fecha_hasta - timedelta(days=dias_atras)

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            r = await client.post(
                endpoint,
                json=build_payload(fecha_desde, fecha_hasta, type_key, 0, 10),
                headers=HEADERS
            )
            r.raise_for_status()
            data = r.json()

            if not data.get("content"):
                print(f"[ {tipo} ] No records found")
                return

            # Get all unique keys from all records
            all_keys = set()
            for item in data["content"][:5]:  # Analyze first 5
                all_keys.update(item.keys())

            print(f"\n{'='*60}")
            print(f"TIPO: {tipo.upper()} ({len(data['content'])} records found)")
            print(f"{'='*60}")

            # Show one complete record as example
            if data["content"]:
                print("\n📋 Ejemplo de registro completo:")
                print(json.dumps(data["content"][0], indent=2, ensure_ascii=False))

            # Show all available fields
            print(f"\n🔑 Campos disponibles ({len(all_keys)}):")
            for key in sorted(all_keys):
                print(f"  - {key}")

            return data

        except Exception as e:
            print(f"[ {tipo} ] Error: {e}")
            return None


async def check_electronic_bid_fields():
    """Check if there are electronic bid status fields in the API."""
    print("\n" + "="*60)
    print("BUSCANDO CAMPOS DE 'ELECTRONIC CONTESTS STATUS'")
    print("="*60)

    for tipo in ["publicadas", "adjudicadas"]:
        data = await fetch_sample(tipo, dias_atras=30)
        if data and data.get("content"):
            # Look for electronic bid related fields
            electronic_fields = []
            for item in data["content"]:
                for key in item.keys():
                    if any(term in key.lower() for term in [
                        "elec", "bid", "stat", "cnt", "join", "open", "close"
                    ]):
                        if key not in electronic_fields:
                            electronic_fields.append(key)

            if electronic_fields:
                print(f"\n⚡ Campos electrónicos encontrados en {tipo}:")
                for f in electronic_fields:
                    print(f"  - {f}")
            else:
                print(f"\n⚠️  No se encontraron campos electrónicos específicos en {tipo}")


async def main():
    print("🚀 Explorando API de SICOP...")
    print("Base URL:", BASE_API)

    # Fetch samples from each endpoint
    for tipo in ["publicadas", "adjudicadas", "modificadas"]:
        await fetch_sample(tipo)

    # Check for electronic bid fields
    await check_electronic_bid_fields()

    print("\n" + "="*60)
    print("EXPLORACIÓN COMPLETA")
    print("="*60)
    print("\n💡 Nota: Si necesitas datos de la página web")
    print("   https://www.sicop.go.cr/app/module/bid/public/electronic-contests-status")
    print("   que NO están en la API, necesitaríamos crear un scraper con Playwright.")


if __name__ == "__main__":
    asyncio.run(main())
