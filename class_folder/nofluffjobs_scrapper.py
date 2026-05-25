import cloudscraper
import bs4
import urllib.parse
import traceback
import re

from database_operations import database_operations
from class_folder.update_browser import update_browser


class nofluffjobs_scrapper:
    def __init__(self) -> None:
        pass

    def scrap(self, link, first):
        """
        Prosty parser dla NoFluffJobs: znajdź wszystkie elementy listingowe i pobierz link, tytuł, region.
        """
        url = link
        scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'platform': 'darwin', 'desktop': True})
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
        try:
            items = content.select('div.list-container a.posting-list-item') or content.select('a.posting-list-item')
            for node in items:
                try:
                    href = node.get('href', '').strip()
                    if not href:
                        continue
                    full_link = urllib.parse.urljoin(url, href)
                    h3 = node.select_one('h3.posting-title__position') or node.find('h3')
                    title = h3.get_text(strip=True) if h3 else 'Brak tytułu'
                    region_span = node.select_one('.posting-info__location span')
                    region = 'Brak regionu'
                    if region_span and region_span.get_text(strip=True):
                        region_text = region_span.get_text(strip=True)
                        region = re.sub(r'\s*\+.*$', '', region_text).strip()

                    data_op = database_operations()
                    if first is True:
                        data_op.add_first_time(full_link, title, region, 'nofluffjobs')
                    else:
                        if data_op.check_duplicate(full_link) is not False:
                            data_op.add(full_link, title, region, 'nofluffjobs')
                except Exception as e:
                    print(f"[nofluffjobs] item parse error: {e}")
                    traceback.print_exc()
        except Exception as e:
            print(f"[nofluffjobs] parse error: {e}")
            traceback.print_exc()
