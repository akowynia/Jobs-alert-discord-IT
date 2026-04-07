from configparser import RawConfigParser

from class_folder.pracuj_pl_scrapper import pracuj_pl_scrapper
from class_folder.olx_pl_scrapper import olx_pl_scrapper
from class_folder.dlastudenta_pl_scrapper import dlastudenta_scrapper
from class_folder.students_pl_scrapper import students_pl_scrapper
from class_folder.nofluffjobs_scrapper import nofluffjobs_scrapper
from class_folder.theitprotocol_scrapper import theitprotocol_scrapper
from class_folder.czy_jest_eldorado_scrapper import czy_jest_eldorado_scrapper
from database_operations import database_operations
from Generate_excel_file import Generate_excel_file

import logging

# inicjuje logowanie
logger = logging.getLogger('latest')

# Mapowanie nazw serwisów na odpowiadające im klasy scraperów
SCRAPPER_MAP = {
    "pracuj":           pracuj_pl_scrapper,
    "olx":              olx_pl_scrapper,
    "dla_studenta":     dlastudenta_scrapper,
    "students_pl":      students_pl_scrapper,
    "nofluffjobs":      nofluffjobs_scrapper,
    "theitprotocol":    theitprotocol_scrapper,
    "czy_jest_eldorado": czy_jest_eldorado_scrapper,
}


class run_scrapper:
    def __init__(self) -> None:
        pass

    def run(self):
        # wczytuje config, wersja raw ze względu na "linki" które muszą być surowe bez zmian
        config = RawConfigParser()
        config_path = "configs/websites.ini"
        config.read(config_path)

        for section in config.sections():
            website_name = config[section].get("website_name")

            if website_name not in SCRAPPER_MAP:
                continue

            scrapper_class = SCRAPPER_MAP[website_name]
            url = config[section]["website_to_scrap"]
            is_first_time = config[section]["first_time"] == "True"

            if is_first_time:
                config[section]["first_time"] = "False"
                with open(config_path, 'w') as configfile:
                    config.write(configfile)

            scrapper = scrapper_class()
            scrapper.scrap(url, is_first_time)

            logger.info(f"Scraped '{website_name}' (first_time={is_first_time})")

    # funkcja która wywołuje wysyłkę na czat discorda
    def send_discord_info(self):
        logger.info('try sending to discord')
        excel_file = Generate_excel_file()
        database = database_operations()

        excel_file.create_excel_file(database.excel_file_data())
        database.not_sended()
        database.get_added_today()
