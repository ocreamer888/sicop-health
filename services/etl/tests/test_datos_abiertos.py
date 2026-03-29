"""Tests for the Datos Abiertos two-step download engine."""
import io, json, zipfile
import pytest
import httpx
from unittest.mock import AsyncMock, MagicMock, patch

# ── Helpers ──────────────────────────────────────────────────────────────────

def make_zip(filename: str, data: list) -> bytes:
    """Create a ZIP bytes object containing one JSON file."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr(filename, json.dumps(data))
    return buf.getvalue()


SERVLET_BASE = "https://www.sicop.go.cr/moduloPcont/servlet/cont/rp"


# ── _fmt_date ─────────────────────────────────────────────────────────────────

def test_fmt_date_formats_correctly():
    from datos_abiertos import _fmt_date
    assert _fmt_date("2026-03-01") == "01032026"
    assert _fmt_date("2026-12-31") == "31122026"


# ── _create_job ───────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_create_job_returns_filename():
    from datos_abiertos import _create_job, REPORT_CONFIGS
    mock_response = MagicMock()
    mock_response.text = "Solicitud de contratac 12345.zip"
    mock_response.raise_for_status = MagicMock()

    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=mock_response)

    cfg = REPORT_CONFIGS["SC"]
    result = await _create_job(mock_client, cfg, "01032026", "26032026", inst_cd="")
    assert result == "Solicitud de contratac 12345.zip"

    # Verify correct URL and cmd=create param
    call_kwargs = mock_client.post.call_args
    assert cfg["controller"] in call_kwargs[0][0]
    assert call_kwargs[1]["data"]["cmd"] == "create"


@pytest.mark.asyncio
async def test_create_job_returns_none_on_empty_response():
    from datos_abiertos import _create_job, REPORT_CONFIGS
    mock_response = MagicMock()
    mock_response.text = ""
    mock_response.raise_for_status = MagicMock()

    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=mock_response)

    result = await _create_job(mock_client, REPORT_CONFIGS["SC"], "01032026", "26032026", "")
    assert result is None


# ── _download_zip ─────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_download_zip_parses_records():
    from datos_abiertos import _download_zip, REPORT_CONFIGS
    records = [{"NUMERO_PROCEDIMIENTO": "2026LD-000001-0031700001", "PRESUPUESTO": "1000000"}]
    zip_bytes = make_zip("Solicitud de contratacion.json", records)

    mock_response = MagicMock()
    mock_response.content = zip_bytes
    mock_response.raise_for_status = MagicMock()

    mock_client = AsyncMock()
    mock_client.get = AsyncMock(return_value=mock_response)

    cfg = REPORT_CONFIGS["SC"]
    result = await _download_zip(mock_client, cfg, "some_file.zip")
    assert len(result) == 1
    assert result[0]["NUMERO_PROCEDIMIENTO"] == "2026LD-000001-0031700001"


# ── fetch_report (integration of both steps) ─────────────────────────────────

@pytest.mark.asyncio
async def test_fetch_report_retries_on_empty_token():
    from datos_abiertos import fetch_report
    # create always returns empty token → should retry and eventually return []
    with patch("datos_abiertos.httpx.AsyncClient") as mock_cls:
        mock_client = AsyncMock()
        mock_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_cls.return_value.__aexit__ = AsyncMock(return_value=False)

        empty_resp = MagicMock()
        empty_resp.text = ""
        empty_resp.raise_for_status = MagicMock()
        mock_client.post = AsyncMock(return_value=empty_resp)

        result = await fetch_report("SC", "01032026", "26032026", inst_cd="", retries=2)
        assert result == []
        assert mock_client.post.call_count == 2


# ── parse_sc_record ───────────────────────────────────────────────────────────

def test_parse_sc_record_extracts_budget():
    from datos_abiertos import parse_sc_record
    r = parse_sc_record({
        "NUMERO_PROCEDIMIENTO": "2026LD-000001-0031700001",
        "PRESUPUESTO": "13018975.2",
        "MONEDA": "CRC",
    })
    assert r["instcartelno"] == "2026LD-000001-0031700001"
    assert r["presupuesto_estimado"] == pytest.approx(13018975.2)
    assert r["moneda_presupuesto"] == "CRC"


def test_parse_sc_record_handles_missing_budget():
    from datos_abiertos import parse_sc_record
    r = parse_sc_record({
        "NUMERO_PROCEDIMIENTO": "2026LD-000001-0031700001",
        "PRESUPUESTO": None,
    })
    assert r["presupuesto_estimado"] is None
    assert r["moneda_presupuesto"] == "CRC"


def test_parse_sc_record_returns_none_without_key():
    from datos_abiertos import parse_sc_record
    assert parse_sc_record({"PRESUPUESTO": "1000"}) is None


# ── parse_dc_record ───────────────────────────────────────────────────────────

def test_parse_dc_record_precalificacion():
    from datos_abiertos import parse_dc_record
    r = parse_dc_record({
        "NRO_PROCEDIMIENTO": "2026LD-000001-0031700001",
        "MODALIDAD_PROCEDIMIENTO": "Precalificación",
    })
    assert r["instcartelno"] == "2026LD-000001-0031700001"
    assert r["modalidad_participacion"] == "Precalificación"


def test_parse_dc_record_open_bid():
    from datos_abiertos import parse_dc_record
    r = parse_dc_record({
        "NRO_PROCEDIMIENTO": "2026LD-000001-0031700001",
        "MODALIDAD_PROCEDIMIENTO": "Cantidad definida",
    })
    assert r["modalidad_participacion"] == "Cantidad definida"


def test_parse_dc_record_empty_modalidad_gives_none():
    from datos_abiertos import parse_dc_record
    r = parse_dc_record({
        "NRO_PROCEDIMIENTO": "2026LD-000001-0031700001",
        "MODALIDAD_PROCEDIMIENTO": "",
    })
    # Unknown (~85% of records): must be None, not empty string
    assert r["modalidad_participacion"] is None


def test_parse_dc_record_returns_none_without_key():
    from datos_abiertos import parse_dc_record
    assert parse_dc_record({"MODALIDAD_PROCEDIMIENTO": "Servicios"}) is None


# ── parse_oferta_record ───────────────────────────────────────────────────────

def test_parse_oferta_eligible_si():
    from datos_abiertos import parse_oferta_record
    r = parse_oferta_record({
        "NUMERO_PROCEDIMIENTO": "2026LD-000001-0031700001",
        "CEDULA_PROVEEDOR":     "3101216432",
        "NOMBRE_PROVEEDOR":     "Empresa S.A.",
        "ELEGIBLE":             "Si",
        "ESTADO":               "Presentada",
    })
    assert r["instcartelno"] == "2026LD-000001-0031700001"
    assert r["suppliercd"] == "3101216432"
    assert r["elegible"] is True


def test_parse_oferta_eligible_no():
    from datos_abiertos import parse_oferta_record
    r = parse_oferta_record({
        "NUMERO_PROCEDIMIENTO": "2026LD-000001-0031700001",
        "CEDULA_PROVEEDOR":     "3101216432",
        "ELEGIBLE":             "No",
    })
    assert r["elegible"] is False


def test_parse_oferta_elegible_no_evaluada_is_none():
    from datos_abiertos import parse_oferta_record
    r = parse_oferta_record({
        "NUMERO_PROCEDIMIENTO": "2026LD-000001-0031700001",
        "CEDULA_PROVEEDOR":     "3101216432",
        "ELEGIBLE":             "No evaluada",
    })
    assert r["elegible"] is None


def test_parse_oferta_returns_none_without_key():
    from datos_abiertos import parse_oferta_record
    assert parse_oferta_record({"CEDULA_PROVEEDOR": "123"}) is None


# ── upsert_scalar_enrichments ─────────────────────────────────────────────────

def test_upsert_scalar_skips_none_values():
    from datos_abiertos import upsert_scalar_enrichments
    mock_sb = MagicMock()
    mock_table = MagicMock()
    mock_sb.table.return_value = mock_table
    mock_table.upsert.return_value = mock_table
    mock_table.execute.return_value = MagicMock()

    rows = [
        {"instcartelno": "A", "presupuesto_estimado": 1000.0, "moneda_presupuesto": "CRC"},
        {"instcartelno": "A", "modalidad_participacion": None},  # None must be dropped
        {"instcartelno": "B", "modalidad_participacion": "Precalificación"},
    ]
    count = upsert_scalar_enrichments(rows, mock_sb)
    assert count == 2  # A (merged) and B

    call_args = mock_table.upsert.call_args[0][0]
    row_a = next(r for r in call_args if r["instcartelno"] == "A")
    # None values must NOT appear in the upsert payload
    assert "modalidad_participacion" not in row_a or row_a.get("modalidad_participacion") is not None


def test_upsert_scalar_returns_zero_for_empty():
    from datos_abiertos import upsert_scalar_enrichments
    mock_sb = MagicMock()
    assert upsert_scalar_enrichments([], mock_sb) == 0


def test_upsert_scalar_enrichments_returns_zero_on_db_error():
    from datos_abiertos import upsert_scalar_enrichments
    mock_sb = MagicMock()
    mock_table = MagicMock()
    mock_sb.table.return_value = mock_table
    mock_table.upsert.return_value = mock_table
    mock_table.execute.side_effect = Exception("DB constraint violation")

    sc = [{"instcartelno": "2026CD-001-0031700001", "presupuesto_estimado": 1000.0, "moneda_presupuesto": "CRC"}]
    dc = []
    # Must NOT raise — must return 0
    result = upsert_scalar_enrichments(sc, dc, mock_sb)
    assert result == 0


def test_upsert_scalar_enrichments_filters_to_known_set():
    from datos_abiertos import upsert_scalar_enrichments
    mock_sb = MagicMock()
    mock_table = MagicMock()
    mock_sb.table.return_value = mock_table
    mock_table.upsert.return_value = mock_table
    mock_table.execute.return_value = MagicMock()

    known = {"2026CD-001-0031700001"}
    sc = [
        {"instcartelno": "2026CD-001-0031700001", "presupuesto_estimado": 1000.0, "moneda_presupuesto": "CRC"},
        {"instcartelno": "2026CD-999-UNKNOWN",    "presupuesto_estimado": 2000.0, "moneda_presupuesto": "CRC"},
    ]
    result = upsert_scalar_enrichments(sc, [], mock_sb, known_set=known)
    assert result == 1  # only the known procedure was upserted


# ── upsert_ofertas ────────────────────────────────────────────────────────────

def test_upsert_ofertas_skips_rows_without_suppliercd():
    from datos_abiertos import upsert_ofertas
    mock_sb = MagicMock()
    mock_table = MagicMock()
    mock_sb.table.return_value = mock_table
    mock_table.upsert.return_value = mock_table
    mock_table.execute.return_value = MagicMock()

    rows = [
        {"instcartelno": "A", "suppliercd": "123", "elegible": True},
        {"instcartelno": "A", "suppliercd": None},   # must be skipped
        {"instcartelno": None, "suppliercd": "456"},  # must be skipped
    ]
    count = upsert_ofertas(rows, mock_sb)
    assert count == 1

    call_args = mock_table.upsert.call_args[0][0]
    assert len(call_args) == 1
    assert call_args[0]["suppliercd"] == "123"


def test_upsert_ofertas_returns_zero_on_db_error():
    from datos_abiertos import upsert_ofertas
    mock_sb = MagicMock()
    mock_table = MagicMock()
    mock_sb.table.return_value = mock_table
    mock_table.upsert.return_value = mock_table
    mock_table.execute.side_effect = Exception("FK violation")

    rows = [{"instcartelno": "2026CD-001-0031700001", "suppliercd": "3101111111", "suppliernm": "Proveedor A"}]
    result = upsert_ofertas(rows, mock_sb)
    assert result == 0


# ── run_datos_abiertos ────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_run_datos_abiertos_calls_all_three_reports():
    from datos_abiertos import run_datos_abiertos

    sc_record = {"NUMERO_PROCEDIMIENTO": "2026LD-000001-0031700001", "PRESUPUESTO": "1000", "MONEDA": "CRC"}
    dc_record = {"NRO_PROCEDIMIENTO": "2026LD-000001-0031700001", "MODALIDAD_PROCEDIMIENTO": "Cantidad definida"}
    o_record  = {"NUMERO_PROCEDIMIENTO": "2026LD-000001-0031700001", "CEDULA_PROVEEDOR": "123", "ELEGIBLE": "Si"}

    af_record = {"NUMERO_PROCEDIMIENTO": "2026LD-000001-0031700001", "FECHA_ADJ_FIRME": "2026-02-27 15:00:27", "DESIERTO": "N"}

    call_order = []
    async def mock_fetch(report_key, *args, **kwargs):
        call_order.append(report_key)
        fixtures = {
            "SC": [sc_record], "DC": [dc_record], "O": [o_record], "AF": [af_record],
            "C": [], "R": [], "A": [], "OP": [],
        }
        return fixtures.get(report_key, [])

    mock_sb = MagicMock()
    mock_table = MagicMock()
    mock_sb.table.return_value = mock_table
    mock_table.upsert.return_value = mock_table
    mock_table.insert.return_value = mock_table
    mock_table.select.return_value = mock_table
    mock_table.limit.return_value = mock_table
    mock_table.execute.return_value = MagicMock(data=[{"instcartelno": "2026LD-000001-0031700001"}])

    with patch("datos_abiertos.fetch_report", side_effect=mock_fetch):
        stats = await run_datos_abiertos(dias=7, supabase_client=mock_sb)

    assert "SC" in call_order
    assert "DC" in call_order
    assert "O" in call_order
    assert "AF" in call_order
    assert stats["scalar"] >= 0
    assert stats["ofertas"] >= 0
    assert stats["adjudicaciones"] >= 0


# ── parse_af_record ────────────────────────────────────────────────────────────

def test_parse_af_record_header_returns_correct_fields():
    from datos_abiertos import parse_af_record
    r = parse_af_record({
        "NUMERO_PROCEDIMIENTO": "2025LY-000006-0001102105",
        "FECHA_ADJ_FIRME":      "2026-02-27 15:00:27",
        "DESIERTO":             "N",
        "NRO_SICOP":            "20250903493",
        "PERMITE_RECURSOS":     "Si",
    })
    assert r is not None
    assert r["instcartelno"] == "2025LY-000006-0001102105"
    assert r["fecha_adj_firme"] == "2026-02-27 15:00:27"
    assert r["desierto"] is False


def test_parse_af_record_desierto_yes():
    from datos_abiertos import parse_af_record
    r = parse_af_record({
        "NUMERO_PROCEDIMIENTO": "2025LY-000007-0001102105",
        "FECHA_ADJ_FIRME":      "2026-01-15 10:00:00",
        "DESIERTO":             "S",
    })
    assert r is not None
    assert r["desierto"] is True


def test_parse_af_record_skips_partida_schema():
    from datos_abiertos import parse_af_record
    # PARTIDA records have NUMERO_PARTIDA, not NUMERO_PROCEDIMIENTO
    r = parse_af_record({
        "NUMERO_PARTIDA":     "2026LD-000022-0001102701",
        "NUMERO_LINEA":       "20260202046",
        "CANTIDAD_SOLICITADA": "3101111262",
    })
    assert r is None


def test_parse_af_record_skips_pricing_schema():
    from datos_abiertos import parse_af_record
    # PRICING records have CEDULA_PROVEEDOR + NRO_ACTO but no NUMERO_PROCEDIMIENTO
    r = parse_af_record({
        "CEDULA_PROVEEDOR":            "3101189270",
        "PRECIO_UNITARIO_ADJUDICADO":  "25",
        "NRO_ACTO":                    "1272518",
        "CANTIDAD_ADJUDICADA":         "1",
    })
    assert r is None


def test_parse_af_record_handles_none_input():
    from datos_abiertos import parse_af_record
    assert parse_af_record({}) is None
    assert parse_af_record({"NRO_SICOP": "123"}) is None


def test_parse_af_record_missing_fecha_adj_firme():
    from datos_abiertos import parse_af_record
    r = parse_af_record({
        "NUMERO_PROCEDIMIENTO": "2025LY-000009-0001102105",
        "DESIERTO":             "N",
    })
    assert r is not None
    assert r["instcartelno"] == "2025LY-000009-0001102105"
    assert r["fecha_adj_firme"] is None
    assert r["desierto"] is False


# ── upsert_adjudicaciones ──────────────────────────────────────────────────────

def test_upsert_adjudicaciones_patches_licitaciones():
    from datos_abiertos import upsert_adjudicaciones
    mock_sb = MagicMock()
    mock_table = MagicMock()
    mock_sb.table.return_value = mock_table
    mock_table.upsert.return_value = mock_table
    mock_table.execute.return_value = MagicMock()

    rows = [
        {"instcartelno": "A", "fecha_adj_firme": "2026-02-27 15:00:27", "desierto": False},
        {"instcartelno": "B", "fecha_adj_firme": "2026-01-15 10:00:00", "desierto": True},
    ]
    count = upsert_adjudicaciones(rows, mock_sb)
    assert count == 2

    mock_sb.table.assert_called_with("licitaciones_medicas")
    call_args = mock_table.upsert.call_args
    assert call_args[1].get("on_conflict") == "instcartelno" or call_args[0][1] == "instcartelno" or "instcartelno" in str(call_args)


def test_upsert_adjudicaciones_returns_zero_for_empty():
    from datos_abiertos import upsert_adjudicaciones
    mock_sb = MagicMock()
    assert upsert_adjudicaciones([], mock_sb) == 0


def test_upsert_adjudicaciones_skips_rows_without_instcartelno():
    from datos_abiertos import upsert_adjudicaciones
    mock_sb = MagicMock()
    mock_table = MagicMock()
    mock_sb.table.return_value = mock_table
    mock_table.upsert.return_value = mock_table
    mock_table.execute.return_value = MagicMock()

    rows = [
        {"instcartelno": "A", "fecha_adj_firme": "2026-02-27 15:00:27", "desierto": False},
        {"instcartelno": None, "fecha_adj_firme": "2026-01-01 00:00:00", "desierto": False},
    ]
    count = upsert_adjudicaciones(rows, mock_sb)
    assert count == 1


def test_upsert_adjudicaciones_returns_zero_on_db_error():
    from datos_abiertos import upsert_adjudicaciones
    mock_sb = MagicMock()
    mock_table = MagicMock()
    mock_sb.table.return_value = mock_table
    mock_table.upsert.return_value = mock_table
    mock_table.execute.side_effect = Exception("DB error")

    rows = [{"instcartelno": "2026CD-001-0031700001", "fecha_adj_firme": "2026-03-01", "desierto": False}]
    result = upsert_adjudicaciones(rows, mock_sb)
    assert result == 0


def test_upsert_adjudicaciones_filters_to_known_set():
    from datos_abiertos import upsert_adjudicaciones
    mock_sb = MagicMock()
    mock_table = MagicMock()
    mock_sb.table.return_value = mock_table
    mock_table.upsert.return_value = mock_table
    mock_table.execute.return_value = MagicMock()

    known = {"2026CD-001-0031700001"}
    rows = [
        {"instcartelno": "2026CD-001-0031700001", "fecha_adj_firme": "2026-03-01", "desierto": False},
        {"instcartelno": "2026CD-999-UNKNOWN",    "fecha_adj_firme": "2026-03-02", "desierto": False},
    ]
    result = upsert_adjudicaciones(rows, mock_sb, known_set=known)
    assert result == 1


# ── parse_af_pricing_record ────────────────────────────────────────────────────

def test_parse_af_pricing_record_extracts_fields():
    from datos_abiertos import parse_af_pricing_record
    row = {
        "CEDULA_PROVEEDOR":           "3101189270",
        "NOMBRE_PROVEEDOR":           "Proveedor S.A.",
        "PRECIO_UNITARIO_ADJUDICADO": "25",
        "CANTIDAD_ADJUDICADA":        "10",
        "UNIDAD_MEDIDA":              "UND",
        "DESCRIPCION":                "Guantes descartables",
        "CODIGO_IDENTIFICACION":      "42131601",
        "NRO_ACTO":                   "1272518",
    }
    r = parse_af_pricing_record(row, "2025LY-000006-0001102105")
    assert r is not None
    assert r["instcartelno"] == "2025LY-000006-0001102105"
    assert r["descripcion_item"] == "Guantes descartables"
    assert r["clasificacion_unspsc"] == "42131601"
    assert r["proveedor"] == "Proveedor S.A."
    assert r["precio_unitario"] == pytest.approx(25.0)
    assert r["cantidad"] == pytest.approx(10.0)
    assert r["unidad"] == "UND"
    assert r["rawdata"] == row


def test_parse_af_pricing_record_returns_none_without_instcartelno():
    from datos_abiertos import parse_af_pricing_record
    row = {
        "CEDULA_PROVEEDOR":           "3101189270",
        "PRECIO_UNITARIO_ADJUDICADO": "25",
        "CANTIDAD_ADJUDICADA":        "1",
    }
    assert parse_af_pricing_record(row, None) is None


def test_parse_af_pricing_record_returns_none_for_header_rows():
    from datos_abiertos import parse_af_pricing_record
    # HEADER rows have NUMERO_PROCEDIMIENTO — must not be parsed as pricing
    row = {
        "NUMERO_PROCEDIMIENTO": "2025LY-000006-0001102105",
        "FECHA_ADJ_FIRME":      "2026-02-27 15:00:27",
        "DESIERTO":             "N",
    }
    assert parse_af_pricing_record(row, "2025LY-000006-0001102105") is None


def test_parse_af_pricing_record_returns_none_when_no_useful_data():
    from datos_abiertos import parse_af_pricing_record
    # No precio_unitario, no cantidad — not useful
    row = {
        "CEDULA_PROVEEDOR": "3101189270",
        "NOMBRE_PROVEEDOR": "Proveedor S.A.",
        "NRO_ACTO":         "1272518",
    }
    assert parse_af_pricing_record(row, "2025LY-000006-0001102105") is None


def test_parse_af_pricing_record_falls_back_cedula_as_proveedor():
    from datos_abiertos import parse_af_pricing_record
    # NOMBRE_PROVEEDOR absent — fallback to CEDULA_PROVEEDOR
    row = {
        "CEDULA_PROVEEDOR":           "3101189270",
        "PRECIO_UNITARIO_ADJUDICADO": "50",
    }
    r = parse_af_pricing_record(row, "2025LY-000006-0001102105")
    assert r is not None
    assert r["proveedor"] == "3101189270"
    assert r["descripcion_item"] == ""


# ── upsert_precios_historicos ──────────────────────────────────────────────────

def test_upsert_precios_historicos_inserts_valid_rows():
    from datos_abiertos import upsert_precios_historicos
    mock_sb = MagicMock()
    mock_table = MagicMock()
    mock_sb.table.return_value = mock_table
    mock_table.insert.return_value = mock_table
    mock_table.execute.return_value = MagicMock()

    rows = [
        {
            "instcartelno":    "2025LY-000006-0001102105",
            "descripcion_item": "Guantes",
            "precio_unitario": 25.0,
            "cantidad":        10.0,
        },
        {
            "instcartelno":    "2025LY-000007-0001102105",
            "descripcion_item": "Mascarillas",
            "precio_unitario": 50.0,
            "cantidad":        5.0,
        },
    ]
    count = upsert_precios_historicos(rows, mock_sb)
    assert count == 2
    mock_sb.table.assert_called_with("precios_historicos")
    call_args = mock_table.insert.call_args[0][0]
    assert len(call_args) == 2


def test_upsert_precios_historicos_skips_rows_without_instcartelno():
    from datos_abiertos import upsert_precios_historicos
    mock_sb = MagicMock()
    mock_table = MagicMock()
    mock_sb.table.return_value = mock_table
    mock_table.insert.return_value = mock_table
    mock_table.execute.return_value = MagicMock()

    rows = [
        {"instcartelno": "A", "descripcion_item": "Item A", "precio_unitario": 10.0, "cantidad": 1.0},
        {"instcartelno": None, "descripcion_item": "Item B", "precio_unitario": 20.0, "cantidad": 2.0},
        {"instcartelno": "",   "descripcion_item": "Item C", "precio_unitario": 30.0, "cantidad": 3.0},
    ]
    count = upsert_precios_historicos(rows, mock_sb)
    assert count == 1
    call_args = mock_table.insert.call_args[0][0]
    assert len(call_args) == 1
    assert call_args[0]["instcartelno"] == "A"


def test_upsert_precios_historicos_skips_empty_desc_and_no_precio():
    from datos_abiertos import upsert_precios_historicos
    mock_sb = MagicMock()
    mock_table = MagicMock()
    mock_sb.table.return_value = mock_table
    mock_table.insert.return_value = mock_table
    mock_table.execute.return_value = MagicMock()

    rows = [
        # Should be skipped: empty descripcion AND no precio_unitario
        {"instcartelno": "A", "descripcion_item": "", "precio_unitario": None, "cantidad": 5.0},
        # Should be kept: empty descripcion but has precio_unitario
        {"instcartelno": "B", "descripcion_item": "", "precio_unitario": 15.0, "cantidad": None},
        # Should be kept: has descripcion and precio
        {"instcartelno": "C", "descripcion_item": "Item C", "precio_unitario": 20.0, "cantidad": 2.0},
    ]
    count = upsert_precios_historicos(rows, mock_sb)
    assert count == 2


def test_upsert_precios_historicos_returns_zero_on_insert_error():
    from datos_abiertos import upsert_precios_historicos
    mock_sb = MagicMock()
    mock_table = MagicMock()
    mock_sb.table.return_value = mock_table
    # delete chain succeeds
    mock_delete = MagicMock()
    mock_table.delete.return_value = mock_delete
    mock_delete.eq.return_value = mock_delete
    mock_delete.in_.return_value = mock_delete
    mock_delete.execute.return_value = MagicMock()
    # insert raises
    mock_table.insert.return_value = mock_table
    mock_table.execute.side_effect = Exception("insert error")

    rows = [{"instcartelno": "2026CD-001", "fuente": "AF", "precio_unitario": 10.0, "cantidad": 1.0,
             "proveedor": "A", "descripcion_item": "item"}]
    result = upsert_precios_historicos(rows, mock_sb)
    assert result == 0


# ── run_datos_abiertos with AF ─────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_run_datos_abiertos_includes_af_report():
    from datos_abiertos import run_datos_abiertos

    sc_record = {"NUMERO_PROCEDIMIENTO": "2026LD-000001-0031700001", "PRESUPUESTO": "1000", "MONEDA": "CRC"}
    dc_record = {"NRO_PROCEDIMIENTO": "2026LD-000001-0031700001", "MODALIDAD_PROCEDIMIENTO": "Cantidad definida"}
    o_record  = {"NUMERO_PROCEDIMIENTO": "2026LD-000001-0031700001", "CEDULA_PROVEEDOR": "123", "ELEGIBLE": "Si"}
    af_record = {
        "NUMERO_PROCEDIMIENTO": "2026LD-000001-0031700001",
        "FECHA_ADJ_FIRME":      "2026-02-27 15:00:27",
        "DESIERTO":             "N",
    }

    call_order = []
    async def mock_fetch(report_key, *args, **kwargs):
        call_order.append(report_key)
        fixtures = {
            "SC": [sc_record], "DC": [dc_record], "O": [o_record], "AF": [af_record],
            "C": [], "R": [], "A": [], "OP": [],
        }
        return fixtures.get(report_key, [])

    mock_sb = MagicMock()
    mock_table = MagicMock()
    mock_sb.table.return_value = mock_table
    mock_table.upsert.return_value = mock_table
    mock_table.insert.return_value = mock_table
    mock_table.select.return_value = mock_table
    mock_table.limit.return_value = mock_table
    mock_table.execute.return_value = MagicMock(data=[{"instcartelno": "2026LD-000001-0031700001"}])

    with patch("datos_abiertos.fetch_report", side_effect=mock_fetch):
        stats = await run_datos_abiertos(dias=7, supabase_client=mock_sb)

    assert "AF" in call_order
    assert set(["SC", "DC", "O", "AF", "C", "R", "A", "OP"]).issubset(set(call_order))
    assert "adjudicaciones" in stats
    assert stats["adjudicaciones"] >= 0
    assert "contratos" in stats
    assert "recursos" in stats
    assert "aclaraciones" in stats
    assert "ordenes" in stats


# ── parse_c_record ─────────────────────────────────────────────────────────────

def test_parse_c_record_returns_instcartelno():
    from datos_abiertos import parse_c_record
    r = parse_c_record({"NUMERO_PROCEDIMIENTO": "2026LD-000005-0001102105"})
    assert r is not None
    assert r["instcartelno"] == "2026LD-000005-0001102105"


def test_parse_c_record_returns_none_without_key():
    from datos_abiertos import parse_c_record
    assert parse_c_record({}) is None
    assert parse_c_record({"PRECIO_UNITARIO": "100"}) is None


# ── parse_c_pricing_record ─────────────────────────────────────────────────────

def test_parse_c_pricing_record_extracts_fields():
    from datos_abiertos import parse_c_pricing_record
    row = {
        "PRECIO_UNITARIO":     "150.50",
        "CANTIDADCONTRATADA":  "20",
        "DESCRIPCION":         "Guantes nitrilo",
        "CEDULA_PROVEEDOR":    "3101189270",
        "UNIDAD_MEDIDA":       "CAJA",
    }
    r = parse_c_pricing_record(row, "2026LD-000005-0001102105")
    assert r is not None
    assert r["instcartelno"] == "2026LD-000005-0001102105"
    assert r["precio_unitario"] == 150.50
    assert r["cantidad"] == 20.0
    assert r["descripcion_item"] == "Guantes nitrilo"
    assert r["proveedor"] == "3101189270"
    assert r["unidad"] == "CAJA"
    assert r["fuente"] == "C"


def test_parse_c_pricing_record_returns_none_without_instcartelno():
    from datos_abiertos import parse_c_pricing_record
    row = {"PRECIO_UNITARIO": "100", "CANTIDADCONTRATADA": "5"}
    assert parse_c_pricing_record(row, None) is None


def test_parse_c_pricing_record_returns_none_for_header_rows():
    from datos_abiertos import parse_c_pricing_record
    row = {"NUMERO_PROCEDIMIENTO": "2026LD-000005-0001102105", "PRECIO_UNITARIO": "100"}
    assert parse_c_pricing_record(row, "2026LD-000005-0001102105") is None


def test_parse_c_pricing_record_returns_none_when_no_useful_data():
    from datos_abiertos import parse_c_pricing_record
    row = {"CEDULA_PROVEEDOR": "3101189270"}  # No price, no quantity
    assert parse_c_pricing_record(row, "2026LD-000005-0001102105") is None


# ── parse_r_record ─────────────────────────────────────────────────────────────

def test_parse_r_record_extracts_fields():
    from datos_abiertos import parse_r_record
    r = parse_r_record({
        "NUMERO_PROCEDIMIENTO": "2026LD-000010-0001102105",
        "ASUNTO":               "Recurso de objeción al cartel",
        "CEDULA_PROVEEDOR":     "3102123456",
        "TIPO_RECURSO":         "OBJECION_CARTEL",
        "FECHA_SOLICITUD":      "2026-03-15 10:00:00",
    })
    assert r is not None
    assert r["instcartelno"] == "2026LD-000010-0001102105"
    assert r["asunto"] == "Recurso de objeción al cartel"
    assert r["cedula_proveedor"] == "3102123456"
    assert r["tipo_recurso"] == "OBJECION_CARTEL"
    assert r["fecha_solicitud"] == "2026-03-15 10:00:00"


def test_parse_r_record_returns_none_without_key():
    from datos_abiertos import parse_r_record
    assert parse_r_record({}) is None
    assert parse_r_record({"ASUNTO": "alguno"}) is None


def test_parse_r_record_accepts_nro_procedimiento_variant():
    from datos_abiertos import parse_r_record
    r = parse_r_record({"NRO_PROCEDIMIENTO": "2026LD-000011-0001102105", "TIPORECURSO": "APELACION"})
    assert r is not None
    assert r["instcartelno"] == "2026LD-000011-0001102105"
    assert r["tipo_recurso"] == "APELACION"


# ── parse_a_record ─────────────────────────────────────────────────────────────

def test_parse_a_record_extracts_fields():
    from datos_abiertos import parse_a_record
    r = parse_a_record({
        "NUMERO_PROCEDIMIENTO": "2026LD-000012-0001102105",
        "TITULO":               "Aclaración sobre especificaciones técnicas",
        "FECHA_SOLICITUD":      "2026-03-10 09:00:00",
        "SOLICITANTE":          "Empresa XYZ S.A.",
    })
    assert r is not None
    assert r["instcartelno"] == "2026LD-000012-0001102105"
    assert r["titulo"] == "Aclaración sobre especificaciones técnicas"
    assert r["fecha_solicitud"] == "2026-03-10 09:00:00"
    assert r["solicitante"] == "Empresa XYZ S.A."


def test_parse_a_record_returns_none_without_key():
    from datos_abiertos import parse_a_record
    assert parse_a_record({}) is None
    assert parse_a_record({"TITULO": "algo"}) is None


# ── parse_op_record ────────────────────────────────────────────────────────────

def test_parse_op_record_extracts_fields():
    from datos_abiertos import parse_op_record
    r = parse_op_record({
        "NUMERO_PROCEDIMIENTO":  "2026LD-000020-0001102105",
        "NUMERO_ORDEN_PEDIDO":   "OP-2026-001234",
        "CEDULA_PROVEEDOR":      "3101189270",
        "PRECIO_UNITARIO":       "75.00",
        "CANTIDAD":              "100",
        "UNIDAD_MEDIDA":         "UNIDAD",
        "MONTO_TOTAL":           "7500.00",
        "TIPO_MONEDA":           "CRC",
        "FECHA_ORDEN":           "2026-03-20 08:00:00",
    })
    assert r is not None
    assert r["numero_orden"] == "OP-2026-001234"
    assert r["instcartelno"] == "2026LD-000020-0001102105"
    assert r["precio_unitario"] == 75.0
    assert r["cantidad"] == 100.0
    assert r["monto_total"] == 7500.0
    assert r["currencytype"] == "CRC"
    assert r["fecha_orden"] == "2026-03-20 08:00:00"


def test_parse_op_record_returns_none_without_numero_orden():
    from datos_abiertos import parse_op_record
    assert parse_op_record({}) is None
    assert parse_op_record({"NUMERO_PROCEDIMIENTO": "2026LD-000020-0001102105"}) is None


def test_parse_op_record_instcartelno_nullable():
    from datos_abiertos import parse_op_record
    # OP may not have NUMERO_PROCEDIMIENTO — instcartelno should be None
    r = parse_op_record({"NUMERO_ORDEN_PEDIDO": "OP-2026-000001", "PRECIO_UNITARIO": "10"})
    assert r is not None
    assert r["instcartelno"] is None
    assert r["numero_orden"] == "OP-2026-000001"


# ── upsert_recursos ────────────────────────────────────────────────────────────

def test_upsert_recursos_inserts_valid_rows():
    from datos_abiertos import upsert_recursos
    mock_sb = MagicMock()
    mock_table = MagicMock()
    mock_sb.table.return_value = mock_table
    mock_table.insert.return_value = mock_table
    mock_table.execute.return_value = MagicMock()

    rows = [
        {"instcartelno": "A", "asunto": "Recurso 1", "cedula_proveedor": "123", "fecha_solicitud": "2026-01-01"},
        {"instcartelno": "B", "asunto": "Recurso 2", "cedula_proveedor": "456", "fecha_solicitud": "2026-01-02"},
    ]
    count = upsert_recursos(rows, mock_sb)
    assert count == 2
    mock_sb.table.assert_called_with("da_recursos")


def test_upsert_recursos_deduplicates():
    from datos_abiertos import upsert_recursos
    mock_sb = MagicMock()
    mock_table = MagicMock()
    mock_sb.table.return_value = mock_table
    mock_table.insert.return_value = mock_table
    mock_table.execute.return_value = MagicMock()

    rows = [
        {"instcartelno": "A", "cedula_proveedor": "123", "fecha_solicitud": "2026-01-01"},
        {"instcartelno": "A", "cedula_proveedor": "123", "fecha_solicitud": "2026-01-01"},  # dup
    ]
    count = upsert_recursos(rows, mock_sb)
    assert count == 1


def test_upsert_recursos_returns_zero_for_empty():
    from datos_abiertos import upsert_recursos
    assert upsert_recursos([], MagicMock()) == 0


def test_upsert_recursos_returns_zero_on_insert_error():
    from datos_abiertos import upsert_recursos
    mock_sb = MagicMock()
    mock_table = MagicMock()
    mock_sb.table.return_value = mock_table
    mock_delete = MagicMock()
    mock_table.delete.return_value = mock_delete
    mock_delete.in_.return_value = mock_delete
    mock_delete.execute.return_value = MagicMock()
    mock_table.insert.return_value = mock_table
    mock_table.execute.side_effect = Exception("insert error")

    rows = [{"instcartelno": "A", "asunto": "R1", "cedula_proveedor": "123", "fecha_solicitud": "2026-01-01"}]
    result = upsert_recursos(rows, mock_sb)
    assert result == 0


# ── upsert_aclaraciones ────────────────────────────────────────────────────────

def test_upsert_aclaraciones_inserts_valid_rows():
    from datos_abiertos import upsert_aclaraciones
    mock_sb = MagicMock()
    mock_table = MagicMock()
    mock_sb.table.return_value = mock_table
    mock_table.insert.return_value = mock_table
    mock_table.execute.return_value = MagicMock()

    rows = [
        {"instcartelno": "A", "titulo": "Aclaración 1", "fecha_solicitud": "2026-01-01", "solicitante": "S.A."},
    ]
    count = upsert_aclaraciones(rows, mock_sb)
    assert count == 1
    mock_sb.table.assert_called_with("da_aclaraciones")


def test_upsert_aclaraciones_returns_zero_for_empty():
    from datos_abiertos import upsert_aclaraciones
    assert upsert_aclaraciones([], MagicMock()) == 0


def test_upsert_aclaraciones_returns_zero_on_insert_error():
    from datos_abiertos import upsert_aclaraciones
    mock_sb = MagicMock()
    mock_table = MagicMock()
    mock_sb.table.return_value = mock_table
    mock_delete = MagicMock()
    mock_table.delete.return_value = mock_delete
    mock_delete.in_.return_value = mock_delete
    mock_delete.execute.return_value = MagicMock()
    mock_table.insert.return_value = mock_table
    mock_table.execute.side_effect = Exception("insert error")

    rows = [{"instcartelno": "A", "titulo": "T", "fecha_solicitud": "2026-01-01", "solicitante": "S"}]
    result = upsert_aclaraciones(rows, mock_sb)
    assert result == 0


# ── upsert_ordenes_pedido ──────────────────────────────────────────────────────

def test_upsert_ordenes_pedido_upserts_valid_rows():
    from datos_abiertos import upsert_ordenes_pedido
    mock_sb = MagicMock()
    mock_table = MagicMock()
    mock_sb.table.return_value = mock_table
    mock_table.upsert.return_value = mock_table
    mock_table.execute.return_value = MagicMock()

    rows = [
        {"numero_orden": "OP-001", "precio_unitario": 10.0, "instcartelno": "A"},
        {"numero_orden": "OP-002", "precio_unitario": 20.0, "instcartelno": "B"},
    ]
    count = upsert_ordenes_pedido(rows, mock_sb)
    assert count == 2
    mock_sb.table.assert_called_with("da_ordenes_pedido")
    call_args = mock_table.upsert.call_args
    assert "numero_orden" in str(call_args)


def test_upsert_ordenes_pedido_skips_rows_without_numero_orden():
    from datos_abiertos import upsert_ordenes_pedido
    mock_sb = MagicMock()
    rows = [
        {"numero_orden": None, "precio_unitario": 10.0},
        {"numero_orden": "",   "precio_unitario": 20.0},
    ]
    assert upsert_ordenes_pedido(rows, mock_sb) == 0


def test_upsert_ordenes_pedido_returns_zero_for_empty():
    from datos_abiertos import upsert_ordenes_pedido
    assert upsert_ordenes_pedido([], MagicMock()) == 0


def test_upsert_ordenes_pedido_returns_zero_on_db_error():
    from datos_abiertos import upsert_ordenes_pedido
    mock_sb = MagicMock()
    mock_table = MagicMock()
    mock_sb.table.return_value = mock_table
    mock_table.upsert.return_value = mock_table
    mock_table.execute.side_effect = Exception("DB error")

    rows = [{"numero_orden": "OP-001", "instcartelno": "2026CD-001-0031700001"}]
    result = upsert_ordenes_pedido(rows, mock_sb)
    assert result == 0


# ── parse_af_pricing_record fuente field ──────────────────────────────────────

def test_parse_af_pricing_record_includes_fuente_af():
    from datos_abiertos import parse_af_pricing_record
    row = {
        "CEDULA_PROVEEDOR":            "3101189270",
        "PRECIO_UNITARIO_ADJUDICADO":  "25",
        "CANTIDAD_ADJUDICADA":         "10",
    }
    r = parse_af_pricing_record(row, "2025LY-000006-0001102105")
    assert r is not None
    assert r["fuente"] == "AF"


# ── fetch_proveedores ──────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_fetch_proveedores_upserts_valid_rows():
    from datos_abiertos import fetch_proveedores

    supplier_records = [
        {"CEDULA": "3101111111", "NOMBRE": "Proveedor A S.A.", "TAMANO": "MEDIANO", "PROVINCIA": "San José"},
        {"CEDULA": "3101222222", "NOMBRE": "Proveedor B Ltda.", "TAMANO": "MICRO", "PROVINCIA": "Heredia"},
    ]
    zip_bytes = make_zip("proveedores.json", supplier_records)

    mock_sb = MagicMock()
    mock_table = MagicMock()
    mock_sb.table.return_value = mock_table
    mock_table.upsert.return_value = mock_table
    mock_table.execute.return_value = MagicMock()

    mock_create_resp = MagicMock()
    mock_create_resp.text = "proveedores_token.zip"
    mock_create_resp.raise_for_status = MagicMock()

    mock_dl_resp = MagicMock()
    mock_dl_resp.content = zip_bytes
    mock_dl_resp.raise_for_status = MagicMock()

    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=mock_create_resp)
    mock_client.get = AsyncMock(return_value=mock_dl_resp)

    with patch("datos_abiertos.httpx.AsyncClient") as mock_async_client:
        mock_async_client.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_async_client.return_value.__aexit__ = AsyncMock(return_value=False)
        count = await fetch_proveedores(mock_sb)

    assert count == 2
    mock_sb.table.assert_called_with("proveedores")
    upsert_call = mock_table.upsert.call_args
    assert upsert_call is not None
    rows = upsert_call[0][0]
    assert rows[0]["cedula"] == "3101111111"
    assert rows[0]["tamano"] == "MEDIANO"


@pytest.mark.asyncio
async def test_fetch_proveedores_skips_records_without_cedula():
    from datos_abiertos import fetch_proveedores

    supplier_records = [
        {"NOMBRE": "Sin cédula S.A."},               # no CEDULA → skip
        {"CEDULA": "3101333333", "NOMBRE": "OK"},     # valid
    ]
    zip_bytes = make_zip("proveedores.json", supplier_records)

    mock_sb = MagicMock()
    mock_table = MagicMock()
    mock_sb.table.return_value = mock_table
    mock_table.upsert.return_value = mock_table
    mock_table.execute.return_value = MagicMock()

    mock_create_resp = MagicMock()
    mock_create_resp.text = "token.zip"
    mock_create_resp.raise_for_status = MagicMock()

    mock_dl_resp = MagicMock()
    mock_dl_resp.content = zip_bytes
    mock_dl_resp.raise_for_status = MagicMock()

    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=mock_create_resp)
    mock_client.get = AsyncMock(return_value=mock_dl_resp)

    with patch("datos_abiertos.httpx.AsyncClient") as mock_async_client:
        mock_async_client.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_async_client.return_value.__aexit__ = AsyncMock(return_value=False)
        count = await fetch_proveedores(mock_sb)

    assert count == 1


# ── fetch_catalogo_bienes ──────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_fetch_catalogo_bienes_upserts_valid_rows():
    from datos_abiertos import fetch_catalogo_bienes

    catalog_records = [
        {
            "CODIGO_CLASIFICACION":       "42181500",
            "CODIGO_IDENTIFICACION":      "4218150000000001",
            "DESCRIPCION_CLASIFICACION":  "Artículos de anestesia",
            "DESCRIPCION_IDENTIFICACION": "Mascarillas anestésicas",
        },
    ]
    zip_bytes = make_zip("catalogo.json", catalog_records)

    mock_sb = MagicMock()
    mock_table = MagicMock()
    mock_sb.table.return_value = mock_table
    mock_table.upsert.return_value = mock_table
    mock_table.execute.return_value = MagicMock()

    mock_create_resp = MagicMock()
    mock_create_resp.text = "catalogo_token.zip"
    mock_create_resp.raise_for_status = MagicMock()

    mock_dl_resp = MagicMock()
    mock_dl_resp.content = zip_bytes
    mock_dl_resp.raise_for_status = MagicMock()

    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=mock_create_resp)
    mock_client.get = AsyncMock(return_value=mock_dl_resp)

    with patch("datos_abiertos.httpx.AsyncClient") as mock_async_client:
        mock_async_client.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_async_client.return_value.__aexit__ = AsyncMock(return_value=False)
        count = await fetch_catalogo_bienes("42000000", mock_sb)

    assert count == 1
    mock_sb.table.assert_called_with("catalogo_bienes")
    upsert_call = mock_table.upsert.call_args
    rows = upsert_call[0][0]
    assert rows[0]["codigo_identificacion"] == "4218150000000001"
    assert rows[0]["codigo_clasificacion"] == "42181500"


@pytest.mark.asyncio
async def test_fetch_catalogo_bienes_skips_records_without_codigo_identificacion():
    from datos_abiertos import fetch_catalogo_bienes

    catalog_records = [
        {"CODIGO_CLASIFICACION": "42181500"},  # no CODIGO_IDENTIFICACION → skip
    ]
    zip_bytes = make_zip("catalogo.json", catalog_records)

    mock_sb = MagicMock()
    mock_table = MagicMock()
    mock_sb.table.return_value = mock_table

    mock_create_resp = MagicMock()
    mock_create_resp.text = "token.zip"
    mock_create_resp.raise_for_status = MagicMock()

    mock_dl_resp = MagicMock()
    mock_dl_resp.content = zip_bytes
    mock_dl_resp.raise_for_status = MagicMock()

    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=mock_create_resp)
    mock_client.get = AsyncMock(return_value=mock_dl_resp)

    with patch("datos_abiertos.httpx.AsyncClient") as mock_async_client:
        mock_async_client.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_async_client.return_value.__aexit__ = AsyncMock(return_value=False)
        count = await fetch_catalogo_bienes("42000000", mock_sb)

    assert count == 0


# ── fetch_instituciones_compradoras ────────────────────────────────────────────

@pytest.mark.asyncio
async def test_fetch_instituciones_compradoras_inserts_valid_rows():
    from datos_abiertos import fetch_instituciones_compradoras

    inst_records = [
        {"NOMBRE_INSTITUCION": "Hospital Nacional de Niños", "PROVINCIA": "San José", "CANTON": "Central"},
        {"NOMBRE_INSTITUCION": "CCSS Central", "PROVINCIA": "San José"},
    ]
    zip_bytes = make_zip("instituciones.json", inst_records)

    mock_sb = MagicMock()
    mock_table = MagicMock()
    mock_sb.table.return_value = mock_table
    mock_table.insert.return_value = mock_table
    mock_table.execute.return_value = MagicMock()

    mock_create_resp = MagicMock()
    mock_create_resp.text = "ic_token.zip"
    mock_create_resp.raise_for_status = MagicMock()

    mock_dl_resp = MagicMock()
    mock_dl_resp.content = zip_bytes
    mock_dl_resp.raise_for_status = MagicMock()

    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=mock_create_resp)
    mock_client.get = AsyncMock(return_value=mock_dl_resp)

    with patch("datos_abiertos.httpx.AsyncClient") as mock_async_client:
        mock_async_client.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_async_client.return_value.__aexit__ = AsyncMock(return_value=False)
        count = await fetch_instituciones_compradoras(mock_sb)

    assert count == 2
    mock_sb.table.assert_called_with("instituciones_salud")


@pytest.mark.asyncio
async def test_fetch_instituciones_compradoras_skips_without_nombre():
    from datos_abiertos import fetch_instituciones_compradoras

    inst_records = [
        {"PROVINCIA": "San José"},  # no nombre → skip
    ]
    zip_bytes = make_zip("instituciones.json", inst_records)

    mock_sb = MagicMock()
    mock_create_resp = MagicMock()
    mock_create_resp.text = "token.zip"
    mock_create_resp.raise_for_status = MagicMock()

    mock_dl_resp = MagicMock()
    mock_dl_resp.content = zip_bytes
    mock_dl_resp.raise_for_status = MagicMock()

    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=mock_create_resp)
    mock_client.get = AsyncMock(return_value=mock_dl_resp)

    with patch("datos_abiertos.httpx.AsyncClient") as mock_async_client:
        mock_async_client.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_async_client.return_value.__aexit__ = AsyncMock(return_value=False)
        count = await fetch_instituciones_compradoras(mock_sb)

    assert count == 0


# ── run_datos_abiertos known_set reuse ────────────────────────────────────────

@pytest.mark.asyncio
async def test_run_datos_abiertos_scalar_filters_unknown_procedures():
    """
    SC rows whose instcartelno is not in licitaciones_medicas must NOT reach
    the upsert call — otherwise FK / NOT-NULL constraints blow up in prod.
    """
    from datos_abiertos import run_datos_abiertos

    KNOWN = "2026CD-001-KNOWN"
    UNKNOWN = "2026CD-999-NOTINDB"

    # Minimal raw SC rows — one known, one unknown
    # parse_sc_record reads NUMERO_PROCEDIMIENTO (not INST_CARTEL_NO)
    sc_raw = [
        {"NUMERO_PROCEDIMIENTO": KNOWN,   "PRESUPUESTO": "1000", "MONEDA": "CRC"},
        {"NUMERO_PROCEDIMIENTO": UNKNOWN, "PRESUPUESTO": "2000", "MONEDA": "USD"},
    ]

    mock_sb = MagicMock()
    mock_table = MagicMock()
    mock_sb.table.return_value = mock_table
    mock_table.select.return_value = mock_table
    mock_table.limit.return_value = mock_table
    mock_table.range.return_value = mock_table
    mock_table.upsert.return_value = mock_table
    mock_table.insert.return_value = mock_table
    mock_table.delete.return_value = mock_table
    mock_table.eq.return_value = mock_table
    mock_table.in_.return_value = mock_table

    # DB returns only KNOWN as a tracked procedure
    mock_table.execute.return_value = MagicMock(data=[{"instcartelno": KNOWN}])

    def fetch_side_effect(report_type, *args, **kwargs):
        return sc_raw if report_type == "SC" else []

    with patch("datos_abiertos.fetch_report", new_callable=AsyncMock, side_effect=fetch_side_effect):
        await run_datos_abiertos(dias=30, supabase_client=mock_sb)

    # Collect all rows passed to any upsert on licitaciones_medicas
    upsert_rows = []
    for call in mock_table.upsert.call_args_list:
        rows = call[0][0] if call[0] else call[1].get("json", [])
        if isinstance(rows, list):
            upsert_rows.extend(rows)

    upserted_keys = {r.get("instcartelno") for r in upsert_rows if isinstance(r, dict)}
    assert UNKNOWN not in upserted_keys, (
        f"Unknown procedure {UNKNOWN!r} reached the DB upsert — known_set not applied to scalar"
    )
