"""
Testy jednostkowe dla klasy database_operations.
"""
import pytest
import sqlite3
from unittest.mock import MagicMock, patch, call


# ─── check_duplicate ──────────────────────────────────────────────────────────

class TestCheckDuplicate:

    @patch("database_operations.sqlite3.connect")
    def test_returns_none_when_no_duplicate(self, mock_connect):
        """Gdy brak duplikatu (0 wierszy) funkcja powinna zwrócić None (implicit)."""
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_connect.return_value.__enter__ = MagicMock()
        mock_connect.return_value.cursor.return_value = mock_cursor
        mock_connect.return_value.commit = MagicMock()
        mock_connect.return_value.close  = MagicMock()

        from database_operations import database_operations
        db_ops = database_operations()
        result = db_ops.check_duplicate("http://unique-link.pl")

        assert result is None

    @patch("database_operations.sqlite3.connect")
    def test_returns_false_when_duplicate_exists(self, mock_connect):
        """Gdy duplikat istnieje (>0 wierszy) funkcja powinna zwrócić False."""
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [("http://link.pl", "Oferta tytul")]
        mock_connect.return_value.cursor.return_value = mock_cursor
        mock_connect.return_value.commit = MagicMock()
        mock_connect.return_value.close  = MagicMock()

        from database_operations import database_operations
        db_ops = database_operations()
        result = db_ops.check_duplicate("http://link.pl")

        assert result is False


# ─── add ──────────────────────────────────────────────────────────────────────

class TestAdd:

    @patch("database_operations.sqlite3.connect")
    def test_add_inserts_with_is_sended_0(self, mock_connect):
        """Metoda add() powinna wstawić rekord z isSended=0."""
        mock_cursor = MagicMock()
        mock_connect.return_value.cursor.return_value = mock_cursor
        mock_connect.return_value.commit = MagicMock()
        mock_connect.return_value.close  = MagicMock()

        from database_operations import database_operations
        db_ops = database_operations()
        db_ops.add("http://link.pl", "Tytuł oferty", "Warszawa", "pracuj")

        args = mock_cursor.execute.call_args
        sql, data = args[0]
        assert "INSERT INTO" in sql
        assert data == ("pracuj", "http://link.pl", "Tytuł oferty", "Warszawa", 0)

    @patch("database_operations.sqlite3.connect")
    def test_add_calls_commit_and_close(self, mock_connect):
        """add() musi wywołać commit() i close()."""
        mock_cursor = MagicMock()
        mock_db = MagicMock()
        mock_db.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_db

        from database_operations import database_operations
        db_ops = database_operations()
        db_ops.add("http://link.pl", "Tytuł", "Kraków", "olx")

        mock_db.commit.assert_called_once()
        mock_db.close.assert_called_once()


# ─── add_first_time ──────────────────────────────────────────────────────────

class TestAddFirstTime:

    @patch("database_operations.sqlite3.connect")
    def test_add_first_time_inserts_with_is_sended_1(self, mock_connect):
        """add_first_time() powinien wstawić rekord z isSended=1."""
        mock_cursor = MagicMock()
        mock_connect.return_value.cursor.return_value = mock_cursor
        mock_connect.return_value.commit = MagicMock()
        mock_connect.return_value.close  = MagicMock()

        from database_operations import database_operations
        db_ops = database_operations()
        db_ops.add_first_time("http://link.pl", "Tytuł oferty", "Wrocław", "nofluffjobs")

        args = mock_cursor.execute.call_args
        sql, data = args[0]
        assert "INSERT INTO" in sql
        assert data[-1] == 1   # isSended powinno być 1


# ─── excel_file_data ──────────────────────────────────────────────────────────

class TestExcelFileData:

    @patch("database_operations.sqlite3.connect")
    @patch("database_operations.date")
    def test_returns_rows_from_db(self, mock_date, mock_connect):
        """excel_file_data() powinien zwrócić rekordy z bazy z dzisiejszą datą."""
        mock_date.today.return_value = MagicMock()
        mock_date.today.return_value.__str__ = MagicMock(return_value="2024-01-01")

        expected = [(1, "pracuj", "2024-01-01 10:00:00", "http://link.pl", "Oferta", "Gdańsk")]
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = expected
        mock_db = MagicMock()
        mock_db.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_db

        from database_operations import database_operations
        db_ops = database_operations()
        result = db_ops.excel_file_data()

        assert result == expected

    @patch("database_operations.sqlite3.connect")
    @patch("database_operations.date")
    def test_returns_empty_when_no_data(self, mock_date, mock_connect):
        """excel_file_data() powinien zwrócić pustą listę gdy brak rekordów."""
        mock_date.today.return_value = MagicMock()
        mock_date.today.return_value.__str__ = MagicMock(return_value="2024-01-01")

        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_db = MagicMock()
        mock_db.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_db

        from database_operations import database_operations
        db_ops = database_operations()
        result = db_ops.excel_file_data()

        assert result == []
