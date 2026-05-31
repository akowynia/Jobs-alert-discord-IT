import cloudscraper
import bs4
from urllib.parse import urljoin, urlparse, urlunparse

from database_operations import database_operations
from class_folder.update_browser import update_browser


class theitprotocol_scrapper:
    def __init__(self) -> None:
        pass

    def scrap(self, link, first):
        """
        pobiera dane z strony theitprotocol
        """

        url = link
        # nawiązuje połączenie
        scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'darwin',
                'desktop': True
            }
        )
        res = scraper.get(url, timeout=15)

        res.raise_for_status()

        # jeśli serwer zwrócił komunikat o konieczności aktualizacji przeglądarki
        content_html = res.text
        ub = update_browser()
        try:
            if ub.is_update_required(content_html):
                rendered = ub.fetch_html(url)
                if rendered:
                    content_html = rendered
        except Exception:
            pass

        # przekształca html obiekt bs4 do przeszukiwania strony
        content = bs4.BeautifulSoup(content_html, features="html.parser")

        # szuka elementu
        elems = content.findAll(attrs={"data-test": "list-item-offer"})

        try:
            for elements in elems:
                # rozbiera elementy na części
                link = elements.get('href')
                title = elements.findAll('h2')
                title = title[0].get_text()
                region = elements.findAll(
                    attrs={"data-test": "text-workplaces"})
                region = region[0].get_text()

                data_op = database_operations()

                # link oferty: dołącz bazę i znormalizuj (usuń parametry zapytania)
                link = urljoin("https://theprotocol.it", link)
                parsed = urlparse(link)
                link = urlunparse((parsed.scheme, parsed.netloc, parsed.path, '', '', ''))

                if first == True:
                    # jeśli jest to pierwsze uruchomienie to dodaje do bazy danych
                    data_op.add_first_time(
                        link, title, region, "theitprotocol")
                else:
                    # jeśli nie to sprawdza czy dany link istnieje w bazie danych
                    if data_op.check_duplicate(link) is not False:
                        data_op.add(link, title, region, "theitprotocol")

        except:
            print("not exist")
