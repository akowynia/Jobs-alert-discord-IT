import cloudscraper
import bs4
import urllib.parse
import re
import traceback

from database_operations import database_operations
from class_folder.update_browser import update_browser


class olx_pl_scrapper:
    def __init__(self) -> None:
        pass

    def scrap(self, link, first):
        """
        pobiera dane z strony olx
        """
        url = link
        scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'darwin',
                'desktop': True
            }
        )
        res = scraper.get(url, timeout=15)
        res.raise_for_status()
        content_html = res.text
        ub = update_browser()
        try:
            if ub.is_update_required(content_html):
                rendered = ub.fetch_html(url)
                if rendered:
                    content_html = rendered
        except Exception:
            pass

        content = bs4.BeautifulSoup(content_html, features="html.parser")

        # różne możliwe selektory kart ofertowych, preferuj data-cy l-card
        items = content.select('a[data-cy="l-card"], [data-cy="l-card"], a[data-testid="ad-list-item"], .offer, .aditem') or []

        for node in items:
            try:
                # znajdź link (element może być samym <a> lub zawierać <a>)
                href_tag = node if node.name == 'a' and node.get('href') else node.select_one('a[href]')
                if not href_tag:
                    continue
                href = href_tag.get('href', '').strip()
                if not href:
                    continue

                full_link = urllib.parse.urljoin('https://www.olx.pl', href)

                # tytuł — kilka możliwych miejsc
                title_tag = node.select_one('h4') or node.select_one('h3') or node.select_one('strong') or href_tag
                if hasattr(title_tag, 'get_text'):
                    title = title_tag.get_text(strip=True)
                else:
                    title = str(title_tag).strip()

                if not title:
                    title = href_tag.get_text(strip=True) or 'Brak tytułu'

                # region — wybierz pierwszy sensowny span z literami (pomiń ceny)
                region = 'Brak regionu'
                spans = node.find_all('span')
                for s in spans:
                    txt = s.get_text(strip=True)
                    if not txt:
                        continue
                    if re.search(r'\d', txt) and 'zł' in txt:
                        continue
                    if re.search(r'[A-Za-zĄĆĘŁŃÓŚŹŻąćęłńóśźż]', txt):
                        region = txt
                        break

                data_op = database_operations()
                if first is True:
                    data_op.add_first_time(full_link, title, region, "olx")
                else:
                    if data_op.check_duplicate(full_link) is not False:
                        data_op.add(full_link, title, region, "olx")
            except Exception as e:
                print("[olx] item parse error:", e)
                traceback.print_exc()


