import requests
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
        # nawiązuje połączenie
        res = requests.get(url)
        res.raise_for_status()
        # przekształca html obiekt bs4 do przeszukiwania strony
        content = bs4.BeautifulSoup(res.text,features="html.parser")

        # szuka elementu
        elems = content.findAll(attrs={"data-test": "default-offer"})

        for elements in elems:

            try:
                # rozbiera elementy na części
                link = elements.findAll(attrs={"data-test": "link-offer"})
                title = elements.findAll(attrs={"data-test": "offer-title"})
                region = elements.findAll(attrs={"data-test": "text-region"})

                # data= [link[0].get('href'),title[0].get_text(),region[0].get_text()]

                data_op = database_operations()

                if first == True:
                    # jeśli jest to pierwsze uruchomienie to dodaje do bazy danych
                    data_op.add_first_time(link[0].get(
                        'href'), title[0].get_text(), region[0].get_text(), "pracuj")
                else:
                    # jeśli nie to sprawdza czy dany link istnieje w bazie danych
                    if data_op.check_duplicate(link[0].get('href')) is not False:
                        data_op.add(link[0].get('href'), title[0].get_text(
                        ), region[0].get_text(), "pracuj")

            except:
                print("not exist")

        # links = bs4.BeautifulSoup(elems.text)
        # link = links.findAll(attrs={"data-test":"link-offer"})

        # link-offer

        # print(link)
        # print(len(link))
