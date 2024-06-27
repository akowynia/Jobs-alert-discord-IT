import requests  # dependency
from urllib import request
import urllib


class webhook_send:
    def __init__(self):
        pass

    def send_message(self, username, avatar_url ,url_webhook, content,description, title):
        """
        Wysyła dane na czat discorda przez webhooki
        """
        #link webhooka
        url = url_webhook

        #zbiera dane do wysłania, format json 
        data = {
            "content": content,
            "username": username,
            "avatar_url":avatar_url
        }


# for all params, see https://discordapp.com/developers/docs/resources/channel#embed-object
        
        
        #Formatuje wiadomość, wyzej jest link z parametrami api do formatowania wiadomości
        data["embeds"] = [
            {
                "description":description,
                "title": title
            }
        ]

        
        #wysyła dane na czat discorda, słownik data jest formatowany do jsona
        result = requests.post(url,json=data)
                
        #files={'upload_file': open('files_path','rb')}
        #result = requests.request("POST", url, json = data,files=files)

        try:
            result.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print(err)
        else:
            print("Payload delivered successfully, code {}.".format(
                result.status_code))
            

    def send_message_file(self,username, avatar_url ,url_webhook):
         
         """
         wysyła z plikiem, głównie dla statystyk
         """
         url = url_webhook

         files = {
            "username": username,
            "avatar_url": avatar_url
        }


        #otwiera plik
         files = {'upload_file': open('statistic.png', 'rb')}

         result = requests.request("POST", url, files=files)
         try:
             result.raise_for_status()
         except requests.exceptions.HTTPError as err:
            print(err)
         else:
            print("Payload delivered successfully, code {}.".format(
                result.status_code))