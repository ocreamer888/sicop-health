"""
Integration tests for the main ETL pipeline.

Tests the full ETL flow with mocked dependencies.
"""

import pytest
from unittest.mock import patch, AsyncMock, MagicMock
import asyncio


class TestMainETLPipeline:
    """Test suite for the main ETL pipeline orchestration."""

    @pytest.fixture(autouse=True)
    def setup_imports(self):
        """Ensure main module can be imported by adding parse_batch to parser."""
        # Import will succeed now that parse_batch exists in parser.py
        pass

    @pytest.fixture
    def mock_fetch_result(self):
        """Sample data returned from fetch_sicop."""
        return {
            "publicadas": [
                {"instCartelNo": "2024-001", "cartelNm": "Medicamentos", "instNm": "CCSS", "typeKey": "RPT_PUB"},
                {"instCartelNo": "2024-002", "cartelNm": "Papelería", "instNm": "MINED", "typeKey": "RPT_PUB"}
            ],
            "adjudicadas": [
                {"instCartelNo": "2024-003", "cartelNm": "Tomógrafo", "instNm": "Hospital", "typeKey": "RPT_ADJ"}
            ],
            "modificadas": [
                {"instCartelNo": "2024-004", "cartelNm": "Insumos médicos modificados", "instNm": "CCSS", "typeKey": "RPT_MOD"}
            ]
        }

    @pytest.fixture
    def mock_parsed_items(self):
        """Sample parsed items with snake_case fields (after parse_batch)."""
        return {
            "RPT_PUB": [
                {"inst_cartel_no": "2024-001", "cartel_nm": "Medicamentos", "inst_nm": "CCSS", "type_key": "RPT_PUB"},
                {"inst_cartel_no": "2024-002", "cartel_nm": "Papelería", "inst_nm": "MINED", "type_key": "RPT_PUB"}
            ],
            "RPT_ADJ": [
                {"inst_cartel_no": "2024-003", "cartel_nm": "Tomógrafo", "inst_nm": "Hospital", "type_key": "RPT_ADJ"}
            ],
            "RPT_MOD": [
                {"inst_cartel_no": "2024-004", "cartel_nm": "Insumos médicos modificados", "inst_nm": "CCSS", "type_key": "RPT_MOD"}
            ]
        }

    @pytest.mark.asyncio
    async def test_etl_pipeline_happy_path(self, mock_fetch_result, mock_parsed_items):
        """Should run complete ETL pipeline successfully."""
        from main import run
        
        # Mock all dependencies
        with patch('main.fetch_sicop', new_callable=AsyncMock) as mock_fetch, \
             patch('main.parse_batch') as mock_parse, \
             patch('main.clasificar') as mock_clasificar, \
             patch('main.upsert_licitaciones') as mock_upsert, \
             patch('main.insert_modificaciones') as mock_insert:
            
            # Setup mocks
            mock_fetch.return_value = mock_fetch_result
            mock_parse.side_effect = lambda data, type_key: mock_parsed_items[type_key]
            
            # Clasificar returns medical items with category, None for non-medical
            # Note: uses snake_case fields (cartel_nm) after parse_batch
            def mock_classify(item):
                cartel_nm = item.get("cartel_nm", "").lower()
                if "medicamento" in cartel_nm or \
                   "tomógrafo" in cartel_nm or \
                   "insumo" in cartel_nm:
                    return {**item, "categoria": "MEDICAMENTO" if "medicamento" in cartel_nm else "EQUIPAMIENTO"}
                return None
            
            mock_clasificar.side_effect = mock_classify
            
            # Run the pipeline
            await run()
            
            # Verify fetch was called (using dias_atras=3 from smoke test)
            mock_fetch.assert_called_once_with(dias_atras=3)
            
            # Verify parse was called for each type
            assert mock_parse.call_count == 3  # publicadas, adjudicadas, modificadas
            
            # Verify upsert was called for publicadas and adjudicadas
            assert mock_upsert.call_count == 2
            
            # Verify insert was called for modificadas
            mock_insert.assert_called_once()

    @pytest.mark.asyncio
    async def test_etl_pipeline_no_medical_items(self):
        """Should handle case where no medical items found."""
        from main import run
        
        non_medical_data = {
            "publicadas": [{"instCartelNo": "2024-001", "cartelNm": "Papelería", "instNm": "MINED", "typeKey": "RPT_PUB"}],
            "adjudicadas": [],
            "modificadas": []
        }
        
        with patch('main.fetch_sicop', new_callable=AsyncMock) as mock_fetch, \
             patch('main.parse_batch') as mock_parse, \
             patch('main.clasificar', return_value=None) as mock_clasificar, \
             patch('main.upsert_licitaciones') as mock_upsert, \
             patch('main.insert_modificaciones') as mock_insert:
            
            mock_fetch.return_value = non_medical_data
            mock_parse.return_value = [{"inst_cartel_no": "2024-001", "cartel_nm": "Papelería", "inst_nm": "MINED", "type_key": "RPT_PUB"}]
            
            await run()
            
            # Should still upsert all items with es_medica=False
            mock_upsert.assert_called()
            # Should not insert modificaciones (empty after filtering)
            mock_insert.assert_called_once()  # Called but with empty list

    @pytest.mark.asyncio
    async def test_etl_pipeline_empty_fetch(self):
        """Should handle empty API response gracefully."""
        from main import run
        
        empty_data = {
            "publicadas": [],
            "adjudicadas": [],
            "modificadas": []
        }
        
        with patch('main.fetch_sicop', new_callable=AsyncMock) as mock_fetch, \
             patch('main.parse_batch', return_value=[]) as mock_parse, \
             patch('main.upsert_licitaciones') as mock_upsert, \
             patch('main.insert_modificaciones') as mock_insert:
            
            mock_fetch.return_value = empty_data
            
            await run()
            
            # Should not crash with empty data
            mock_fetch.assert_called_once()

    @pytest.mark.asyncio
    async def test_etl_pipeline_handles_fetch_error(self):
        """Should handle fetch errors gracefully."""
        from main import run
        
        with patch('main.fetch_sicop', new_callable=AsyncMock) as mock_fetch:
            mock_fetch.side_effect = Exception("API Error")
            
            with pytest.raises(Exception, match="API Error"):
                await run()

    @pytest.mark.asyncio
    async def test_etl_es_medica_flag_set(self, mock_fetch_result, mock_parsed_items):
        """Should set es_medica flag on all items."""
        from main import run
        
        with patch('main.fetch_sicop', new_callable=AsyncMock) as mock_fetch, \
             patch('main.parse_batch') as mock_parse, \
             patch('main.clasificar') as mock_clasificar, \
             patch('main.upsert_licitaciones') as mock_upsert, \
             patch('main.insert_modificaciones') as mock_insert:
            
            mock_fetch.return_value = mock_fetch_result
            mock_parse.side_effect = lambda data, type_key: mock_parsed_items[type_key]
            
            # First item is medical, second is not
            def mock_classify(item):
                if item["inst_cartel_no"] == "2024-001":
                    return {**item, "categoria": "MEDICAMENTO"}
                if item["inst_cartel_no"] == "2024-003":
                    return {**item, "categoria": "EQUIPAMIENTO"}
                if item["inst_cartel_no"] == "2024-004":
                    return {**item, "categoria": "INSUMO"}
                return None
            
            mock_clasificar.side_effect = mock_classify
            
            await run()
            
            # Check that upsert was called with items that have es_medica flag
            for call in mock_upsert.call_args_list:
                rows = call[0][0]  # First positional argument
                for row in rows:
                    assert "es_medica" in row
                    if row["inst_cartel_no"] in ["2024-001", "2024-003"]:
                        assert row["es_medica"] == True
                    else:
                        assert row["es_medica"] == False

    @pytest.mark.asyncio
    async def test_etl_only_medical_modifications_inserted(self, mock_fetch_result, mock_parsed_items):
        """Should only insert medical modificaciones."""
        from main import run
        
        with patch('main.fetch_sicop', new_callable=AsyncMock) as mock_fetch, \
             patch('main.parse_batch') as mock_parse, \
             patch('main.clasificar') as mock_clasificar, \
             patch('main.upsert_licitaciones') as mock_upsert, \
             patch('main.insert_modificaciones') as mock_insert:
            
            mock_fetch.return_value = mock_fetch_result
            mock_parse.side_effect = lambda data, type_key: mock_parsed_items[type_key]
            
            # Only modificadas with insumos is medical (using snake_case)
            def mock_classify(item):
                if "insumo" in item.get("cartel_nm", "").lower():
                    return {**item, "categoria": "INSUMO"}
                return None
            
            mock_clasificar.side_effect = mock_classify
            
            await run()
            
            # Insert should be called only with medical modificaciones
            mock_insert.assert_called_once()
            inserted_rows = mock_insert.call_args[0][0]
            
            # All inserted rows should be medical (non-medical filtered out)
            for row in inserted_rows:
                assert "categoria" in row


class TestMainModule:
    """Test suite for main module structure."""

    def test_run_function_exists(self):
        """run() function should be defined."""
        from main import run
        assert callable(run)

    def test_main_imports(self):
        """Should be able to import main module."""
        try:
            import main
            assert hasattr(main, 'run')
        except ImportError as e:
            pytest.fail(f"Failed to import main module: {e}")

    def test_async_run(self):
        """run() should be an async function."""
        import inspect
        from main import run
        
        assert inspect.iscoroutinefunction(run)
