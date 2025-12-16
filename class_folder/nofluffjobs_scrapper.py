import cloudscraper
import bs4

from database_operations import database_operations


class nofluffjobs_scrapper:
    def __init__(self) -> None:
        pass

    def scrap(self, link, first):
        """
        pobiera dane z strony no fluffjobs
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
        #przekształca html obiekt bs4 do przeszukiwania strony
        content = bs4.BeautifulSoup(res.text,features="html.parser")

        try:
            #szuka elementy
            elems = content.findAll('div', class_="list-container")
            divs = elems[0].findAll('a', class_="posting-list-item")
            for elements in divs:
                link = elements.get('href')
                title = elements.findAll('h3')
                title = title[0].get_text()
                region = elements.findAll('span')
                region = region[-1].get_text()

                data_op = database_operations()
                #link oferty, pobiera nie link a cześć wiec dodaje brakującą część
                nofluffjobs_link = "https://nofluffjobs.com" + link
                if first == True:
                    #jeśli jest to pierwsze uruchomienie to dodaje do bazy danych
                    data_op.add_first_time(
                        nofluffjobs_link, title, region, "nofluffjobs")
                else:
                    #jeśli nie to sprawdza czy dany link istnieje w bazie danych
                    if data_op.check_duplicate(nofluffjobs_link) is not False:
                        data_op.add(
                            nofluffjobs_link, title, region, "nofluffjobs")


        except:
                print("not exist")



        # for elements in elems:

            # try:
            #     print(elements)

            # except:
            #     print("not exist")

        # links = bs4.BeautifulSoup(elems.text)
        # link = links.findAll(attrs={"data-test":"link-offer"})

        # link-offer

        # print(link)
        # print(len(link))
