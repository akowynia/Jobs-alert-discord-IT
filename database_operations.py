import sqlite3  # import database
from class_folder.webhook_send import webhook_send
import os
from configparser import RawConfigParser
from datetime import date
from matplotlib import pyplot as plt
import matplotlib.dates as mdates
import time


class database_operations:
    def __init__(self):
        pass

    def check_duplicate(self, link):
        """
        funkcja sprawdza duplikaty

        """
        db = sqlite3.connect('discord_bot.db')
        cursor = db.cursor()

        # sprawdzające czy istnieje już taki link w bazie danych
        sql = ''' select linkOffer,offerTitle from JobsInformation where linkOffer like ? '''

        cursor.execute(sql, (link,))
        rows = cursor.fetchall()

        db.commit()
        db.close()
        # zwraca false jeśli nie ma duplikatu (sprawdza ilość występujących wierszy z bazy danych )
        if len(rows) != 0:
            return False

    def add(self, link, title, region, jobs_service):
        """
        funkcja dodaje do bazy danych
        """

        db = sqlite3.connect('discord_bot.db')
        cursor = db.cursor()

        # kwerenda insert into dodająca wartości do bazy danych
        sql = ''' INSERT INTO JobsInformation(jobService,linkOffer,offerTitle,region,isSended)VALUES(?,?,?,?,?); '''

        # wartość 0 jest statyczna bo słuzy do sprawdzania czy dany wiersz został już wysłany na discorda
        data = (jobs_service, link, title, region, 0)

        cursor.execute(sql, data)
        db.commit()
        db.close()

    def add_first_time(self, link, title, region, jobs_service):
        """
        funkcja dodaje do bazy danych
        """
        db = sqlite3.connect('discord_bot.db')
        cursor = db.cursor()
        sql = ''' INSERT INTO JobsInformation(jobService,linkOffer,offerTitle,region,isSended)VALUES(?,?,?,?,?); '''
        data = (jobs_service, link, title, region, 1)

        cursor.execute(sql, data)
        db.commit()
        db.close()

    def not_sended(self):
        """
        funkcja wysyła na discorda
        """
        
        #odczytuje konfiguracje z pliku
        config = RawConfigParser()
        config_path = "configs/websites.ini"
        config.read(config_path)
        website_dictionary = {'pracuj', 'dla_studenta',
                              'students_pl', 'olx', 'nofluffjobs', 'theitprotocol'}
        

        #zmienne do przechowywania zdjeć bota
        pracuj_discord_image = ""
        olx_discord_image = ""
        dla_studenta_image = ""
        students_pl_image = ""
        nofluffjobs_image = ""
        theitprotocol_image = ""

        #zmienne przechowywujące link do webhooka(do wysłania zadania)
        olx_link = ""
        pracuj_pl_link = ""
        dla_studenta_link = ""
        students_pl_link = ""
        nofluffjobs_link = ""
        theitprotocol_link = ""


        #odczytywanie z pliku konfiguracyjnego linków do webhooków oraz avatarów 
        sections = config.sections()
        for list_website in sections:
            if config[list_website]["website_name"] in website_dictionary:
                if config[list_website]["website_name"] == "olx":
                    olx_link = config[list_website]["url_webhook_discord"]
                    olx_discord_image = config[list_website]["avatar_url_discord"]

                if config[list_website]["website_name"] == "pracuj":
                    pracuj_pl_link = config[list_website]["url_webhook_discord"]
                    pracuj_discord_image = config[list_website]["avatar_url_discord"]

                if config[list_website]["website_name"] == "dla_studenta":
                    dla_studenta_link = config[list_website]["url_webhook_discord"]
                    dla_studenta_image = config[list_website]["avatar_url_discord"]

                if config[list_website]["website_name"] == "students_pl":
                    students_pl_link = config[list_website]["url_webhook_discord"]
                    students_pl_image = config[list_website]["avatar_url_discord"]

                if config[list_website]["website_name"] == "nofluffjobs":
                    nofluffjobs_link = config[list_website]["url_webhook_discord"]
                    nofluffjobs_image = config[list_website]["avatar_url_discord"]

                if config[list_website]["website_name"] == "theitprotocol":
                    theitprotocol_link = config[list_website]["url_webhook_discord"]
                    theitprotocol_image = config[list_website]["avatar_url_discord"]




        db = sqlite3.connect('discord_bot.db')
        cursor = db.cursor()


        #pobiera wszystkie dane które nie zostały wysłane na discorda
        sql = ''' select id,jobService,linkOffer,offerTitle,region,isSended from JobsInformation where isSended = 0'''

        cursor.execute(sql)
        rows = cursor.fetchall()
        #inicjowanie klasy webhook_send
        webhook = webhook_send()
        for row in rows:
            #zmienne przechowujące dane z bazy danych
            id = row[0]
            jobService = row[1]
            linkOffer = row[2]
            offerTitle = row[3]
            region = row[4]
            isSended = row[5]
            
            #wysyła na discorda w zależności od serwisu z którego pochodzi oferta
            if jobService == "olx" and isSended == 0:
                webhook.send_message(
                    "olx_bot", olx_discord_image, olx_link, offerTitle, linkOffer, region)
            if jobService == "pracuj" and isSended == 0:
                webhook.send_message(
                    "pracuj_pl", pracuj_discord_image, pracuj_pl_link, offerTitle, linkOffer, region)

            if jobService == "dla_studenta" and isSended == 0:
                webhook.send_message(
                    "dla_studenta", dla_studenta_image, dla_studenta_link, offerTitle, linkOffer, region)

            if jobService == "students_pl" and isSended == 0:
                webhook.send_message(
                    "students_pl", students_pl_image, students_pl_link, offerTitle, linkOffer, region)

            if jobService == "nofluffjobs" and isSended == 0:
                webhook.send_message(
                    "nofluffjobs", nofluffjobs_image, nofluffjobs_link, offerTitle, linkOffer, region)
            if jobService == "theitprotocol" and isSended == 0:
                webhook.send_message(
                    "theitprotocol", theitprotocol_image, theitprotocol_link, offerTitle, linkOffer, region)


            time.sleep(2)


            #aktualizuje tabele która informuje czy dany wiersz został już wysłany na discorda
            sql = '''UPDATE JobsInformation
                SET isSended = 1
                WHERE id = ?'''
            cursor.execute(sql, (id,))
            # print(id,jobService,linkOffer,offerTitle,region,isSended)

        db.commit()
        db.close()

    def get_added_today(self):
        """
        Robi statystykę ile dodało rekordów dziennie/miesięcznie
        """

        db = sqlite3.connect('discord_bot.db')
        cursor = db.cursor()
        current_day = date.today()

        #kwerenda zliczająca ile rekordów dodano dziennie
        sql = '''SELECT strftime('%Y-%m-%d', currentTime) AS day, COUNT(id) AS count
         FROM JobsInformation
         GROUP BY day
         ORDER BY day;'''

        cursor.execute(sql)
        results = cursor.fetchall()
        # ustawia x-y dla danych na wykres
        dates = [row[0] for row in results]
        counts = [row[1] for row in results]
        

        #rysuje figure , w nawiasie są wymiary, szerokośc/wysokość
        plt.figure(figsize=(10, 7))
        #ustawia legendę i oznaczenia osi
        plt.plot(dates, counts, label='Ilość', color='r')
        plt.xlabel('Data')
        plt.ylabel('Ilość')

        #tytuł
        plt.title('Ilość dodanych rekordów codziennie')
        plt.xticks(rotation=45)
        #narzuca legendę
        plt.legend()

        #zapisuje do pliku
        plt.savefig('statistic.png')

        #odczytuje i wysyła statystykę na discorda
        config = RawConfigParser()
        config.read('configs/statistic.ini')
        avatar_url_discord = config.get(
            'discord', 'avatar_url_discord', raw=True)
        url_webhook_discord = config.get(
            'discord', 'url_webhook_discord', raw=True)

        webhook = webhook_send()
        webhook.send_message_file(
            "statistic", avatar_url_discord, url_webhook_discord)

        db.commit()
        db.close()
