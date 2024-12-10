import requests
import bs4

from database_operations import database_operations


class olx_pl_scrapper:
    def __init__(self) -> None:
        pass

    def scrap(self, link, first):
        """
        pobiera dane z strony olx
        """
        url = link
        # nawiązuje połączenie
        res = requests.get(url)
        res.raise_for_status()
        # przekształca html obiekt bs4 do przeszukiwania strony
        content = bs4.BeautifulSoup(res.text,features="html.parser")

        elems = content.findAll(attrs={"data-cy": "l-card"})
        
        for elements in elems:

            try:
                #rozbiera elementy na części
                link = elements.find_all('a')
                # zmieniono z h6 na h4 / 2024-12-10
                title = elements.find_all('h4')
                region = elements.find_all('span')
                
                # data = [link[0].get('href'), title[0].get_text(),region[0].get_text()]

                data_op = database_operations()
                #link oferty, pobiera nie link a cześć wiec dodaje brakującą część
                olx_link = "https://www.olx.pl" + link[0].get('href')
                if first == True:
                    #jeśli jest to pierwsze uruchomienie to dodaje do bazy danych
                    data_op.add_first_time(
                        olx_link, title[0].get_text(), region[0].get_text(), "olx")
                else:
                    #jeśli nie to sprawdza czy dany link istnieje w bazie danych
                    if data_op.check_duplicate(olx_link) is not False:
                        data_op.add(
                            olx_link, title[0].get_text(), region[0].get_text(), "olx")

            except Exception as e:
                print("not exist",e,"olx")

        # links = bs4.BeautifulSoup(elems.text)
        # link = links.findAll(attrs={"data-test":"link-offer"})

        # link-offer

        # print(link)
        # print(len(link))
