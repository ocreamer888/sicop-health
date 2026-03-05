# SICOP ETL Tests

This directory contains comprehensive tests for the SICOP ETL pipeline.

## Test Structure

```
tests/
├── conftest.py              # Shared fixtures and configuration
├── test_classifier.py       # Medical classification logic tests
├── test_parser.py           # CSV parsing and data cleaning tests
├── test_fetcher.py          # SICOP API integration tests
├── test_uploader.py         # Supabase upload tests
├── test_main.py             # ETL pipeline orchestration tests
└── README.md                # This file
```

## Test Types

### Unit Tests (70%)
Fast, isolated tests for individual functions:
- `test_classifier.py` - Medical keyword matching, categorization
- `test_parser.py` - Column normalization, data cleaning, amount parsing
- `test_uploader.py` - Supabase operations (with mocks)

### Integration Tests (20%)
Tests for component interactions:
- `test_fetcher.py` - HTTP API calls with mocked responses
- `test_main.py` - Full ETL pipeline flow

## Running Tests

### Run All Tests
```bash
cd services/etl
./run_tests.sh
```

### Run Only Unit Tests
```bash
./run_tests.sh -u
```

### Run Only Integration Tests
```bash
./run_tests.sh -i
```

### Run With Coverage
```bash
./run_tests.sh -c
```

### Run Directly with Pytest
```bash
# All tests
pytest tests/

# Unit tests only
pytest tests/ -m unit

# Integration tests only
pytest tests/ -m integration

# With coverage
pytest tests/ --cov=. --cov-report=html

# Verbose output
pytest tests/ -vv
```

## Test Coverage Targets

| Module | Target | Priority |
|--------|--------|----------|
| classifier.py | 90%+ | Critical - medical classification logic |
| parser.py | 85%+ | High - data quality |
| fetcher.py | 80%+ | Medium - external API |
| uploader.py | 80%+ | Medium - database operations |
| main.py | 75%+ | Medium - orchestration |

## Fixtures

Common test data is defined in `conftest.py`:
- `sample_sicop_publicada` - Sample publicada item
- `sample_sicop_adjudicada` - Sample adjudicada item
- `sample_sicop_modificada` - Sample modificada item
- `sample_non_medical_item` - Non-medical item (should be filtered)
- `mock_supabase_client` - Mocked Supabase client
- `sample_csv_content` - Sample CSV data

## Mocking Strategy

### External APIs
- `respx` is used to mock HTTP calls to SICOP API
- No real API calls during testing

### Database
- Supabase client is fully mocked
- Tests verify correct method calls without hitting real DB

### File System
- `tmp_path` fixture creates temporary files
- CSV parsing tests use real temporary files

## Adding New Tests

1. **Identify test type**: Unit vs Integration
2. **Use appropriate fixtures**: Import from conftest.py
3. **Follow naming**: `test_<function>_<scenario>`
4. **Add markers**: `@pytest.mark.unit` or `@pytest.mark.integration`
5. **Test edge cases**: Empty inputs, None values, errors

Example:
```python
import pytest
from classifier import clasificar

class TestClasificar:
    @pytest.mark.unit
    def test_clasificar_medicamento(self):
        item = {"cartelNm": "Compra de medicamentos", "instNm": "CCSS"}
        result = clasificar(item)
        assert result is not None
        assert result["categoria"] == "MEDICAMENTO"
```

## Continuous Integration

Tests should be run in CI/CD:
```yaml
# .github/workflows/test.yml (example)
- name: Run ETL Tests
  run: |
    cd services/etl
    pip install -r requirements.txt
    pytest tests/ --cov=. --cov-fail-under=75
```

## Debugging Failed Tests

1. **Run single test**: `pytest tests/test_classifier.py::TestClasificar::test_clasificar_medicamento -v`
2. **Show print statements**: `pytest tests/ -v -s`
3. **PDB debugger**: `pytest tests/ --pdb`
4. **Detailed traceback**: `pytest tests/ --tb=long`
