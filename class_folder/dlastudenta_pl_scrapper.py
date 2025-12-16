import cloudscraper
import bs4

from database_operations import database_operations


class dlastudenta_scrapper:
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
        #przekształca html obiekt bs4 do przeszukiwania strony
        content = bs4.BeautifulSoup(res.text,features="html.parser")
        #szuka elentu
        elems = content.findAll('div', class_="offer")

        for elements in elems:
            #sprawdza czy pola które chcemy pobrać istnieją
            try:
                link = elements.find_all('span', class_="offer_name")
                link = link[0].find_all('a')
                title = elements.find_all('span', class_="offer_name")
                region = elements.find_all('span', class_="singleJobArea")

                
                #dekoduje tekst z utf-8 do iso-8859-1 / problemy z pobieraniem były
                raw_text = title[0].get_text()
                decoded_title = raw_text.encode('ISO-8859-1').decode('utf-8')

                raw_text=region[0].get_text()
                decoded_region = raw_text.encode('ISO-8859-1').decode('utf-8')
                # data = [link[0].get('href'), decoded_title,
                #         decoded_region]
                # print(data)
                
                data_op = database_operations()
                
                students_link = link[0].get('href')

                if first == True:
                    #jeśli jest to pierwsze uruchomienie to dodaje do bazy danych
                    data_op.add_first_time(
                        students_link, decoded_title, decoded_region, "dla_studenta")
                else:
                    #jeśli nie to sprawdza czy dany link istnieje w bazie danych
                    if data_op.check_duplicate(students_link) is not False:
                        data_op.add(
                            students_link, decoded_title, decoded_region, "dla_studenta")

            except:
                print("not exist")

        # links = bs4.BeautifulSoup(elems.text)
        # link = links.findAll(attrs={"data-test":"link-offer"})

        # link-offer

        # print(link)
        # print(len(link))
