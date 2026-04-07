"""
Testy jednostkowe dla klasy run_scrapper.
"""
import pytest
from unittest.mock import MagicMock, patch, call
from configparser import RawConfigParser


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _make_config(sections: list[dict]) -> RawConfigParser:
    """Buduje in-memory RawConfigParser na podstawie listy słowników sekcji."""
    config = RawConfigParser()
    for sec in sections:
        name = sec["section"]
        config.add_section(name)
        for key, value in sec.items():
            if key != "section":
                config.set(name, key, value)
    return config


# ─── Testy metody run() ───────────────────────────────────────────────────────

class TestRunScrapperRun:

    @patch("run_scrapper.RawConfigParser")
    def test_unknown_website_is_skipped(self, MockConfigParser):
        """Sekcja z nieobsługiwaną nazwą strony powinna być pominięta."""
        config = _make_config([
            {"section": "Unknown", "website_name": "unknown_site", "website_to_scrap": "http://x.com", "first_time": "False"},
        ])
        MockConfigParser.return_value = config

        from run_scrapper import run_scrapper, SCRAPPER_MAP
        rs = run_scrapper()

        # Żaden scraper nie powinien zostać wywołany
        with patch.dict("run_scrapper.SCRAPPER_MAP", {}, clear=True):
            rs.run()  # brak wyjątku = test przeszedł

    @patch("run_scrapper.RawConfigParser")
    def test_first_time_true_sets_flag_false_and_writes_config(self, MockConfigParser):
        """Gdy first_time=True scraper powinien zapisać config (first_time=False) i wywołać scrap(url, True)."""
        config = _make_config([
            {"section": "Pracuj", "website_name": "pracuj", "website_to_scrap": "http://pracuj.pl", "first_time": "True"},
        ])
        MockConfigParser.return_value = config

        mock_scrapper_instance = MagicMock()
        MockScrapperClass = MagicMock(return_value=mock_scrapper_instance)

        from run_scrapper import run_scrapper
        rs = run_scrapper()

        # Patchujemy open tylko w kontekście run_scrapper, żeby uniknąć
        # konfliktu z config.read() który też używa open.
        with patch("run_scrapper.open", create=True) as mock_open, \
             patch.dict("run_scrapper.SCRAPPER_MAP", {"pracuj": MockScrapperClass}):
            mock_open.return_value.__enter__ = MagicMock(return_value=MagicMock())
            mock_open.return_value.__exit__ = MagicMock(return_value=False)
            rs.run()

        assert config["Pracuj"]["first_time"] == "False"
        mock_open.assert_called_once_with("configs/websites.ini", 'w')
        mock_scrapper_instance.scrap.assert_called_once_with("http://pracuj.pl", True)

    @patch("run_scrapper.RawConfigParser")
    def test_first_time_false_calls_scrap_with_false(self, MockConfigParser):
        """Gdy first_time=False scraper powinien wywołać scrap(url, False) bez zapisu configu."""
        config = _make_config([
            {"section": "OLX", "website_name": "olx", "website_to_scrap": "http://olx.pl", "first_time": "False"},
        ])
        MockConfigParser.return_value = config

        mock_scrapper_instance = MagicMock()
        MockScrapperClass = MagicMock(return_value=mock_scrapper_instance)

        from run_scrapper import run_scrapper
        rs = run_scrapper()

        # Patchujemy open w kontekście modułu run_scrapper (nie builtins)
        # żeby przechwycić tylko zapis pliku configu (nie config.read).
        with patch("run_scrapper.open", create=True) as mock_open, \
             patch.dict("run_scrapper.SCRAPPER_MAP", {"olx": MockScrapperClass}):
            rs.run()
            mock_open.assert_not_called()

        mock_scrapper_instance.scrap.assert_called_once_with("http://olx.pl", False)

    @patch("run_scrapper.RawConfigParser")
    def test_multiple_sections_all_scraped(self, MockConfigParser):
        """Każda sekcja z obsługiwaną stroną powinna wywołać odpowiedni scraper."""
        config = _make_config([
            {"section": "Pracuj", "website_name": "pracuj",    "website_to_scrap": "http://pracuj.pl",  "first_time": "False"},
            {"section": "OLX",    "website_name": "olx",       "website_to_scrap": "http://olx.pl",     "first_time": "False"},
            {"section": "NFJ",    "website_name": "nofluffjobs","website_to_scrap": "http://nfj.pl",    "first_time": "False"},
        ])
        MockConfigParser.return_value = config

        mock_pracuj    = MagicMock()
        mock_olx       = MagicMock()
        mock_nofluff   = MagicMock()

        scrapper_map = {
            "pracuj":      MagicMock(return_value=mock_pracuj),
            "olx":         MagicMock(return_value=mock_olx),
            "nofluffjobs": MagicMock(return_value=mock_nofluff),
        }

        from run_scrapper import run_scrapper
        rs = run_scrapper()

        with patch.dict("run_scrapper.SCRAPPER_MAP", scrapper_map, clear=True):
            rs.run()

        mock_pracuj.scrap.assert_called_once_with("http://pracuj.pl", False)
        mock_olx.scrap.assert_called_once_with("http://olx.pl", False)
        mock_nofluff.scrap.assert_called_once_with("http://nfj.pl", False)

    @patch("run_scrapper.RawConfigParser")
    def test_empty_config_runs_without_error(self, MockConfigParser):
        """Pusty plik konfiguracyjny nie powinien powodować błędu."""
        config = RawConfigParser()
        MockConfigParser.return_value = config

        from run_scrapper import run_scrapper
        rs = run_scrapper()
        rs.run()  # brak wyjątku = test przeszedł

    @patch("run_scrapper.RawConfigParser")
    def test_all_supported_websites_in_scrapper_map(self, MockConfigParser):
        """Wszystkie obsługiwane serwisy muszą być obecne w SCRAPPER_MAP."""
        from run_scrapper import SCRAPPER_MAP

        expected = {"pracuj", "olx", "dla_studenta", "students_pl",
                    "nofluffjobs", "theitprotocol", "czy_jest_eldorado"}
        assert expected == set(SCRAPPER_MAP.keys())


# ─── Testy metody send_discord_info() ─────────────────────────────────────────

class TestRunScrapperSendDiscordInfo:

    @patch("run_scrapper.database_operations")
    @patch("run_scrapper.Generate_excel_file")
    def test_send_discord_info_calls_all_steps(self, MockExcel, MockDB):
        """send_discord_info powinien wywołać: create_excel_file, not_sended, get_added_today."""
        mock_db_instance    = MagicMock()
        mock_excel_instance = MagicMock()
        MockDB.return_value    = mock_db_instance
        MockExcel.return_value = mock_excel_instance

        mock_db_instance.excel_file_data.return_value = [("row1",), ("row2",)]

        from run_scrapper import run_scrapper
        rs = run_scrapper()
        rs.send_discord_info()

        mock_excel_instance.create_excel_file.assert_called_once_with(mock_db_instance.excel_file_data.return_value)
        mock_db_instance.not_sended.assert_called_once()
        mock_db_instance.get_added_today.assert_called_once()

    @patch("run_scrapper.database_operations")
    @patch("run_scrapper.Generate_excel_file")
    def test_send_discord_info_passes_correct_data(self, MockExcel, MockDB):
        """excel_file_data musi być przekazane do create_excel_file."""
        expected_data = [(1, "pracuj", "2024-01-01", "http://link.pl", "Dev", "Warszawa")]

        mock_db_instance    = MagicMock()
        mock_excel_instance = MagicMock()
        MockDB.return_value    = mock_db_instance
        MockExcel.return_value = mock_excel_instance

        mock_db_instance.excel_file_data.return_value = expected_data

        from run_scrapper import run_scrapper
        rs = run_scrapper()
        rs.send_discord_info()

        mock_excel_instance.create_excel_file.assert_called_once_with(expected_data)
