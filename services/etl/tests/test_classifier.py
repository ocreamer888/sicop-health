"""
Unit tests for the classifier module.

Tests the medical classification logic for SICOP items.
"""

import pytest
from classifier import clasificar, KEYWORDS_MEDICOS


class TestClasificar:
    """Test suite for the clasificar function."""

    # ============= Medical Items Tests =============

    def test_clasificar_medicamento_por_nombre(self):
        """Should classify as MEDICAMENTO when keywords in cartel_nm."""
        item = {
            "inst_cartel_no": "2024-001",
            "cartel_nm": "Compra de medicamentos genéricos",
            "inst_nm": "Hospital General"
        }
        
        result = clasificar(item)
        
        assert result is not None
        assert result["categoria"] == "MEDICAMENTO"
        assert result["inst_cartel_no"] == "2024-001"

    def test_clasificar_medicamento_por_institucion(self):
        """Should classify as medical when institution contains health keywords."""
        item = {
            "inst_cartel_no": "2024-002",
            "cartel_nm": "Compra de papelería",  # non-medical name
            "inst_nm": "Ministerio de Salud"      # medical institution
        }
        
        result = clasificar(item)
        
        assert result is not None
        # Institution match without specific category keywords = OTRO
        assert result["categoria"] == "OTRO"

    def test_clasificar_equipamiento(self):
        """Should classify as EQUIPAMIENTO for medical equipment."""
        item = {
            "inst_cartel_no": "2024-003",
            "cartel_nm": "Adquisición de tomógrafo de resonancia magnética",
            "inst_nm": "Hospital Nacional"
        }
        
        result = clasificar(item)
        
        assert result is not None
        assert result["categoria"] == "EQUIPAMIENTO"

    def test_clasificar_insumo(self):
        """Should classify as INSUMO for medical supplies."""
        item = {
            "inst_cartel_no": "2024-004",
            "cartel_nm": "Compra de jeringas y catéteres",
            "inst_nm": "Clínica San José"
        }
        
        result = clasificar(item)
        
        assert result is not None
        assert result["categoria"] == "INSUMO"

    def test_clasificar_servicio_salud(self):
        """Should classify as SERVICIO_SALUD when hospital keyword in name."""
        item = {
            "inst_cartel_no": "2024-005",
            "cartel_nm": "Servicios hospitalarios de mantenimiento",
            "inst_nm": "Ministerio de Obras Públicas"
        }
        
        result = clasificar(item)
        
        assert result is not None
        assert result["categoria"] == "SERVICIO_SALUD"

    def test_clasificar_vacuna(self):
        """Should classify vaccines as MEDICAMENTO."""
        item = {
            "inst_cartel_no": "2024-006",
            "cartel_nm": "Compra de vacunas contra influenza",
            "inst_nm": "CCSS"
        }
        
        result = clasificar(item)
        
        assert result is not None
        assert result["categoria"] == "MEDICAMENTO"

    def test_clasificar_antibiotico(self):
        """Should classify antibiotics as MEDICAMENTO."""
        item = {
            "inst_cartel_no": "2024-007",
            "cartel_nm": "Adquisición de antibióticos de amplio espectro",
            "inst_nm": "EBAIS Central"
        }
        
        result = clasificar(item)
        
        assert result is not None
        assert result["categoria"] == "MEDICAMENTO"

    # ============= Non-Medical Items Tests =============

    def test_clasificar_no_medical_returns_none(self):
        """Should return None for non-medical items."""
        item = {
            "inst_cartel_no": "2024-008",
            "cartel_nm": "Compra de mobiliario de oficina",
            "inst_nm": "Ministerio de Educación"
        }
        
        result = clasificar(item)
        
        assert result is None

    def test_clasificar_construccion_returns_none(self):
        """Should return None for construction items."""
        item = {
            "inst_cartel_no": "2024-009",
            "cartel_nm": "Construcción de edificio administrativo",
            "inst_nm": "Ministerio de Obras Públicas"
        }
        
        result = clasificar(item)
        
        assert result is None

    def test_clasificar_veiculos_returns_none(self):
        """Should return None for vehicle purchases."""
        item = {
            "inst_cartel_no": "2024-010",
            "cartel_nm": "Adquisición de vehículos para flota",
            "inst_nm": "Instituto Costarricense de Electricidad"
        }
        
        result = clasificar(item)
        
        assert result is None

    # ============= Edge Cases Tests =============

    def test_clasificar_case_insensitive(self):
        """Should be case insensitive when matching keywords."""
        item = {
            "inst_cartel_no": "2024-011",
            "cartel_nm": "COMPRA DE MEDICAMENTOS",  # uppercase
            "inst_nm": "hospital nacional"           # lowercase
        }
        
        result = clasificar(item)
        
        assert result is not None
        assert result["categoria"] == "MEDICAMENTO"

    def test_clasificar_accented_characters(self):
        """Should handle accented characters in keywords."""
        item = {
            "inst_cartel_no": "2024-012",
            "cartel_nm": "Compra de fármacos oncológicos",
            "inst_nm": "Hospital"
        }
        
        result = clasificar(item)
        
        assert result is not None
        assert result["categoria"] == "MEDICAMENTO"

    def test_clasificar_partial_match(self):
        """Should match partial words within longer strings."""
        item = {
            "inst_cartel_no": "2024-013",
            "cartel_nm": "Mantenimiento de ecógrafo veterinario",
            "inst_nm": "Universidad Nacional"
        }
        
        result = clasificar(item)
        
        assert result is not None
        assert result["categoria"] == "EQUIPAMIENTO"

    def test_clasificar_empty_strings(self):
        """Should handle empty strings gracefully."""
        item = {
            "inst_cartel_no": "2024-014",
            "cartel_nm": "",
            "inst_nm": ""
        }
        
        result = clasificar(item)
        
        assert result is None

    def test_clasificar_none_values(self):
        """Should handle None values gracefully."""
        item = {
            "inst_cartel_no": "2024-015",
            "cartel_nm": None,
            "inst_nm": None
        }
        
        result = clasificar(item)
        
        assert result is None

    def test_clasificar_preserves_all_fields(self):
        """Should preserve all original fields when classifying."""
        item = {
            "inst_cartel_no": "2024-016",
            "cartel_nm": "Compra de insulina",
            "inst_nm": "Caja Costarricense de Seguro Social",
            "extraField1": "value1",
            "extraField2": 12345,
            "extraField3": True
        }
        
        result = clasificar(item)
        
        assert result is not None
        assert result["inst_cartel_no"] == "2024-016"
        assert result["cartel_nm"] == "Compra de insulina"
        assert result["inst_nm"] == "Caja Costarricense de Seguro Social"
        assert result["extraField1"] == "value1"
        assert result["extraField2"] == 12345
        assert result["extraField3"] == True
        assert result["categoria"] == "MEDICAMENTO"

    def test_clasificar_otro_when_no_specific_category(self):
        """Should classify as OTRO when no specific category matches."""
        item = {
            "inst_cartel_no": "2024-017",
            "cartel_nm": "Compra de reactivos de laboratorio",
            "inst_nm": "IAFA"
        }
        
        result = clasificar(item)
        
        assert result is not None
        assert result["categoria"] == "OTRO"


class TestKeywordsMedicos:
    """Test suite for medical keywords list."""

    def test_keywords_list_not_empty(self):
        """Keywords list should not be empty."""
        assert len(KEYWORDS_MEDICOS) > 0

    def test_keywords_are_lowercase(self):
        """All keywords should be lowercase for consistent matching."""
        for keyword in KEYWORDS_MEDICOS:
            assert keyword == keyword.lower(), f"Keyword '{keyword}' is not lowercase"

    def test_keywords_no_duplicates(self):
        """Keywords list should not have duplicates."""
        unique_keywords = set(KEYWORDS_MEDICOS)
        assert len(unique_keywords) == len(KEYWORDS_MEDICOS), "Duplicate keywords found"
