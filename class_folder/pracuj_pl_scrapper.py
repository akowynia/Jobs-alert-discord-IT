import cloudscraper
import bs4

from database_operations import database_operations


class pracuj_pl_scrapper:
    def __init__(self) -> None:
        pass

    def scrap(self, link, first):
        """
        pobiera dane z strony pracuj
        """

        url = link
        
        # Użyj cloudscraper zamiast requests - omija zabezpieczenia Cloudflare
        scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'darwin',
                'desktop': True
            }
        )
        
        try:
            res = scraper.get(url, timeout=15)
            res.raise_for_status()
            
            # przekształca html obiekt bs4 do przeszukiwania strony
            content = bs4.BeautifulSoup(res.text, features="html.parser")

            # szuka elementu
            elems = content.findAll(attrs={"data-test": "default-offer"})

            for elements in elems:
                try:
                    # ...existing code...
                    link = elements.findAll(attrs={"data-test": "link-offer"})
                    title = elements.findAll(attrs={"data-test": "offer-title"})
                    region = elements.findAll(attrs={"data-test": "text-region"})

                    data_op = database_operations()

                    if first == True:
                        data_op.add_first_time(link[0].get(
                            'href'), title[0].get_text(), region[0].get_text(), "pracuj")
                    else:
                        if data_op.check_duplicate(link[0].get('href')) is not False:
                            data_op.add(link[0].get('href'), title[0].get_text(
                            ), region[0].get_text(), "pracuj")

                except Exception as e:
                    print(f"Element error: {e}")
                    
        except Exception as e:
            print(f"Request error: {e}")
            raise