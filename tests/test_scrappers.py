"""
Testy jednostkowe dla scraperów (wspólna logika scrap()).

Każdy scraper powinien:
 - wywołać add_first_time() gdy first=True
 - wywołać add() gdy first=False i link nie jest duplikatem
 - NIE wywołać add() gdy first=False i link jest duplikatem
 - obsłużyć błąd HTTP bez rzucania wyjątku wyżej (tam gdzie jest try/except)
"""
import pytest
from unittest.mock import MagicMock, patch
import bs4


# ─── Pomocny HTML ─────────────────────────────────────────────────────────────

PRACUJ_HTML = """
<div data-test="default-offer">
    <a data-test="link-offer" href="https://pracuj.pl/oferta/123">
        <span data-test="offer-title">Python Developer</span>
    </a>
    <span data-test="text-region">Warszawa</span>
</div>
"""

OLX_HTML = """
<div data-cy="l-card">
    <a href="/oferta/programista-123">Python Dev</a>
    <h4>Python Developer</h4>
    <span>Kraków</span>
</div>
"""


# ─── pracuj_pl_scrapper ───────────────────────────────────────────────────────

class TestPracujPlScrapper:

    def _make_mock_response(self, html: str, status=200):
        response = MagicMock()
        response.text = html
        response.status_code = status
        response.raise_for_status = MagicMock()
        return response

    @patch("class_folder.pracuj_pl_scrapper.database_operations")
    @patch("class_folder.pracuj_pl_scrapper.cloudscraper.create_scraper")
    def test_first_time_calls_add_first_time(self, mock_create_scraper, MockDB):
        """Przy first=True powinien wywołać add_first_time."""
        mock_scraper = MagicMock()
        mock_scraper.get.return_value = self._make_mock_response(PRACUJ_HTML)
        mock_create_scraper.return_value = mock_scraper

        mock_db_instance = MagicMock()
        MockDB.return_value = mock_db_instance

        from class_folder.pracuj_pl_scrapper import pracuj_pl_scrapper
        s = pracuj_pl_scrapper()
        s.scrap("http://pracuj.pl", True)

        mock_db_instance.add_first_time.assert_called_once()
        mock_db_instance.add.assert_not_called()

    @patch("class_folder.pracuj_pl_scrapper.database_operations")
    @patch("class_folder.pracuj_pl_scrapper.cloudscraper.create_scraper")
    def test_not_first_time_calls_add_when_no_duplicate(self, mock_create_scraper, MockDB):
        """Przy first=False i braku duplikatu powinien wywołać add."""
        mock_scraper = MagicMock()
        mock_scraper.get.return_value = self._make_mock_response(PRACUJ_HTML)
        mock_create_scraper.return_value = mock_scraper

        mock_db_instance = MagicMock()
        mock_db_instance.check_duplicate.return_value = None  # brak duplikatu
        MockDB.return_value = mock_db_instance

        from class_folder.pracuj_pl_scrapper import pracuj_pl_scrapper
        s = pracuj_pl_scrapper()
        s.scrap("http://pracuj.pl", False)

        mock_db_instance.add.assert_called_once()

    @patch("class_folder.pracuj_pl_scrapper.database_operations")
    @patch("class_folder.pracuj_pl_scrapper.cloudscraper.create_scraper")
    def test_not_first_time_skips_add_when_duplicate(self, mock_create_scraper, MockDB):
        """Przy first=False i duplikacie NIE powinien wywołać add."""
        mock_scraper = MagicMock()
        mock_scraper.get.return_value = self._make_mock_response(PRACUJ_HTML)
        mock_create_scraper.return_value = mock_scraper

        mock_db_instance = MagicMock()
        mock_db_instance.check_duplicate.return_value = False  # duplikat istnieje
        MockDB.return_value = mock_db_instance

        from class_folder.pracuj_pl_scrapper import pracuj_pl_scrapper
        s = pracuj_pl_scrapper()
        s.scrap("http://pracuj.pl", False)

        mock_db_instance.add.assert_not_called()

    @patch("class_folder.pracuj_pl_scrapper.cloudscraper.create_scraper")
    def test_http_error_raises(self, mock_create_scraper):
        """Błąd HTTP z raise_for_status powinien propagować wyjątek."""
        import requests
        mock_scraper = MagicMock()
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404")
        mock_scraper.get.return_value = mock_response
        mock_create_scraper.return_value = mock_scraper

        from class_folder.pracuj_pl_scrapper import pracuj_pl_scrapper
        s = pracuj_pl_scrapper()
        with pytest.raises(Exception):
            s.scrap("http://pracuj.pl", False)


# ─── olx_pl_scrapper ──────────────────────────────────────────────────────────

class TestOlxPlScrapper:

    def _make_mock_response(self, html: str):
        response = MagicMock()
        response.text = html
        response.raise_for_status = MagicMock()
        return response

    @patch("class_folder.olx_pl_scrapper.database_operations")
    @patch("class_folder.olx_pl_scrapper.cloudscraper.create_scraper")
    def test_first_time_calls_add_first_time(self, mock_create_scraper, MockDB):
        """Przy first=True powinien wywołać add_first_time z pełnym linkiem OLX."""
        mock_scraper = MagicMock()
        mock_scraper.get.return_value = self._make_mock_response(OLX_HTML)
        mock_create_scraper.return_value = mock_scraper

        mock_db_instance = MagicMock()
        MockDB.return_value = mock_db_instance

        from class_folder.olx_pl_scrapper import olx_pl_scrapper
        s = olx_pl_scrapper()
        s.scrap("http://olx.pl", True)

        call_args = mock_db_instance.add_first_time.call_args[0]
        assert call_args[0].startswith("https://www.olx.pl")

    @patch("class_folder.olx_pl_scrapper.database_operations")
    @patch("class_folder.olx_pl_scrapper.cloudscraper.create_scraper")
    def test_not_first_time_calls_add_when_no_duplicate(self, mock_create_scraper, MockDB):
        """Przy first=False i braku duplikatu powinien wywołać add."""
        mock_scraper = MagicMock()
        mock_scraper.get.return_value = self._make_mock_response(OLX_HTML)
        mock_create_scraper.return_value = mock_scraper

        mock_db_instance = MagicMock()
        mock_db_instance.check_duplicate.return_value = None
        MockDB.return_value = mock_db_instance

        from class_folder.olx_pl_scrapper import olx_pl_scrapper
        s = olx_pl_scrapper()
        s.scrap("http://olx.pl", False)

        mock_db_instance.add.assert_called_once()

    @patch("class_folder.olx_pl_scrapper.database_operations")
    @patch("class_folder.olx_pl_scrapper.cloudscraper.create_scraper")
    def test_not_first_time_skips_add_when_duplicate(self, mock_create_scraper, MockDB):
        """Przy first=False i duplikacie NIE powinien wywołać add."""
        mock_scraper = MagicMock()
        mock_scraper.get.return_value = self._make_mock_response(OLX_HTML)
        mock_create_scraper.return_value = mock_scraper

        mock_db_instance = MagicMock()
        mock_db_instance.check_duplicate.return_value = False
        MockDB.return_value = mock_db_instance

        from class_folder.olx_pl_scrapper import olx_pl_scrapper
        s = olx_pl_scrapper()
        s.scrap("http://olx.pl", False)

        mock_db_instance.add.assert_not_called()
