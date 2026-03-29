"""
Unit tests for the uploader module.

Tests Supabase upload operations with mocked client.
"""

import pytest
from unittest.mock import MagicMock, patch
from uploader import upsert_licitaciones, insert_modificaciones, get_supabase_client


class TestUpsertLicitaciones:
    """Test suite for upsert_licitaciones function."""

    @pytest.fixture
    def mock_supabase(self):
        """Create a mocked Supabase client chain matching actual upsert call pattern."""
        mock_client = MagicMock()
        mock_table = MagicMock()
        mock_upsert = MagicMock()
        mock_execute = MagicMock()

        mock_client.table.return_value = mock_table
        mock_table.upsert.return_value = mock_upsert
        mock_upsert.execute = mock_execute
        # make response.data non-None so _exec_upsert doesn't short-circuit
        mock_execute.return_value.data = []

        return {
            "client": mock_client,
            "table": mock_table,
            "upsert": mock_upsert,
            "execute": mock_execute,
        }

    def test_upsert_licitaciones_success(self, mock_supabase, sample_sicop_publicada):
        """Should call upsert on the licitaciones_medicas table."""
        with patch("uploader.get_supabase_client", return_value=mock_supabase["client"]):
            upsert_licitaciones([sample_sicop_publicada])

        mock_supabase["client"].table.assert_called_with("licitaciones_medicas")
        mock_supabase["table"].upsert.assert_called_once()

    def test_upsert_licitaciones_uses_instcartelno_conflict(self, mock_supabase, sample_sicop_publicada):
        """Should use instcartelno as the on_conflict key."""
        with patch("uploader.get_supabase_client", return_value=mock_supabase["client"]):
            upsert_licitaciones([sample_sicop_publicada])

        call_kwargs = mock_supabase["table"].upsert.call_args[1]
        assert call_kwargs["on_conflict"] == "instcartelno"

    def test_upsert_licitaciones_empty_list(self, mock_supabase):
        """Should not call Supabase for empty list."""
        with patch("uploader.get_supabase_client", return_value=mock_supabase["client"]):
            upsert_licitaciones([])

        mock_supabase["client"].table.assert_not_called()

    def test_upsert_licitaciones_none_input(self, mock_supabase):
        """Should handle None input gracefully."""
        with patch("uploader.get_supabase_client", return_value=mock_supabase["client"]):
            upsert_licitaciones(None)

        mock_supabase["client"].table.assert_not_called()

    def test_upsert_licitaciones_multiple_rows(self, mock_supabase, sample_sicop_publicada, sample_sicop_adjudicada):
        """Should upsert multiple rows in one call."""
        with patch("uploader.get_supabase_client", return_value=mock_supabase["client"]):
            upsert_licitaciones([sample_sicop_publicada, sample_sicop_adjudicada])

        mock_supabase["table"].upsert.assert_called_once()

    def test_upsert_licitaciones_swallows_db_errors(self, mock_supabase, sample_sicop_publicada):
        """upsert errors are caught and logged, not re-raised."""
        mock_supabase["execute"].side_effect = Exception("DB error")

        with patch("uploader.get_supabase_client", return_value=mock_supabase["client"]):
            # Should NOT raise
            upsert_licitaciones([sample_sicop_publicada])


class TestInsertModificaciones:
    """Test suite for insert_modificaciones function."""

    @pytest.fixture
    def mock_supabase(self):
        """Create a mocked Supabase client chain for insert."""
        mock_client = MagicMock()
        mock_table = MagicMock()
        mock_insert = MagicMock()
        mock_execute = MagicMock()

        mock_client.table.return_value = mock_table
        mock_table.insert.return_value = mock_insert
        mock_insert.execute = mock_execute
        mock_execute.return_value.data = []

        return {
            "client": mock_client,
            "table": mock_table,
            "insert": mock_insert,
            "execute": mock_execute,
        }

    def test_insert_modificaciones_success(self, mock_supabase, sample_sicop_modificada):
        """Should insert into licitaciones_modificaciones table."""
        with patch("uploader.get_supabase_client", return_value=mock_supabase["client"]):
            insert_modificaciones([sample_sicop_modificada])

        mock_supabase["client"].table.assert_called_once_with("licitaciones_modificaciones")
        mock_supabase["table"].insert.assert_called_once()
        call_args = mock_supabase["table"].insert.call_args[0][0]
        assert len(call_args) == 1
        assert call_args[0]["inst_cartel_no"] == "2024-003"

    def test_insert_modificaciones_empty_list(self, mock_supabase):
        """Should not call Supabase for empty list."""
        with patch("uploader.get_supabase_client", return_value=mock_supabase["client"]):
            insert_modificaciones([])

        mock_supabase["client"].table.assert_not_called()

    def test_insert_modificaciones_multiple_rows(self, mock_supabase, sample_sicop_modificada):
        """Should insert all rows in one call."""
        rows = [
            sample_sicop_modificada,
            {**sample_sicop_modificada, "inst_cartel_no": "2024-006"},
        ]
        with patch("uploader.get_supabase_client", return_value=mock_supabase["client"]):
            insert_modificaciones(rows)

        call_args = mock_supabase["table"].insert.call_args[0][0]
        assert len(call_args) == 2

    def test_insert_modificaciones_uses_insert_not_upsert(self, mock_supabase, sample_sicop_modificada):
        """Should use insert (not upsert) — modificaciones allow duplicates."""
        with patch("uploader.get_supabase_client", return_value=mock_supabase["client"]):
            insert_modificaciones([sample_sicop_modificada])

        mock_supabase["table"].insert.assert_called_once()
        assert not mock_supabase["table"].upsert.called

    def test_insert_modificaciones_allows_repeated_calls(self, mock_supabase, sample_sicop_modificada):
        """Calling insert twice should result in two DB calls."""
        with patch("uploader.get_supabase_client", return_value=mock_supabase["client"]):
            insert_modificaciones([sample_sicop_modificada])
            insert_modificaciones([sample_sicop_modificada])

        assert mock_supabase["table"].insert.call_count == 2

    def test_insert_modificaciones_swallows_db_errors(self, mock_supabase, sample_sicop_modificada):
        """Insert errors are caught and logged, not re-raised."""
        mock_supabase["execute"].side_effect = Exception("DB error")

        with patch("uploader.get_supabase_client", return_value=mock_supabase["client"]):
            # Should NOT raise
            insert_modificaciones([sample_sicop_modificada])


class TestGetSupabaseClient:
    """Test suite for get_supabase_client function."""

    @patch.dict("os.environ", {"SUPABASE_URL": "https://test.supabase.co", "SUPABASE_KEY": "test-key"})
    @patch("uploader.create_client")
    def test_get_supabase_client_creates_client(self, mock_create_client):
        """Should create client using env vars."""
        mock_create_client.return_value = MagicMock()
        import uploader
        uploader._supabase_client = None

        client = get_supabase_client()

        mock_create_client.assert_called_once()
        assert client is not None

    @patch.dict("os.environ", {}, clear=True)
    def test_get_supabase_client_missing_env_raises(self):
        """Should raise RuntimeError when env vars are missing."""
        import uploader
        uploader._supabase_client = None

        with pytest.raises(RuntimeError, match="SUPABASE_URL"):
            get_supabase_client()

    @patch.dict("os.environ", {"SUPABASE_URL": "https://test.supabase.co", "SUPABASE_KEY": "test-key"})
    @patch("uploader.create_client")
    def test_get_supabase_client_returns_singleton(self, mock_create_client):
        """Should return the same client instance on repeated calls."""
        mock_create_client.return_value = MagicMock()
        import uploader
        uploader._supabase_client = None

        client1 = get_supabase_client()
        client2 = get_supabase_client()

        assert client1 is client2
        mock_create_client.assert_called_once()
