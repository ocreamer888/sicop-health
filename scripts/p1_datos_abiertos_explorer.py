#!/usr/bin/env python3
"""
P1: Datos Abiertos Validation & UNSPSC Line-Item Discovery
Tests JSP endpoints for structured data downloads and inspects for:
1. Proveedores catalog (cédula jurídica → nombre canonical)
2. Detalle pliego JSON (line-item level UNSPSC codes)
3. Contratos/Órdenes structured data

References:
- docs/SICOP_API_Reference_v3.md Section 17 (Endpoints Still to Map)
- JSP Module: /moduloPcont/pcont/rp/CE_MOD_DATOSABIERTOSVIEW.jsp
"""

import httpx
import asyncio
import json
from datetime import datetime, timedelta
from pathlib import Path

# JSP Base URL (legacy Java layer)
JSP_BASE = "https://www.sicop.go.cr/moduloPcont/pcont/rp"

# REST API for comparison
REST_BASE = "https://prod-api.sicop.go.cr"

OUTPUT_DIR = Path(__file__).parent / "p1_output"
OUTPUT_DIR.mkdir(exist_ok=True)


async def test_datos_abiertos_jsp(client: httpx.AsyncClient):
    """
    Test the datos abiertos JSP endpoint for structured downloads.
    This is the legacy Java module that exports:
    - Detalle pliego de condiciones
    - Contratos
    - Órdenes de pedido
    - Proveedores catalog
    """
    print("\n" + "="*70)
    print("📊 P1.1: Testing Datos Abiertos JSP Endpoint")
    print("="*70)

    jsp_url = f"{JSP_BASE}/CE_MOD_DATOSABIERTOSVIEW.jsp"

    # Common form params based on JSP form structure
    form_params = {
        "codigoInstitucion": "0031700001",  # CCSS main
        "tipoProcedimiento": "LD",          # Licitación Directa
        "fechaDesde": "20260101",
        "fechaHasta": "20260307",
        "tipoReporte": "DETALLE_PLIEGO",    # Or CONTRATOS, ORDENES, PROVEEDORES
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Origin": "https://www.sicop.go.cr",
        "Referer": "https://www.sicop.go.cr/",
    }

    try:
        print(f"\n🌐 Testing: {jsp_url}")
        print(f"📋 Form params: {json.dumps(form_params, indent=2)}")

        # Try POST (form submission)
        r = await client.post(
            jsp_url,
            data=form_params,
            headers=headers,
            timeout=30.0,
            follow_redirects=True
        )

        print(f"📡 Status: {r.status_code}")
        print(f"📄 Content-Type: {r.headers.get('content-type', 'unknown')}")
        print(f"📏 Content-Length: {len(r.text)} chars")

        # Check what we got back
        if "application/json" in r.headers.get("content-type", ""):
            print("✅ JSON response detected!")
            data = r.json()
            output_file = OUTPUT_DIR / "datos_abiertos_detalle_pliego.json"
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"💾 Saved to: {output_file}")

            # Inspect for UNSPSC
            if isinstance(data, list) and len(data) > 0:
                first_item = data[0]
                print(f"\n🔍 First item keys: {list(first_item.keys())}")
                if "unspsc" in str(first_item).lower() or "codigoclasificacion" in str(first_item).lower():
                    print("🎯 UNSPSC codes found in response!")
                return data

        elif "text/html" in r.headers.get("content-type", ""):
            print("⚠️  HTML response (JSP form page, not export)")
            # Check if there's a download link or form
            if "export" in r.text.lower() or "json" in r.text.lower():
                print("💡 Export functionality detected in page")
            # Save snippet for inspection
            snippet_file = OUTPUT_DIR / "datos_abiertos_response.html"
            with open(snippet_file, "w", encoding="utf-8") as f:
                f.write(r.text[:5000])  # First 5000 chars
            print(f"💾 HTML snippet saved to: {snippet_file}")

        else:
            print(f"⚠️  Unexpected content type")
            # Save raw response
            raw_file = OUTPUT_DIR / "datos_abiertos_raw.txt"
            with open(raw_file, "w", encoding="utf-8") as f:
                f.write(r.text[:10000])
            print(f"💾 Raw response saved to: {raw_file}")

    except httpx.HTTPStatusError as e:
        print(f"❌ HTTP Error: {e.response.status_code}")
    except Exception as e:
        print(f"💥 Error: {type(e).__name__}: {e}")

    return None


async def scrape_proveedores_catalog(client: httpx.AsyncClient):
    """
    Attempt to download the proveedores catalog with cédula jurídica
    and size classification (Grande/Mediana/Pequeña/Micro).
    """
    print("\n" + "="*70)
    print("🏢 P1.2: Scraping Proveedores Catalog")
    print("="*70)

    # Try the datos abiertos endpoint with PROVEEDORES report type
    jsp_url = f"{JSP_BASE}/CE_MOD_DATOSABIERTOSVIEW.jsp"

    form_params = {
        "tipoReporte": "PROVEEDORES",
        # No filters - get full catalog
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }

    try:
        print(f"\n🌐 Testing: {jsp_url} (tipoReporte=PROVEEDORES)")

        r = await client.post(
            jsp_url,
            data=form_params,
            headers=headers,
            timeout=30.0,
            follow_redirects=True
        )

        print(f"📡 Status: {r.status_code}")
        print(f"📄 Content-Type: {r.headers.get('content-type', 'unknown')}")

        if "json" in r.headers.get("content-type", "").lower():
            data = r.json()
            print(f"✅ Got {len(data)} proveedores")

            # Inspect structure
            if data:
                sample = data[0]
                print(f"\n🔍 Sample keys: {list(sample.keys())}")

                # Look for cédula field
                cedula_fields = [k for k in sample.keys() if "cedula" in k.lower() or "ruc" in k.lower() or "id" in k.lower()]
                if cedula_fields:
                    print(f"🎯 Cédula fields: {cedula_fields}")

                # Look for size classification
                size_fields = [k for k in sample.keys() if any(x in k.lower() for x in ["tama", "size", "clasif", "grande", "peque", "micro"])]
                if size_fields:
                    print(f"🎯 Size classification fields: {size_fields}")

            output_file = OUTPUT_DIR / "proveedores_catalog.json"
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"💾 Saved to: {output_file}")
            return data

        else:
            print("⚠️  Non-JSON response - may need different approach")
            # Save for manual inspection
            raw_file = OUTPUT_DIR / "proveedores_raw.html"
            with open(raw_file, "w", encoding="utf-8") as f:
                f.write(r.text[:10000])
            print(f"💾 Saved HTML to: {raw_file}")

    except Exception as e:
        print(f"💥 Error: {type(e).__name__}: {e}")

    return None


async def inspect_detalle_pliego_with_unspsc(client: httpx.AsyncClient, inst_cartel_no: str = None):
    """
    Try to get line-item level details for a specific cartel,
    looking for UNSPSC codes at the item level (not cartel level).

    REST API rarely has unspscCd on publicadas, but adjudicadas line items
    should have them via detail endpoint.
    """
    print("\n" + "="*70)
    print("🔍 P1.3: Inspecting Detalle Pliego for UNSPSC Line Items")
    print("="*70)

    # First, let's get a sample adjudicada from the REST API
    if not inst_cartel_no:
        print("\n📡 Fetching sample adjudicada from REST API...")
        adjudicadas_url = f"{REST_BASE}/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded"

        payload = {
            "pageNumber": 0,
            "pageSize": 5,
            "tableSorter": {"sorter": "", "order": "desc"},
            "tableFilters": [],
            "formFilters": [
                {"field": "bgnYmd", "value": "2026-02-01T00:00:00.000Z"},
                {"field": "endYmd", "value": "2026-03-07T23:59:59.999Z"},
                {"field": "typeKey", "value": "RPT_ADJ"}
            ]
        }

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Origin": "https://www.sicop.go.cr",
            "Referer": "https://www.sicop.go.cr/",
        }

        try:
            r = await client.post(adjudicadas_url, json=payload, headers=headers, timeout=30.0)
            if r.status_code == 200:
                data = r.json()
                content = data.get("content", [])
                if content:
                    # Pick first one with instCartelNo
                    sample = content[0]
                    inst_cartel_no = sample.get("instCartelNo")
                    print(f"✅ Sample adjudicada: {inst_cartel_no}")
                    print(f"   Title: {sample.get('cartelNm', 'N/A')[:60]}...")
                    print(f"   UNSPSC (cartel level): {sample.get('unspscCd', 'null')}")
                else:
                    print("⚠️  No adjudicadas found")
                    return None
            else:
                print(f"❌ REST API error: {r.status_code}")
                return None
        except Exception as e:
            print(f"💥 Error fetching sample: {e}")
            return None

    if not inst_cartel_no:
        print("❌ No instCartelNo to inspect")
        return None

    # Now try to get line-item details
    # Potential endpoints based on Angular chunk analysis patterns
    detail_endpoints = [
        f"{REST_BASE}/bid/api/v1/public/epCartel/getDetail",
        f"{REST_BASE}/bid/api/v1/public/epCartel/lineItems",
        f"{REST_BASE}/bid/api/v1/public/epCartel/partidas",
    ]

    print(f"\n🔎 Testing detail endpoints for: {inst_cartel_no}")

    for endpoint in detail_endpoints:
        try:
            print(f"\n🌐 Testing: {endpoint}")

            # Try with instCartelNo as param
            payload = {"instCartelNo": inst_cartel_no}

            r = await client.post(
                endpoint,
                json=payload,
                headers=headers,
                timeout=10.0
            )

            print(f"   Status: {r.status_code}")

            if r.status_code == 200:
                data = r.json()
                print(f"   ✅ Success! Got data type: {type(data)}")

                # Save for analysis
                endpoint_name = endpoint.split("/")[-1]
                output_file = OUTPUT_DIR / f"detalle_{endpoint_name}_{inst_cartel_no.replace('-', '_')}.json"
                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                print(f"   💾 Saved to: {output_file}")

                # Check for UNSPSC in response
                json_str = json.dumps(data, ensure_ascii=False).lower()
                if "unspsc" in json_str or "partida" in json_str or "linea" in json_str:
                    print(f"   🎯 UNSPSC or line items detected!")

                    # Try to extract structure
                    if isinstance(data, list) and len(data) > 0:
                        print(f"   📋 Array with {len(data)} items")
                        sample = data[0]
                        print(f"   🔍 Keys: {list(sample.keys())}")

                    return data

            elif r.status_code == 404:
                print(f"   ❌ Not found")
            else:
                print(f"   ⚠️  Status {r.status_code}")
                if r.text:
                    print(f"   📝 Response preview: {r.text[:200]}")

        except Exception as e:
            print(f"   💥 Error: {type(e).__name__}: {e}")

    # Also try datos abiertos JSP for the same cartel
    print(f"\n📊 Trying datos abiertos JSP for detalle pliego...")
    jsp_url = f"{JSP_BASE}/CE_MOD_DATOSABIERTOSVIEW.jsp"

    form_params = {
        "codigoInstitucion": inst_cartel_no.split("-")[-1] if "-" in inst_cartel_no else "",
        "tipoProcedimiento": inst_cartel_no.split("-")[0][4:6] if "-" in inst_cartel_no else "LD",
        "fechaDesde": "20260101",
        "fechaHasta": "20260307",
        "tipoReporte": "DETALLE_PLIEGO",
        "numeroProcedimiento": inst_cartel_no.split("-")[1] if "-" in inst_cartel_no else "",
    }

    try:
        r = await client.post(
            jsp_url,
            data=form_params,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=30.0,
            follow_redirects=True
        )

        print(f"📡 Status: {r.status_code}")
        print(f"📄 Content-Type: {r.headers.get('content-type', 'unknown')}")

        if "json" in r.headers.get("content-type", "").lower():
            data = r.json()
            print(f"✅ Got detalle pliego data!")

            # Check for UNSPSC
            json_str = json.dumps(data, ensure_ascii=False)
            if "unspsc" in json_str.lower():
                print("🎯🎯🎯 UNSPSC codes found in detalle pliego!")

            output_file = OUTPUT_DIR / f"detalle_pliego_jsp_{inst_cartel_no.replace('-', '_')}.json"
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"💾 Saved to: {output_file}")
            return data
        else:
            raw_file = OUTPUT_DIR / f"detalle_pliego_jsp_{inst_cartel_no.replace('-', '_')}.html"
            with open(raw_file, "w", encoding="utf-8") as f:
                f.write(r.text[:10000])
            print(f"💾 HTML response saved to: {raw_file}")

    except Exception as e:
        print(f"💥 Error: {type(e).__name__}: {e}")

    return None


async def check_price_bank_cata_params(client: httpx.AsyncClient):
    """
    Test priceBankCata/list endpoint with various param combinations.
    This endpoint currently returns 500 - need to find working params.
    """
    print("\n" + "="*70)
    print("💰 P1.4: Probing priceBankCata/list (Currently 500)")
    print("="*70)

    url = f"{REST_BASE}/bid/api/v1/public/priceBankCata/list"

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Origin": "https://www.sicop.go.cr",
        "Referer": "https://www.sicop.go.cr/",
    }

    # Try different payload structures
    payloads = [
        # Standard listPage format
        {
            "pageNumber": 0,
            "pageSize": 10,
            "tableSorter": {"sorter": "", "order": "desc"},
            "tableFilters": [],
            "formFilters": [
                {"field": "bgnYmd", "value": "2026-01-01T00:00:00.000Z"},
                {"field": "endYmd", "value": "2026-03-07T23:59:59.999Z"},
            ]
        },
        # Direct fields format (like getGeneralReport)
        {
            "dateBefore": "2026-01-01",
            "dateAfter": "2026-03-07",
        },
        # Minimal payload
        {
            "pageNumber": 0,
            "pageSize": 10,
        },
        # With instCartelNo filter
        {
            "pageNumber": 0,
            "pageSize": 10,
            "formFilters": [
                {"field": "instCartelNo", "value": "2026LD-000001-0031700001"},
            ]
        },
    ]

    for i, payload in enumerate(payloads):
        try:
            print(f"\n🧪 Test payload {i+1}: {list(payload.keys())}")
            r = await client.post(url, json=payload, headers=headers, timeout=10.0)
            print(f"   Status: {r.status_code}")

            if r.status_code == 200:
                print(f"   ✅ SUCCESS! Found working params")
                data = r.json()
                output_file = OUTPUT_DIR / f"price_bank_cata_working.json"
                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump({
                        "working_payload": payload,
                        "response": data
                    }, f, indent=2, ensure_ascii=False)
                print(f"   💾 Saved to: {output_file}")
                return data
            elif r.status_code == 500:
                error_data = r.json() if r.text else {"error": "Empty response"}
                print(f"   ❌ 500 Error: {error_data.get('message', 'Unknown')}")
            else:
                print(f"   ⚠️  Status {r.status_code}")

        except Exception as e:
            print(f"   💥 Error: {type(e).__name__}: {e}")

    return None


async def main():
    print("\n" + "="*70)
    print("🔬 P1: Datos Abiertos Validation & UNSPSC Discovery")
    print("="*70)
    print(f"\n📁 Output directory: {OUTPUT_DIR}")
    print(f"⏰ Started at: {datetime.now().isoformat()}")

    async with httpx.AsyncClient(follow_redirects=True) as client:
        results = {}

        # P1.1: Test JSP endpoint
        results["datos_abiertos"] = await test_datos_abiertos_jsp(client)

        # P1.2: Scrape proveedores
        results["proveedores"] = await scrape_proveedores_catalog(client)

        # P1.3: Inspect detalle pliego for UNSPSC
        results["detalle_unspsc"] = await inspect_detalle_pliego_with_unspsc(client)

        # P1.4: Bonus - probe price bank endpoint
        results["price_bank"] = await check_price_bank_cata_params(client)

    # Summary
    print("\n" + "="*70)
    print("📊 P1 Results Summary")
    print("="*70)

    for key, value in results.items():
        status = "✅ Data captured" if value else "❌ No data / Failed"
        print(f"{key:20} {status}")

    print(f"\n💾 All outputs saved to: {OUTPUT_DIR}/")
    print(f"⏰ Finished at: {datetime.now().isoformat()}")

    # Write summary
    summary_file = OUTPUT_DIR / "p1_summary.json"
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "results": {k: "success" if v else "failed" for k, v in results.items()},
            "output_dir": str(OUTPUT_DIR),
        }, f, indent=2)
    print(f"📄 Summary saved to: {summary_file}")


if __name__ == "__main__":
    asyncio.run(main())
