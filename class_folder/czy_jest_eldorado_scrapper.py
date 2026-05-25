import cloudscraper
import bs4
import re
import urllib.parse
import traceback

from database_operations import database_operations
from class_folder.update_browser import update_browser


class czy_jest_eldorado_scrapper:
    def __init__(self) -> None:
        pass

    def scrap(self, link, first):
        """
        pobiera dane z strony czyjesteldorado: link, title, region
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

        # kontenery ofert: div.space-y-3 > div.relative.group (ma data-offer-id)
        containers = content.select('div.space-y-3 div.relative.group')
        if not containers:
            containers = content.select('a.block > article, article')

        for node in containers:
            try:
                # wybierz anchor prowadzący do /praca/
                a_tag = None
                for a in node.find_all('a', href=True):
                    href = a.get('href', '')
                    if '/praca/' in href:
                        a_tag = a
                        break
                if not a_tag:
                    a_tag = node.find('a', href=True)
                if not a_tag and node.name == 'a' and node.get('href'):
                    a_tag = node
                if not a_tag:
                    continue

                offer_href = a_tag.get('href')
                offer_link = urllib.parse.urljoin(url, offer_href)

                # tytuł najczęściej w h3 > span
                title = None
                h3 = node.find('h3')
                if h3:
                    span = h3.find('span')
                    title = (span.get_text(strip=True) if span and span.get_text(strip=True) else h3.get_text(strip=True))

                # region: najpierw po ikonie map-pin, fallback krótki span
                region = "Brak regionu"
                svg_map = None
                for sv in node.find_all('svg'):
                    cls = sv.get('class') or ''
                    cls_str = ' '.join(cls) if isinstance(cls, (list, tuple)) else str(cls)
                    if 'map-pin' in cls_str:
                        svg_map = sv
                        break
                if svg_map:
                    span_after = svg_map.find_next('span')
                    if span_after and span_after.get_text(strip=True):
                        region_text = span_after.get_text(strip=True)
                        region_text = re.sub(r'\s*\+.*$', '', region_text).strip()
                        if region_text and not re.match(r'(?i)^(dodana\b|\d+\s+dni?\s+temu|wczoraj|dzisiaj|godz|minut)', region_text):
                            region = region_text
                else:
                    spans = [s.get_text(strip=True) for s in node.find_all('span') if s.get_text(strip=True)]
                    for s in spans:
                        if len(s) <= 30 and not re.search(r'\d', s):
                            if s.lower() in ('new', 'junior', 'remote', 'zdalnie'):
                                continue
                            region = re.sub(r'\s*\+.*$', '', s).strip()
                            break

                if not title:
                    title = a_tag.get('aria-label') or a_tag.get('title') or a_tag.get_text(strip=True) or "Brak tytułu"

                data_op = database_operations()

                print(f"[czy_jest_eldorado] found: link={offer_link!r}, title={title!r}, region={region!r}")

                if first is True:
                    data_op.add_first_time(offer_link, title, region, "czy_jest_eldorado")
                else:
                    if data_op.check_duplicate(offer_link) is not False:
                        data_op.add(offer_link, title, region, "czy_jest_eldorado")

            except Exception as e:
                print(f"[czy_jest_eldorado] parse error: {e}")
                traceback.print_exc()