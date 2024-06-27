import requests
import bs4

from database_operations import database_operations


class theitprotocol_scrapper:
    def __init__(self) -> None:
        pass

    def scrap(self, link, first):
        """
        pobiera dane z strony theitprotocol
        """

        url = link
        # nawiązuje połączenie
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
        res = requests.get(url,headers=headers)

        res.raise_for_status()
        # przekształca html obiekt bs4 do przeszukiwania strony
        content = bs4.BeautifulSoup(res.text,features="html.parser")

        # szuka elementu
        elems = content.findAll(attrs={"data-test": "list-item-offer"})
        

        try:
            for elements in elems:
                # rozbiera elementy na części
                link = elements.get('href')
                title = elements.findAll('h2')
                title = title[0].get_text()
                region = elements.findAll(attrs={"data-test": "text-workplaces"})
                region = region[0].get_text()

                data_op = database_operations()

                #link oferty, pobiera nie link a cześć wiec dodaje brakującą część
                link = "https://theprotocol.it" + link
                
                
                if first == True:
                    #jeśli jest to pierwsze uruchomienie to dodaje do bazy danych
                    data_op.add_first_time(
                        link, title, region, "theitprotocol")
                else:
                    #jeśli nie to sprawdza czy dany link istnieje w bazie danych
                    if data_op.check_duplicate(link) is not False:
                        data_op.add(link, title, region, "theitprotocol")
                

        except:
                print("not exist")
  
