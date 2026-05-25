import cloudscraper
import bs4
import urllib.parse
import traceback

from database_operations import database_operations
from class_folder.update_browser import update_browser


class dlastudenta_scrapper:
    def __init__(self) -> None:
        pass

    def scrap(self, link, first):
        """
        Prosty parser dla dlastudenta: dla każdego wpisu pobiera link, title i region.
        Jeśli w ofercie jest lista lokalizacji, dodaje osobny wpis dla każdej lokalizacji.
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
        elems = content.find_all('div', class_='offer')

        for elements in elems:
            try:
                a_main = elements.select_one('span.offer_name a')
                if not a_main:
                    print('[dlastudenta] brak linku głównego, pomijam element')
                    continue

                main_href = a_main.get('href', '').strip()
                main_link = urllib.parse.urljoin(url, main_href)
                title = a_main.get_text(strip=True) or a_main.get('title') or 'Brak tytułu'

                # lista lokalizacji (jobAreas). Jeśli jest — dodajemy wpis dla każdej lokalizacji
                job_areas = elements.select('ul.jobAreas li')
                if job_areas:
                    for li in job_areas:
                        a_loc = li.select_one('span.column-jobName a')
                        href_loc = a_loc.get('href', '').strip() if a_loc else ''
                        link_to_use = urllib.parse.urljoin(url, href_loc) if href_loc else main_link
                        region_span = li.select_one('span.column-jobArea')
                        region_text = region_span.get_text(strip=True) if region_span else 'Brak regionu'

                        data_op = database_operations()
                        print(f"[dlastudenta] found: link={link_to_use!r}, title={title!r}, region={region_text!r}")

                        if first is True:
                            data_op.add_first_time(link_to_use, title, region_text, 'dla_studenta')
                        else:
                            if data_op.check_duplicate(link_to_use) is not False:
                                data_op.add(link_to_use, title, region_text, 'dla_studenta')
                else:
                    # brak listy lokalizacji — użyjemy głównego linku
                    data_op = database_operations()
                    print(f"[dlastudenta] found: link={main_link!r}, title={title!r}, region=Brak regionu")
                    if first is True:
                        data_op.add_first_time(main_link, title, 'Brak regionu', 'dla_studenta')
                    else:
                        if data_op.check_duplicate(main_link) is not False:
                            data_op.add(main_link, title, 'Brak regionu', 'dla_studenta')

            except Exception as e:
                print(f"[dlastudenta] parse error: {e}")
                traceback.print_exc()