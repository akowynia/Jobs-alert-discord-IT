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

# Dodatkowe przykładowe HTML-e dla pozostałych scraperów
DLASTUDENTA_HTML = """
<div class="offer">
        <span class="offer_name"><a href="/offer/1">Junior Dev</a></span>
</div>
"""

STUDENTS_HTML = """
<div class="c-ListingCard">
        <a class="c-ListingCard_headerLink" href="/offer/1">Student Dev</a>
        <div class="c-ListingCard_briefText-location">Gdańsk</div>
</div>
"""

NOFLUFF_HTML = """
<a class="posting-list-item" href="/job/1">
        <h3 class="posting-title__position">NoFluff Dev</h3>
        <div class="posting-info__location"><span>Łódź</span></div>
</a>
"""

THEPROTO_HTML = """
<a data-test="list-item-offer" href="/job/1">
        <h2>DevOps Engineer</h2>
        <span data-test="text-workplaces">Poznań</span>
</a>
"""

CZY_ELDORADO_HTML = """
<div class="space-y-3">
    <div class="relative group" data-offer-id="1">
        <a href="/praca/1">
            <h3><span>Frontend Dev</span></h3>
            <svg class="map-pin"></svg>
            <span>Warszawa</span>
        </a>
    </div>
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


    @patch("class_folder.pracuj_pl_scrapper.database_operations")
    @patch("class_folder.pracuj_pl_scrapper.cloudscraper.create_scraper")
    def test_pracuj_parses_some_offers(self, mock_create_scraper, MockDB):
        """Szybki test: czy parser pracuj zwraca przynajmniej jedną ofertę (add/add_first_time)."""
        mock_scraper = MagicMock()
        mock_scraper.get.return_value = self._make_mock_response(PRACUJ_HTML)
        mock_create_scraper.return_value = mock_scraper

        mock_db_instance = MagicMock()
        MockDB.return_value = mock_db_instance

        from class_folder.pracuj_pl_scrapper import pracuj_pl_scrapper
        s = pracuj_pl_scrapper()
        s.scrap("http://pracuj.pl", False)

        total_calls = mock_db_instance.add.call_count + mock_db_instance.add_first_time.call_count
        assert total_calls > 0


    @patch("class_folder.olx_pl_scrapper.database_operations")
    @patch("class_folder.olx_pl_scrapper.cloudscraper.create_scraper")
    def test_olx_parses_some_offers(self, mock_create_scraper, MockDB):
        """Szybki test: czy parser OLX zwraca przynajmniej jedną ofertę (add/add_first_time)."""
        mock_scraper = MagicMock()
        mock_scraper.get.return_value = self._make_mock_response(OLX_HTML)
        mock_create_scraper.return_value = mock_scraper

        mock_db_instance = MagicMock()
        MockDB.return_value = mock_db_instance

        from class_folder.olx_pl_scrapper import olx_pl_scrapper
        s = olx_pl_scrapper()
        s.scrap("http://olx.pl", False)

        total_calls = mock_db_instance.add.call_count + mock_db_instance.add_first_time.call_count
        assert total_calls > 0


class TestAllScrapersQuickParse:
    """Szybkie testy parsowania dla wszystkich scraperów z `class_folder`.
    Sprawdzają tylko, czy parser wywołuje `add` lub `add_first_time` przynajmniej raz.
    """

    def _make_mock_response(self, html: str):
        response = MagicMock()
        response.text = html
        response.raise_for_status = MagicMock()
        return response

    @patch("class_folder.dlastudenta_pl_scrapper.database_operations")
    @patch("class_folder.dlastudenta_pl_scrapper.cloudscraper.create_scraper")
    def test_dlastudenta_parses_some_offers(self, mock_create_scraper, MockDB):
        mock_scraper = MagicMock()
        mock_scraper.get.return_value = self._make_mock_response(DLASTUDENTA_HTML)
        mock_create_scraper.return_value = mock_scraper

        mock_db_instance = MagicMock()
        MockDB.return_value = mock_db_instance

        from class_folder.dlastudenta_pl_scrapper import dlastudenta_scrapper
        s = dlastudenta_scrapper()
        s.scrap("http://dlastudenta.pl", False)

        total_calls = mock_db_instance.add.call_count + mock_db_instance.add_first_time.call_count
        assert total_calls > 0

    @patch("class_folder.students_pl_scrapper.database_operations")
    @patch("class_folder.students_pl_scrapper.cloudscraper.create_scraper")
    def test_students_pl_parses_some_offers(self, mock_create_scraper, MockDB):
        mock_scraper = MagicMock()
        mock_scraper.get.return_value = self._make_mock_response(STUDENTS_HTML)
        mock_create_scraper.return_value = mock_scraper

        mock_db_instance = MagicMock()
        MockDB.return_value = mock_db_instance

        from class_folder.students_pl_scrapper import students_pl_scrapper
        s = students_pl_scrapper()
        s.scrap("http://students.pl", False)

        total_calls = mock_db_instance.add.call_count + mock_db_instance.add_first_time.call_count
        assert total_calls > 0

    @patch("class_folder.nofluffjobs_scrapper.database_operations")
    @patch("class_folder.nofluffjobs_scrapper.cloudscraper.create_scraper")
    def test_nofluffjobs_parses_some_offers(self, mock_create_scraper, MockDB):
        mock_scraper = MagicMock()
        mock_scraper.get.return_value = self._make_mock_response(NOFLUFF_HTML)
        mock_create_scraper.return_value = mock_scraper

        mock_db_instance = MagicMock()
        MockDB.return_value = mock_db_instance

        from class_folder.nofluffjobs_scrapper import nofluffjobs_scrapper
        s = nofluffjobs_scrapper()
        s.scrap("http://nofluffjobs.pl", False)

        total_calls = mock_db_instance.add.call_count + mock_db_instance.add_first_time.call_count
        assert total_calls > 0

    @patch("class_folder.theitprotocol_scrapper.database_operations")
    @patch("class_folder.theitprotocol_scrapper.cloudscraper.create_scraper")
    def test_theitprotocol_parses_some_offers(self, mock_create_scraper, MockDB):
        mock_scraper = MagicMock()
        mock_scraper.get.return_value = self._make_mock_response(THEPROTO_HTML)
        mock_create_scraper.return_value = mock_scraper

        mock_db_instance = MagicMock()
        MockDB.return_value = mock_db_instance

        from class_folder.theitprotocol_scrapper import theitprotocol_scrapper
        s = theitprotocol_scrapper()
        s.scrap("http://theprotocol.it", False)

        total_calls = mock_db_instance.add.call_count + mock_db_instance.add_first_time.call_count
        assert total_calls > 0

    @patch("class_folder.czy_jest_eldorado_scrapper.database_operations")
    @patch("class_folder.czy_jest_eldorado_scrapper.cloudscraper.create_scraper")
    def test_czy_jest_eldorado_parses_some_offers(self, mock_create_scraper, MockDB):
        mock_scraper = MagicMock()
        mock_scraper.get.return_value = self._make_mock_response(CZY_ELDORADO_HTML)
        mock_create_scraper.return_value = mock_scraper

        mock_db_instance = MagicMock()
        MockDB.return_value = mock_db_instance

        from class_folder.czy_jest_eldorado_scrapper import czy_jest_eldorado_scrapper
        s = czy_jest_eldorado_scrapper()
        s.scrap("http://czyjesteldorado.pl", False)

        total_calls = mock_db_instance.add.call_count + mock_db_instance.add_first_time.call_count
        assert total_calls > 0
