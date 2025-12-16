import cloudscraper
import bs4

from database_operations import database_operations


class students_pl_scrapper:
    def __init__(self) -> None:
        pass

    def scrap(self, link, first):
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
        # przekształca html obiekt bs4 do przeszukiwania strony
        content = bs4.BeautifulSoup(res.text,features="html.parser")

        # szuka elementu
        elems = content.findAll(attrs={"class": "c-ListingCard"})
        
        for elements in elems:

            try:
                # rozbiera elementy na części
                link = elements.findAll("a", class_="c-ListingCard_headerLink")
                title = elements.findAll(
                    "a", class_="c-ListingCard_headerLink")
                region = elements.findAll(
                    "div", class_="c-ListingCard_briefText-location")

                data= [link[0].get('href'),title[0].get_text(),region[0].get_text()]

                data_op = database_operations()
                #link oferty, pobiera nie link a cześć wiec dodaje brakującą część
                link = "https://students.pl" + link[0].get('href')
                
                if first == True:
                    #jeśli jest to pierwsze uruchomienie to dodaje do bazy danych
                    data_op.add_first_time(
                        link, title[0].get_text(), region[0].get_text(), "students_pl")
                else:
                    #jeśli nie to sprawdza czy dany link istnieje w bazie danych
                    if data_op.check_duplicate(link) is not False:
                        data_op.add(link, title[0].get_text(
                        ), region[0].get_text(), "students_pl")

            except:
                print("not exist")

        # links = bs4.BeautifulSoup(elems.text)
        # link = links.findAll(attrs={"data-test":"link-offer"})

        # link-offer

        # print(link)
        # print(len(link))
