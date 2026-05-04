import cloudscraper
import bs4
import re

from database_operations import database_operations
from class_folder.update_browser import update_browser


class czy_jest_eldorado_scrapper:
    def __init__(self) -> None:
        pass

    def scrap(self, link, first):
        """
        pobiera dane z strony dla studenta
        """
        url = link
        #nawiązuje połączenie
        scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'darwin',
                'desktop': True
            }
        )
        res =  scraper.get(url, timeout=15) 
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

        #przekształca html obiekt bs4 do przeszukiwania strony
        content = bs4.BeautifulSoup(content_html,features="html.parser")
        #szuka elementu
        elems = content.findAll('div', class_="offer-card-wrapper")
        for elements in elems:
            #sprawdza czy pola które chcemy pobrać istnieją
            try:
                link = elements.find_all('a', class_="btn-quick-apply")
                
                link = link[0].get('href')
                title = elements.find_all('div', class_="job-title")
                title = title[0].get('title')
                region_list = elements.find_all('span')
                region = ""
                for span in region_list:
                    if "data-bs-toggle" in span.attrs:
                        region = span.get('title') or ""
                        region = re.sub(r"\s+", " ", region).strip()
                        if not region or re.match(r'(?i)^(dodana\b|\d+\s+dni?\s+temu|wczoraj|dzisiaj|godz|minut)', region):
                            region = "Brak regionu"
                        break

                
                data_op = database_operations()
                

                if first == True:
                    #jeśli jest to pierwsze uruchomienie to dodaje do bazy danych
                    data_op.add_first_time(
                        link, title, region, "czy_jest_eldorado")
                else:
                    #jeśli nie to sprawdza czy dany link istnieje w bazie danych
                    if data_op.check_duplicate(link) is not False:
                        data_op.add(
                            link, title, region, "czy_jest_eldorado")

            except:
                print("not exist")