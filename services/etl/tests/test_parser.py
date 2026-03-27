"""
Unit tests for the parser module.

Tests API item normalization via parse_item / parse_batch.
CSV/pandas functions (parse_csv, clean_dataframe, etc.) are internal/legacy
and are not tested here.
"""

import pytest
from parser import parse_batch


class TestParseBatch:
    """Test suite for parse_batch — API data normalization."""

    def test_parse_batch_empty_list(self):
        """Should return empty list for empty input."""
        result = parse_batch([], "RPT_PUB")
        assert result == []

    def test_parse_batch_single_item_key_mapping(self):
        """Should map camelCase API keys to snake_case output schema."""
        items = [{
            "instCartelNo": "2024-001",
            "cartelNm": "Compra de medicamentos",
            "instNm": "CCSS",
        }]

        result = parse_batch(items, "RPT_PUB")

        assert len(result) == 1
        r = result[0]
        assert r["inst_cartel_no"] == "2024-001"
        assert r["cartel_nm"] == "Compra de medicamentos"
        assert r["inst_nm"] == "CCSS"

    def test_parse_batch_type_key_passed_through(self):
        """type_key argument should appear in each output row."""
        items = [{"instCartelNo": "2024-001", "cartelNm": "Test"}]

        for type_key in ("RPT_PUB", "RPT_ADJ", "RPT_MOD"):
            result = parse_batch(items, type_key)
            assert result[0]["type_key"] == type_key

    def test_parse_batch_multiple_items(self):
        """Should parse every item in the input list."""
        items = [
            {"instCartelNo": "2024-001", "cartelNm": "Item 1", "instNm": "CCSS"},
            {"instCartelNo": "2024-002", "cartelNm": "Item 2", "instNm": "Hospital"},
            {"instCartelNo": "2024-003", "cartelNm": "Item 3", "instNm": "MINSAL"},
        ]

        result = parse_batch(items, "RPT_PUB")

        assert len(result) == 3
        assert result[0]["inst_cartel_no"] == "2024-001"
        assert result[1]["inst_cartel_no"] == "2024-002"
        assert result[2]["inst_cartel_no"] == "2024-003"

    def test_parse_batch_es_medica_defaults_false(self):
        """Parsed items should have es_medica=False until classifier enriches them."""
        items = [{"instCartelNo": "2024-001", "cartelNm": "Medicamentos"}]

        result = parse_batch(items, "RPT_PUB")

        assert result[0]["es_medica"] is False

    def test_parse_batch_categoria_defaults_none(self):
        """Parsed items should have categoria=None until classifier enriches them."""
        items = [{"instCartelNo": "2024-001", "cartelNm": "Medicamentos"}]

        result = parse_batch(items, "RPT_PUB")

        assert result[0]["categoria"] is None

    def test_parse_batch_amount_mapped(self):
        """amt field should be extracted from API estBidAmt (via detalle or direct)."""
        items = [{"instCartelNo": "2024-001", "cartelNm": "Test", "amt": 1500000}]

        result = parse_batch(items, "RPT_PUB")

        assert result[0]["amt"] == 1500000

    def test_parse_batch_supplier_fields(self):
        """Supplier name and code should be mapped."""
        items = [{
            "instCartelNo": "2024-001",
            "cartelNm": "Test",
            "supplierNm": "Farmacia ABC",
            "supplierCd": "3101234567",
        }]

        result = parse_batch(items, "RPT_ADJ")

        assert result[0]["supplier_nm"] == "Farmacia ABC"
        assert result[0]["supplier_cd"] == "3101234567"

    def test_parse_batch_date_fields(self):
        """Date fields should be mapped by name."""
        items = [{
            "instCartelNo": "2024-001",
            "cartelNm": "Test",
            "biddocStartDt": "2024-03-01",
            "biddocEndDt": "2024-03-15",
            "openbidDt": "2024-03-20",
        }]

        result = parse_batch(items, "RPT_PUB")

        assert result[0]["biddoc_start_dt"] == "2024-03-01"
        assert result[0]["biddoc_end_dt"] == "2024-03-15"
        assert result[0]["openbid_dt"] == "2024-03-20"

    def test_parse_batch_missing_optional_fields_are_none(self):
        """Output should have None for unmapped optional fields."""
        items = [{"instCartelNo": "2024-001", "cartelNm": "Minimal item"}]

        result = parse_batch(items, "RPT_PUB")

        r = result[0]
        assert r["inst_cartel_no"] == "2024-001"
        assert r["inst_nm"] is None
        assert r["supplier_nm"] is None

    def test_parse_batch_null_cartel_nm(self):
        """None cartelNm should be preserved as None."""
        items = [{"instCartelNo": "2024-001", "cartelNm": None, "instNm": "CCSS"}]

        result = parse_batch(items, "RPT_PUB")

        assert result[0]["inst_cartel_no"] == "2024-001"
        assert result[0]["cartel_nm"] is None

    def test_parse_batch_raw_data_preserved(self):
        """Original API item should be stored in raw_data."""
        original = {"instCartelNo": "2024-001", "cartelNm": "Test", "extraField": "value"}
        result = parse_batch([original], "RPT_PUB")

        assert result[0]["raw_data"] == original

    def test_parse_batch_returns_new_list(self):
        """Should return a new list without mutating the input."""
        original = [{"instCartelNo": "2024-001", "cartelNm": "Test"}]

        result = parse_batch(original, "RPT_PUB")

        assert result is not original
        assert "inst_cartel_no" not in original[0]
