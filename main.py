import sqlite3  # import database

# import logger
import logging

# import configs
from configparser import ConfigParser
from run_scrapper import run_scrapper
import os.path

#tworzy konfiguracje 
def createConfig():
    config = ConfigParser()


    if not os.path.isfile("configs/websites.ini"):
        try:
    # username,avatar_url , description, title, url_webhook
            config["Template"] = {'website_to_scrap': "template",
                            'avatar_url_discord': "url_avatar",
                            'url_webhook_discord': "template",
                            'website_name': "website_name",
                            'first_time': "True"

                            }
            with open("configs/websites.ini", 'w') as configfile:
                config.write(configfile)

            logger.info('Template config has created.')
        except:
            logger.error('Template config not created.')


# tworzy bazę danych sqllite
def createDatabase():
    
    #tworzy folder configs jeśli nie istnieje
    if not os.path.isdir("configs"):
        os.makedirs("configs", exist_ok=True)
        config_path = os.path.abspath("configs")
        logger.info('Config folder created.')

    
    #tworzy bazę danych jeśli nie istnieje
    if not os.path.isfile("discord_bot.db"):
        try:
            db = sqlite3.connect("discord_bot.db")
            cursor = db.cursor()



            #wykonuje kwerendę tworzącą tabele
            cursor.execute('''
       CREATE TABLE JobsInformation(
        id integer,
        jobService varchar,
        currentTime  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        linkOffer varchar,
        offerTitle varchar,
        region varchar,                   
        isSended boolean,
        PRIMARY KEY(id)

         );

            ''')
        
            db.commit()
            # cursor.execute(sql,data)
            db.close()
            logger.info('Created database.')
        except:
            logger.error('Database not created.')


# inicjuje logger, loguje błędy i to co się dzieje
logging.basicConfig(filename="latest.log",
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.DEBUG)

#inicjuje logger o nazwie latest
logger = logging.getLogger('latest')

logger.info('Script has started.')

# wywołuje sprawdzanie baz i konfiguracji
createDatabase()
createConfig()

#uruchamia całą logikę programu 
try:
    run_scrapper = run_scrapper()
    run_scrapper.run()
    run_scrapper.send_discord_info()
except:
    logger.error('Error in run_scrapper.py')
    



