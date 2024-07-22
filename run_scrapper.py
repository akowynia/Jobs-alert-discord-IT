from configparser import RawConfigParser
from class_folder.pracuj_pl_scrapper import pracuj_pl_scrapper
from class_folder.olx_pl_scrapper import olx_pl_scrapper
from class_folder.dlastudenta_pl_scrapper import dlastudenta_scrapper
from class_folder.students_pl_scrapper import students_pl_scrapper
from class_folder.nofluffjobs_scrapper import nofluffjobs_scrapper
from class_folder.theitprotocol_scrapper import theitprotocol_scrapper
from database_operations import database_operations
import requests
import bs4
from Generate_excel_file import Generate_excel_file


import logging

#inicjuje logowanie
logger = logging.getLogger('latest')


class run_scrapper:
    def __init__(self) -> None:
        pass

    def run(self):

        #wczytuje config, wersja raw z względu na "linki" które muszą być surowe bez zmian
        config = RawConfigParser()
        config_path = "configs/websites.ini"
        config.read(config_path)


        #zawiera nazwy stron które są obsługiwane wszystkie klasy znajdują się w folderze class_folder

        website_dictionary = {'pracuj', 'dla_studenta', 'students_pl','olx', 'nofluffjobs','theitprotocol','justjoinit'}
        
        #odczytuje sekcje z pliku konfiguracyjnego
        sections = config.sections()

        #iteruje po sekcjach
        for list_website in sections:
            if config[list_website]["website_name"] in website_dictionary:

                #sprawdza czy jest to pierwsze uruchomienie
                if config[list_website]["first_time"] == "True":

                    config[list_website]["first_time"] = "False"
                    if config[list_website]["website_name"] == "pracuj":
                        with open(config_path, 'w') as configfile:
                            config.write(configfile)
                            pracuj = pracuj_pl_scrapper()
                            pracuj.scrap(config[list_website]
                                         ["website_to_scrap"],True)
                            

                    if config[list_website]["website_name"] == "olx":
                        with open(config_path, 'w') as configfile:
                            config.write(configfile)
                            olx = olx_pl_scrapper()
                            olx.scrap(config[list_website]
                                         ["website_to_scrap"],True)
                    if config[list_website]["website_name"] == "dla_studenta":
                        with open(config_path, 'w') as configfile:
                            config.write(configfile)
                            student = dlastudenta_scrapper()
                            student.scrap(config[list_website]
                                         ["website_to_scrap"],True)
                    if config[list_website]["website_name"] == "students_pl":
                        with open(config_path, 'w') as configfile:
                            config.write(configfile)
                            students_pl = students_pl_scrapper()
                            students_pl.scrap(config[list_website]
                                         ["website_to_scrap"],True)
                            
                    if config[list_website]["website_name"] == "nofluffjobs":
                        with open(config_path, 'w') as configfile:
                            config.write(configfile)
                            nofluffjobs = nofluffjobs_scrapper()
                            nofluffjobs.scrap(config[list_website]
                                         ["website_to_scrap"],True)
                   
                    if config[list_website]["website_name"] == "theitprotocol":
                        with open(config_path, 'w') as configfile:
                            config.write(configfile)
                            theitprotocol = theitprotocol_scrapper()
                            theitprotocol.scrap(config[list_website]
                                         ["website_to_scrap"],True)
                            
                    
                #jeśli nie jest to pierwsze uruchomienie to uruchamia normalnie
                else:

                    if config[list_website]["website_name"] == "pracuj":
                        pracuj = pracuj_pl_scrapper()
                        pracuj.scrap(config[list_website]["website_to_scrap"],False)
                        
                    if config[list_website]["website_name"] == "olx":
                        olx = olx_pl_scrapper()
                        olx.scrap(config[list_website]["website_to_scrap"],False)
                    if config[list_website]["website_name"] == "dla_studenta":
                        student = dlastudenta_scrapper()
                        student.scrap(config[list_website]["website_to_scrap"],False)

                    if config[list_website]["website_name"] == "students_pl":
                        students_pl = students_pl_scrapper()
                        students_pl.scrap(config[list_website]["website_to_scrap"],False)
                        
                    if config[list_website]["website_name"] == "nofluffjobs":
                        nofluffjobs = nofluffjobs_scrapper()
                        nofluffjobs.scrap(config[list_website]["website_to_scrap"],False)
                        
                    if config[list_website]["website_name"] == "theitprotocol":
                        theitprotocol = theitprotocol_scrapper()
                        theitprotocol.scrap(config[list_website]["website_to_scrap"],False)

                    
    
        #end def
                        
    #funkcja która wywołuje wysyłkę na czat discorda
    def send_discord_info(self):
        
        logger.info('try sending to discord')
        excel_file = Generate_excel_file()
        database = database_operations()

        excel_file.create_excel_file(database.excel_file_data())
        database.not_sended()
        database.get_added_today()


        
        pass



