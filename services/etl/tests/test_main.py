"""
Integration tests for the main ETL pipeline.

Tests the full ETL flow with mocked dependencies.
"""

import pytest
from unittest.mock import patch, AsyncMock, MagicMock


class TestMainETLPipeline:
    """Test suite for the main ETL pipeline orchestration."""

    @pytest.fixture
    def mock_fetch_result(self):
        """Sample data returned from fetch_sicop."""
        return {
            "publicadas": [
                {"instCartelNo": "2024-001", "cartelNm": "Medicamentos", "instNm": "CCSS", "typeKey": "RPT_PUB"},
                {"instCartelNo": "2024-002", "cartelNm": "Papelería", "instNm": "MINED", "typeKey": "RPT_PUB"},
            ],
            "adjudicadas": [
                {"instCartelNo": "2024-003", "cartelNm": "Tomógrafo", "instNm": "Hospital", "typeKey": "RPT_ADJ"}
            ],
            "modificadas": [
                {"instCartelNo": "2024-004", "cartelNm": "Insumos médicos modificados", "instNm": "CCSS", "typeKey": "RPT_MOD"}
            ],
        }

    @pytest.mark.asyncio
    async def test_etl_pipeline_happy_path(self, mock_fetch_result):
        """Should run complete ETL pipeline successfully."""
        from main import run

        with patch("main.fetch_sicop", new_callable=AsyncMock) as mock_fetch, \
             patch("main.parse_batch") as mock_parse, \
             patch("main.clasificar", return_value=None), \
             patch("main.upsert_licitaciones") as mock_upsert, \
             patch("main.insert_modificaciones") as mock_insert, \
             patch("main.run_datos_abiertos", new_callable=AsyncMock) as mock_da:

            mock_fetch.return_value = mock_fetch_result
            mock_parse.return_value = []
            mock_da.return_value = {"scalar": 0, "ofertas": 0, "adjudicaciones": 0}

            await run(dias_atras=3)

            mock_fetch.assert_called_once_with(dias_atras=3)
            # parse_batch called for publicadas, adjudicadas, modificadas
            assert mock_parse.call_count == 3
            # upsert called for publicadas and adjudicadas
            assert mock_upsert.call_count == 2
            # insert called for modificadas
            mock_insert.assert_called_once()

    @pytest.mark.asyncio
    async def test_etl_pipeline_empty_fetch(self):
        """Should handle empty API response gracefully."""
        from main import run

        empty_data = {"publicadas": [], "adjudicadas": [], "modificadas": []}

        with patch("main.fetch_sicop", new_callable=AsyncMock) as mock_fetch, \
             patch("main.parse_batch", return_value=[]), \
             patch("main.upsert_licitaciones"), \
             patch("main.insert_modificaciones"), \
             patch("main.run_datos_abiertos", new_callable=AsyncMock) as mock_da:

            mock_fetch.return_value = empty_data
            mock_da.return_value = {"scalar": 0, "ofertas": 0, "adjudicaciones": 0}

            await run()

            mock_fetch.assert_called_once()

    @pytest.mark.asyncio
    async def test_etl_pipeline_handles_fetch_error(self):
        """Should propagate fetch errors (no try/except wraps fetch_sicop)."""
        from main import run

        with patch("main.fetch_sicop", new_callable=AsyncMock) as mock_fetch:
            mock_fetch.side_effect = Exception("API Error")

            with pytest.raises(Exception, match="API Error"):
                await run()

    @pytest.mark.asyncio
    async def test_etl_es_medica_flag_set(self, mock_fetch_result):
        """Items classified as medical should have es_medica=True in upsert payload."""
        from main import run

        captured = []

        def capture_upsert(rows):
            captured.extend(rows)

        with patch("main.fetch_sicop", new_callable=AsyncMock) as mock_fetch, \
             patch("main.parse_batch") as mock_parse, \
             patch("main.clasificar") as mock_clasificar, \
             patch("main.upsert_licitaciones", side_effect=capture_upsert), \
             patch("main.insert_modificaciones"), \
             patch("main.run_datos_abiertos", new_callable=AsyncMock) as mock_da:

            mock_fetch.return_value = mock_fetch_result
            mock_da.return_value = {"scalar": 0, "ofertas": 0, "adjudicaciones": 0}

            def _parsed_items(raw, type_key):
                return [
                    {"inst_cartel_no": i["instCartelNo"], "cartel_nm": i["cartelNm"],
                     "inst_nm": i["instNm"], "type_key": type_key,
                     "es_medica": False, "categoria": None}
                    for i in raw
                ]

            mock_parse.side_effect = _parsed_items

            def _classify(item):
                if item["inst_cartel_no"] == "2024-001":
                    return {**item, "es_medica": True, "categoria": "MEDICAMENTO"}
                return None

            mock_clasificar.side_effect = _classify

            await run(dias_atras=3)

        all_keys = {r["inst_cartel_no"] for r in captured}
        assert "2024-001" in all_keys
        medical = next(r for r in captured if r["inst_cartel_no"] == "2024-001")
        assert medical["es_medica"] is True

    @pytest.mark.asyncio
    async def test_etl_da_failure_is_non_fatal(self, mock_fetch_result):
        """DA enrichment errors should be caught and not abort the main ETL run."""
        from main import run

        with patch("main.fetch_sicop", new_callable=AsyncMock) as mock_fetch, \
             patch("main.parse_batch", return_value=[]), \
             patch("main.clasificar", return_value=None), \
             patch("main.upsert_licitaciones"), \
             patch("main.insert_modificaciones"), \
             patch("main.run_datos_abiertos", new_callable=AsyncMock) as mock_da:

            mock_fetch.return_value = mock_fetch_result
            mock_da.side_effect = Exception("DA server down")

            # Should complete without raising
            await run(dias_atras=3)


class TestMainModule:
    """Test suite for main module structure."""

    def test_run_function_exists(self):
        """run() function should be defined."""
        from main import run
        assert callable(run)

    def test_main_imports(self):
        """Should be able to import main module."""
        import main
        assert hasattr(main, "run")

    def test_async_run(self):
        """run() should be an async function."""
        import inspect
        from main import run
        assert inspect.iscoroutinefunction(run)
