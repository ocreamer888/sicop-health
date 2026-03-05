"""
Integration tests for the fetcher module.

Tests HTTP API interactions with mocked responses using respx.
"""

import pytest
import respx
from httpx import Response
from datetime import datetime, timedelta
from fetcher import fetch_all, fetch_sicop, build_payload, BASE_API, HEADERS, ENDPOINTS


class TestBuildPayload:
    """Test suite for build_payload function."""

    def test_build_payload_basic(self):
        """Should build correct payload structure."""
        fecha_desde = datetime(2024, 3, 1, 0, 0, 0)
        fecha_hasta = datetime(2024, 3, 5, 0, 0, 0)
        
        payload = build_payload(fecha_desde, fecha_hasta, "RPT_PUB", 0, 100)
        
        assert payload["pageNumber"] == 0
        assert payload["pageSize"] == 100
        assert payload["tableSorter"]["order"] == "desc"
        assert payload["formFilters"][0]["field"] == "bgnYmd"
        assert payload["formFilters"][1]["field"] == "endYmd"
        assert payload["formFilters"][2]["field"] == "typeKey"
        assert payload["formFilters"][2]["value"] == "RPT_PUB"

    def test_build_payload_date_format(self):
        """Should format dates correctly in ISO format."""
        fecha_desde = datetime(2024, 3, 1, 12, 30, 45)
        fecha_hasta = datetime(2024, 3, 5, 23, 59, 59)
        
        payload = build_payload(fecha_desde, fecha_hasta, "RPT_ADJ")
        
        assert payload["formFilters"][0]["value"] == "2024-03-01T12:30:45.000Z"
        assert payload["formFilters"][1]["value"] == "2024-03-05T23:59:59.000Z"

    def test_build_payload_page_number(self):
        """Should include correct page number."""
        fecha_desde = datetime(2024, 3, 1)
        fecha_hasta = datetime(2024, 3, 5)
        
        payload = build_payload(fecha_desde, fecha_hasta, "RPT_MOD", page=5)
        
        assert payload["pageNumber"] == 5

    def test_build_payload_page_size(self):
        """Should include correct page size."""
        fecha_desde = datetime(2024, 3, 1)
        fecha_hasta = datetime(2024, 3, 5)
        
        payload = build_payload(fecha_desde, fecha_hasta, "RPT_PUB", page_size=50)
        
        assert payload["pageSize"] == 50


class TestFetchAll:
    """Test suite for fetch_all function."""

    @pytest.fixture
    def sample_api_response(self):
        """Sample paginated API response."""
        return {
            "content": [
                {"instCartelNo": "2024-001", "cartelNm": "Item 1"},
                {"instCartelNo": "2024-002", "cartelNm": "Item 2"}
            ],
            "totalElements": 2,
            "totalPages": 1,
            "pageable": {"pageNumber": 0, "pageSize": 100}
        }

    @pytest.fixture
    def multi_page_response(self):
        """Sample multi-page API response."""
        return {
            "content": [
                {"instCartelNo": f"2024-{i:03d}", "cartelNm": f"Item {i}"}
                for i in range(1, 101)  # 100 items
            ],
            "totalElements": 250,
            "totalPages": 3,
            "pageable": {"pageNumber": 0, "pageSize": 100}
        }

    @respx.mock
    async def test_fetch_all_single_page(self, sample_api_response):
        """Should fetch all items from single page."""
        # Mock the endpoint
        route = respx.post(ENDPOINTS["publicadas"]).mock(return_value=Response(200, json=sample_api_response))
        
        fecha_desde = datetime(2024, 3, 1)
        fecha_hasta = datetime(2024, 3, 5)
        
        result = await fetch_all("publicadas", fecha_desde, fecha_hasta)
        
        assert len(result) == 2
        assert result[0]["instCartelNo"] == "2024-001"
        assert result[1]["instCartelNo"] == "2024-002"
        assert route.called

    @respx.mock
    async def test_fetch_all_multiple_pages(self, multi_page_response):
        """Should fetch items across multiple pages."""
        # First page response
        page1 = {**multi_page_response, "pageable": {"pageNumber": 0, "pageSize": 100}}
        
        # Second page response
        page2_items = [{"instCartelNo": f"2024-{i:03d}", "cartelNm": f"Item {i}"} for i in range(101, 201)]
        page2 = {
            "content": page2_items,
            "totalElements": 250,
            "totalPages": 3,
            "pageable": {"pageNumber": 1, "pageSize": 100}
        }
        
        # Third page response
        page3_items = [{"instCartelNo": f"2024-{i:03d}", "cartelNm": f"Item {i}"} for i in range(201, 251)]
        page3 = {
            "content": page3_items,
            "totalElements": 250,
            "totalPages": 3,
            "pageable": {"pageNumber": 2, "pageSize": 100}
        }
        
        # Mock endpoint to return different responses based on page
        def side_effect(request):
            import json
            body = json.loads(request.content)
            page = body.get("pageNumber", 0)
            if page == 0:
                return Response(200, json=page1)
            elif page == 1:
                return Response(200, json=page2)
            else:
                return Response(200, json=page3)
        
        route = respx.post(ENDPOINTS["adjudicadas"]).mock(side_effect=side_effect)
        
        fecha_desde = datetime(2024, 3, 1)
        fecha_hasta = datetime(2024, 3, 5)
        
        result = await fetch_all("adjudicadas", fecha_desde, fecha_hasta)
        
        # Should have fetched all items across all pages
        assert len(result) == 250
        assert route.call_count == 3

    @respx.mock
    async def test_fetch_all_empty_response(self):
        """Should handle empty response gracefully."""
        empty_response = {
            "content": [],
            "totalElements": 0,
            "totalPages": 0,
            "pageable": {"pageNumber": 0, "pageSize": 100}
        }
        
        route = respx.post(ENDPOINTS["modificadas"]).mock(return_value=Response(200, json=empty_response))
        
        fecha_desde = datetime(2024, 3, 1)
        fecha_hasta = datetime(2024, 3, 5)
        
        result = await fetch_all("modificadas", fecha_desde, fecha_hasta)
        
        assert len(result) == 0
        assert result == []

    @respx.mock
    async def test_fetch_all_http_error(self):
        """Should handle HTTP errors."""
        route = respx.post(ENDPOINTS["publicadas"]).mock(return_value=Response(500, text="Internal Server Error"))
        
        fecha_desde = datetime(2024, 3, 1)
        fecha_hasta = datetime(2024, 3, 5)
        
        with pytest.raises(Exception):
            await fetch_all("publicadas", fecha_desde, fecha_hasta)

    @respx.mock
    async def test_fetch_all_correct_headers(self, sample_api_response):
        """Should send correct headers."""
        route = respx.post(ENDPOINTS["publicadas"]).mock(return_value=Response(200, json=sample_api_response))
        
        fecha_desde = datetime(2024, 3, 1)
        fecha_hasta = datetime(2024, 3, 5)
        
        await fetch_all("publicadas", fecha_desde, fecha_hasta)
        
        request = route.calls[0].request
        assert request.headers["Content-Type"] == "application/json"
        assert request.headers["Accept"] == "application/json"
        assert request.headers["Origin"] == "https://www.sicop.go.cr"
        assert request.headers["Referer"] == "https://www.sicop.go.cr/"

    @respx.mock
    async def test_fetch_all_correct_payload(self, sample_api_response):
        """Should send correct payload structure."""
        route = respx.post(ENDPOINTS["adjudicadas"]).mock(return_value=Response(200, json=sample_api_response))
        
        fecha_desde = datetime(2024, 3, 1, 0, 0, 0)
        fecha_hasta = datetime(2024, 3, 5, 0, 0, 0)
        
        await fetch_all("adjudicadas", fecha_desde, fecha_hasta)
        
        request = route.calls[0].request
        import json
        payload = json.loads(request.content)
        
        assert payload["pageNumber"] == 0
        assert payload["pageSize"] == 100
        assert payload["formFilters"][0]["field"] == "bgnYmd"
        assert payload["formFilters"][2]["value"] == "RPT_ADJ"


class TestFetchSicop:
    """Test suite for fetch_sicop function."""

    @pytest.fixture
    def single_item_response(self):
        """Sample response with single item."""
        return {
            "content": [{"instCartelNo": "2024-001", "cartelNm": "Test"}],
            "totalElements": 1,
            "totalPages": 1,
            "pageable": {"pageNumber": 0, "pageSize": 100}
        }

    @respx.mock
    async def test_fetch_sicop_all_types(self, single_item_response):
        """Should fetch all three types (publicadas, adjudicadas, modificadas)."""
        # Mock all three endpoints
        route_pub = respx.post(ENDPOINTS["publicadas"]).mock(return_value=Response(200, json=single_item_response))
        route_adj = respx.post(ENDPOINTS["adjudicadas"]).mock(return_value=Response(200, json=single_item_response))
        route_mod = respx.post(ENDPOINTS["modificadas"]).mock(return_value=Response(200, json=single_item_response))
        
        result = await fetch_sicop(dias_atras=1)
        
        assert "publicadas" in result
        assert "adjudicadas" in result
        assert "modificadas" in result
        assert len(result["publicadas"]) == 1
        assert len(result["adjudicadas"]) == 1
        assert len(result["modificadas"]) == 1

    @respx.mock
    async def test_fetch_sicop_date_range(self, single_item_response):
        """Should calculate correct date range."""
        from freezegun import freeze_time
        
        # Freeze time for consistent testing
        with freeze_time("2024-03-05 12:00:00"):
            # Mock all three endpoints
            route_pub = respx.post(ENDPOINTS["publicadas"]).mock(return_value=Response(200, json=single_item_response))
            route_adj = respx.post(ENDPOINTS["adjudicadas"]).mock(return_value=Response(200, json=single_item_response))
            route_mod = respx.post(ENDPOINTS["modificadas"]).mock(return_value=Response(200, json=single_item_response))
            
            await fetch_sicop(dias_atras=3)
            
            request = route_pub.calls[0].request
            import json
            payload = json.loads(request.content)
            
            # Should request data from 2024-03-02 to 2024-03-05
            assert "2024-03-02" in payload["formFilters"][0]["value"]  # bgnYmd
            assert "2024-03-05" in payload["formFilters"][1]["value"]  # endYmd

    @respx.mock
    async def test_fetch_sicop_default_days(self, single_item_response):
        """Should default to 1 day back."""
        from freezegun import freeze_time
        
        with freeze_time("2024-03-05 12:00:00"):
            # Mock all three endpoints
            route_pub = respx.post(ENDPOINTS["publicadas"]).mock(return_value=Response(200, json=single_item_response))
            route_adj = respx.post(ENDPOINTS["adjudicadas"]).mock(return_value=Response(200, json=single_item_response))
            route_mod = respx.post(ENDPOINTS["modificadas"]).mock(return_value=Response(200, json=single_item_response))
            
            await fetch_sicop()  # No argument
            
            request = route_pub.calls[0].request
            import json
            payload = json.loads(request.content)
            
            # Should request data from yesterday (2024-03-04)
            assert "2024-03-04" in payload["formFilters"][0]["value"]

    @respx.mock
    async def test_fetch_sicop_returns_dict(self, single_item_response):
        """Should return dict with three keys."""
        respx.post(ENDPOINTS["publicadas"]).mock(return_value=Response(200, json=single_item_response))
        respx.post(ENDPOINTS["adjudicadas"]).mock(return_value=Response(200, json=single_item_response))
        respx.post(ENDPOINTS["modificadas"]).mock(return_value=Response(200, json=single_item_response))
        
        result = await fetch_sicop(dias_atras=1)
        
        assert isinstance(result, dict)
        assert set(result.keys()) == {"publicadas", "adjudicadas", "modificadas"}


class TestFetcherConfiguration:
    """Test suite for fetcher constants and configuration."""

    def test_base_api_url(self):
        """BASE_API should be correct SICOP URL."""
        assert BASE_API == "https://prod-api.sicop.go.cr/bid/api/v1/public"

    def test_endpoints_structure(self):
        """ENDPOINTS should have all three types."""
        assert set(ENDPOINTS.keys()) == {"publicadas", "adjudicadas", "modificadas"}
        
        for url in ENDPOINTS.values():
            assert url.startswith(BASE_API)
            assert "/epCartelReleaseAdjuMod/" in url

    def test_headers_structure(self):
        """HEADERS should have required fields."""
        required_headers = ["Content-Type", "Accept", "Origin", "Referer"]
        
        for header in required_headers:
            assert header in HEADERS

    def test_headers_content_type(self):
        """Content-Type should be application/json."""
        assert HEADERS["Content-Type"] == "application/json"
