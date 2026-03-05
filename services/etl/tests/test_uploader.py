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
        """Create a fully mocked Supabase chain."""
        mock_client = MagicMock()
        mock_table = MagicMock()
        mock_upsert = MagicMock()
        mock_execute = MagicMock()
        
        # Build the chain: client.table() -> table.upsert() -> upsert.on_conflict() -> upsert.execute()
        mock_client.table.return_value = mock_table
        mock_table.upsert.return_value = mock_upsert
        mock_upsert.on_conflict.return_value = mock_upsert  # Returns self for chaining
        mock_upsert.execute = mock_execute
        
        return {
            'client': mock_client,
            'table': mock_table,
            'upsert': mock_upsert,
            'execute': mock_execute
        }

    def test_upsert_licitaciones_success(self, mock_supabase, sample_sicop_publicada):
        """Should successfully upsert licitaciones with mapped fields."""
        with patch('uploader.get_supabase_client', return_value=mock_supabase['client']):
            rows = [sample_sicop_publicada]
            upsert_licitaciones(rows)
            
            # Verify the chain was called
            mock_supabase['client'].table.assert_called_once_with("licitaciones_medicas")
            mock_supabase['table'].upsert.assert_called_once()
            # Verify on_conflict is numero_procedimiento (mapped from inst_cartel_no)
            call_kwargs = mock_supabase['table'].upsert.call_args[1]
            assert call_kwargs['on_conflict'] == "numero_procedimiento"
            mock_supabase['execute'].assert_called_once()

    def test_upsert_licitaciones_empty_list(self, mock_supabase):
        """Should not call Supabase for empty list."""
        with patch('uploader.get_supabase_client', return_value=mock_supabase['client']):
            upsert_licitaciones([])
            
            # Should not call anything
            mock_supabase['client'].table.assert_not_called()

    def test_upsert_licitaciones_multiple_rows(self, mock_supabase, sample_sicop_publicada, sample_sicop_adjudicada):
        """Should upsert multiple rows in one call with mapped fields."""
        with patch('uploader.get_supabase_client', return_value=mock_supabase['client']):
            rows = [sample_sicop_publicada, sample_sicop_adjudicada]
            upsert_licitaciones(rows)
            
            mock_supabase['table'].upsert.assert_called_once()
            call_kwargs = mock_supabase['table'].upsert.call_args[1]
            assert call_kwargs['on_conflict'] == "numero_procedimiento"

    def test_upsert_licitaciones_handles_error(self, mock_supabase, sample_sicop_publicada):
        """Should propagate errors from Supabase."""
        mock_supabase['execute'].side_effect = Exception("Supabase error")
        
        with patch('uploader.get_supabase_client', return_value=mock_supabase['client']):
            with pytest.raises(Exception, match="Supabase error"):
                upsert_licitaciones([sample_sicop_publicada])

    def test_upsert_licitaciones_conflict_resolution(self, mock_supabase, sample_sicop_publicada):
        """Should use numero_procedimiento for conflict resolution (mapped from inst_cartel_no)."""
        with patch('uploader.get_supabase_client', return_value=mock_supabase['client']):
            upsert_licitaciones([sample_sicop_publicada])
            
            # Verify on_conflict parameter uses DB column name
            call_args = mock_supabase['table'].upsert.call_args
            assert call_args[1]['on_conflict'] == "numero_procedimiento"

    def test_upsert_licitaciones_none_input(self, mock_supabase):
        """Should handle None input gracefully."""
        with patch('uploader.get_supabase_client', return_value=mock_supabase['client']):
            # Empty list or None should not call Supabase
            upsert_licitaciones(None)
            
            mock_supabase['client'].table.assert_not_called()


class TestInsertModificaciones:
    """Test suite for insert_modificaciones function."""

    @pytest.fixture
    def mock_supabase(self):
        """Create a fully mocked Supabase chain."""
        mock_client = MagicMock()
        mock_table = MagicMock()
        mock_insert = MagicMock()
        mock_execute = MagicMock()
        
        # Build the chain: client.table() -> table.insert() -> insert.execute()
        mock_client.table.return_value = mock_table
        mock_table.insert.return_value = mock_insert
        mock_insert.execute = mock_execute
        
        return {
            'client': mock_client,
            'table': mock_table,
            'insert': mock_insert,
            'execute': mock_execute
        }

    def test_insert_modificaciones_success(self, mock_supabase, sample_sicop_modificada):
        """Should successfully insert modificaciones with mapped fields."""
        with patch('uploader.get_supabase_client', return_value=mock_supabase['client']):
            rows = [sample_sicop_modificada]
            insert_modificaciones(rows)
            
            # Verify the chain was called
            mock_supabase['client'].table.assert_called_once_with("licitaciones_modificaciones")
            mock_supabase['table'].insert.assert_called_once()
            # Verify data is transformed (inst_cartel_no should be in mapped data)
            call_args = mock_supabase['table'].insert.call_args[0][0]
            assert len(call_args) == 1
            assert call_args[0]['inst_cartel_no'] == '2024-003'
            mock_supabase['execute'].assert_called_once()

    def test_insert_modificaciones_empty_list(self, mock_supabase):
        """Should not call Supabase for empty list."""
        with patch('uploader.get_supabase_client', return_value=mock_supabase['client']):
            insert_modificaciones([])
            
            mock_supabase['client'].table.assert_not_called()

    def test_insert_modificaciones_multiple_rows(self, mock_supabase, sample_sicop_modificada):
        """Should insert multiple rows with mapped fields."""
        with patch('uploader.get_supabase_client', return_value=mock_supabase['client']):
            rows = [
                sample_sicop_modificada,
                {**sample_sicop_modificada, "inst_cartel_no": "2024-006"}
            ]
            insert_modificaciones(rows)
            
            mock_supabase['table'].insert.assert_called_once()
            call_args = mock_supabase['table'].insert.call_args[0][0]
            assert len(call_args) == 2
            assert call_args[0]['inst_cartel_no'] == '2024-003'
            assert call_args[1]['inst_cartel_no'] == '2024-006'

    def test_insert_modificaciones_no_upsert(self, mock_supabase, sample_sicop_modificada):
        """Should NOT use upsert for modificaciones (always insert)."""
        with patch('uploader.get_supabase_client', return_value=mock_supabase['client']):
            insert_modificaciones([sample_sicop_modificada])
            
            # Should use insert, not upsert
            mock_supabase['table'].insert.assert_called_once()
            assert not mock_supabase['table'].upsert.called

    def test_insert_modificaciones_handles_error(self, mock_supabase, sample_sicop_modificada):
        """Should propagate errors from Supabase."""
        mock_supabase['execute'].side_effect = Exception("Database error")
        
        with patch('uploader.get_supabase_client', return_value=mock_supabase['client']):
            with pytest.raises(Exception, match="Database error"):
                insert_modificaciones([sample_sicop_modificada])

    def test_insert_modificaciones_allows_duplicates(self, mock_supabase, sample_sicop_modificada):
        """Insert should allow duplicate rows (no conflict resolution)."""
        with patch('uploader.get_supabase_client', return_value=mock_supabase['client']):
            # Insert same item twice (simulating two modificaciones for same licitacion)
            row = sample_sicop_modificada
            insert_modificaciones([row])
            insert_modificaciones([row])  # Should not raise
            
            # Both calls should succeed
            assert mock_supabase['table'].insert.call_count == 2


class TestGetSupabaseClient:
    """Test suite for get_supabase_client function."""

    @patch.dict('os.environ', {
        'SUPABASE_URL': 'https://test.supabase.co',
        'SUPABASE_KEY': 'test-key'
    })
    @patch('uploader.create_client')
    def test_get_supabase_client_creates_client(self, mock_create_client):
        """Should create client with env vars."""
        mock_create_client.return_value = MagicMock()
        
        # Reset the singleton
        import uploader
        uploader._supabase_client = None
        
        client = get_supabase_client()
        
        mock_create_client.assert_called_once_with(
            'https://test.supabase.co',
            'test-key'
        )
        assert client is not None

    @patch.dict('os.environ', {}, clear=True)
    def test_get_supabase_client_missing_env_raises(self):
        """Should raise error when env vars missing."""
        # Reset the singleton
        import uploader
        uploader._supabase_client = None
        
        with pytest.raises(RuntimeError, match="SUPABASE_URL and SUPABASE_KEY"):
            get_supabase_client()

    @patch.dict('os.environ', {
        'SUPABASE_URL': 'https://test.supabase.co',
        'SUPABASE_KEY': 'test-key'
    })
    @patch('uploader.create_client')
    def test_get_supabase_client_returns_singleton(self, mock_create_client):
        """Should return same client instance (singleton)."""
        mock_create_client.return_value = MagicMock()
        
        # Reset the singleton
        import uploader
        uploader._supabase_client = None
        
        client1 = get_supabase_client()
        client2 = get_supabase_client()
        
        assert client1 is client2
        mock_create_client.assert_called_once()


class TestUploaderEnvironment:
    """Test suite for uploader environment setup."""

    def test_supabase_client_function_exists(self):
        """Should be able to import get_supabase_client."""
        from uploader import get_supabase_client
        assert callable(get_supabase_client)

    def test_required_env_vars(self):
        """Should document required env vars."""
        import os
        
        # Check if env vars are set (they may not be in test environment)
        url = os.environ.get('SUPABASE_URL')
        key = os.environ.get('SUPABASE_KEY')
        
        # If both are set, uploader should work
        # If not, it's okay for unit tests (we mock it)
        if url and key:
            assert url.startswith('http')
            assert len(key) > 0
