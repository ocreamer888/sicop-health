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
        return {"SC": [sc_record], "DC": [dc_record], "O": [o_record], "AF": [af_record]}[report_key]

    mock_sb = MagicMock()
    mock_table = MagicMock()
    mock_sb.table.return_value = mock_table
    mock_table.upsert.return_value = mock_table
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
        return {"SC": [sc_record], "DC": [dc_record], "O": [o_record], "AF": [af_record]}[report_key]

    mock_sb = MagicMock()
    mock_table = MagicMock()
    mock_sb.table.return_value = mock_table
    mock_table.upsert.return_value = mock_table
    mock_table.select.return_value = mock_table
    mock_table.limit.return_value = mock_table
    mock_table.execute.return_value = MagicMock(data=[{"instcartelno": "2026LD-000001-0031700001"}])

    with patch("datos_abiertos.fetch_report", side_effect=mock_fetch):
        stats = await run_datos_abiertos(dias=7, supabase_client=mock_sb)

    assert "AF" in call_order
    assert "adjudicaciones" in stats
    assert stats["adjudicaciones"] >= 0
