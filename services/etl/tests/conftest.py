"""
Pytest fixtures and configuration for ETL tests.
"""

import pytest
from datetime import datetime
from unittest.mock import MagicMock, AsyncMock


# ============= Sample Data Fixtures =============

@pytest.fixture
def sample_sicop_publicada():
    """Sample publicada item from SICOP API."""
    return {
        "inst_cartel_no": "2024-001",
        "cartel_nm": "Compra de medicamentos para hospital",
        "inst_nm": "Caja Costarricense de Seguro Social",
        "pubYmd": "2024-03-01T00:00:00.000Z",
        "bidYmd": "2024-03-15T00:00:00.000Z",
        "curCd": "CRC",
        "estBidAmt": 1500000.00,
        "cartelTypeCd": "PUBLIC",
        "typeKey": "RPT_PUB"
    }


@pytest.fixture
def sample_sicop_adjudicada():
    """Sample adjudicada item from SICOP API."""
    return {
        "inst_cartel_no": "2024-002",
        "cartel_nm": "Adquisición de tomógrafo",
        "inst_nm": "Hospital Nacional",
        "pubYmd": "2024-02-01T00:00:00.000Z",
        "adjYmd": "2024-02-20T00:00:00.000Z",
        "curCd": "USD",
        "estBidAmt": 250000.00,
        "cartelTypeCd": "ADJ",
        "typeKey": "RPT_ADJ",
        "adjAmt": 245000.00,
        "cntrAmt": 1
    }


@pytest.fixture
def sample_sicop_modificada():
    """Sample modificada item from SICOP API."""
    return {
        "inst_cartel_no": "2024-003",
        "cartel_nm": "Modificación compra insumos médicos",
        "inst_nm": "Ministerio de Salud",
        "pubYmd": "2024-01-15T00:00:00.000Z",
        "modYmd": "2024-03-05T00:00:00.000Z",
        "curCd": "CRC",
        "estBidAmt": 500000.00,
        "cartelTypeCd": "MOD",
        "typeKey": "RPT_MOD",
        "modDesc": "Prórroga de fecha límite"
    }


@pytest.fixture
def sample_non_medical_item():
    """Sample non-medical item that should be filtered out."""
    return {
        "inst_cartel_no": "2024-004",
        "cartel_nm": "Compra de papelería de oficina",
        "inst_nm": "Ministerio de Educación",
        "pubYmd": "2024-03-01T00:00:00.000Z",
        "bidYmd": "2024-03-15T00:00:00.000Z",
        "curCd": "CRC",
        "estBidAmt": 50000.00,
        "cartelTypeCd": "PUBLIC",
        "typeKey": "RPT_PUB"
    }


@pytest.fixture
def sample_api_response_publicadas():
    """Sample paginated API response for publicadas."""
    return {
        "content": [
            {
                "inst_cartel_no": "2024-001",
                "cartel_nm": "Compra de medicamentos",
                "inst_nm": "CCSS",
                "pubYmd": "2024-03-01T00:00:00.000Z",
                "bidYmd": "2024-03-15T00:00:00.000Z",
                "curCd": "CRC",
                "estBidAmt": 1500000.00,
                "cartelTypeCd": "PUBLIC",
                "typeKey": "RPT_PUB"
            },
            {
                "inst_cartel_no": "2024-005",
                "cartel_nm": "Contrucción de edificio",
                "inst_nm": "Institución Pública",
                "pubYmd": "2024-03-01T00:00:00.000Z",
                "bidYmd": "2024-03-15T00:00:00.000Z",
                "curCd": "CRC",
                "estBidAmt": 50000000.00,
                "cartelTypeCd": "PUBLIC",
                "typeKey": "RPT_PUB"
            }
        ],
        "totalElements": 2,
        "totalPages": 1,
        "pageable": {
            "pageNumber": 0,
            "pageSize": 100
        }
    }


@pytest.fixture
def sample_csv_content():
    """Sample CSV content for parser testing."""
    return """numero_procedimiento,descripcion,institucion,tipo_procedimiento,clasificacion_unspsc,monto_colones,adjudicatario,estado,fecha_tramite,fecha_limite_oferta
2024-001,Compra de medicamentos,CCSS,Licitación Pública,512312,1500000.00,Farmacia ABC,Publicada,01/03/2024,15/03/2024
2024-002,Adquisición de equipos médicos,Hospital Nacional,Contratación Directe,421612,2500000.00,MedTech SA,Adjudicada,15/02/2024,28/02/2024
"""


# ============= Mock Fixtures =============

@pytest.fixture
def mock_supabase_client():
    """Create a mocked Supabase client."""
    mock_client = MagicMock()
    
    # Mock table operations
    mock_table = MagicMock()
    mock_client.table.return_value = mock_table
    
    # Mock upsert/insert chains
    mock_upsert = MagicMock()
    mock_insert = MagicMock()
    mock_execute = MagicMock()
    
    mock_table.upsert.return_value = mock_upsert
    mock_table.insert.return_value = mock_insert
    mock_upsert.execute = mock_execute
    mock_insert.execute = mock_execute
    mock_upsert.on_conflict = MagicMock(return_value=mock_upsert)
    
    return mock_client


@pytest.fixture
def mock_httpx_client():
    """Create a mocked httpx AsyncClient."""
    mock_client = AsyncMock()
    return mock_client


@pytest.fixture
def mock_datetime_now():
    """Fixed datetime for consistent testing."""
    return datetime(2024, 3, 5, 12, 0, 0)
