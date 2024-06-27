# Jobs-alert-discord-IT

Ten projekt to bot Discorda, który scrapuje informacje o ofertach pracy z różnych stron internetowych głównie pod kątem szukania praktyk/stazy i wysyła je na serwer Discorda. Bot jest napisany w Pythonie i korzysta z SQLite do przechowywania danych.

## Wymagania

- Python 3.6+
- SQLite
- Discord Webhook URL

## Instalacja

1. Sklonuj repozytorium na swoje lokalne środowisko.
2. Zainstaluj wymagane zależności za pomocą `pip install -r requirements.txt`.
3. Utwórz plik konfiguracyjny `configs/websites.ini` zgodnie z szablonem poniżej lub pozwól skryptowi utworzyć go automatycznie przy pierwszym uruchomieniu.
4. Ustaw swoje Discord Webhook URL w pliku konfiguracyjnym.

## Konfiguracja

### Plik `configs/websites.ini`

```ini
[Template]
website_to_scrap = "template"
avatar_url_discord = "url_avatar"
url_webhook_discord = "template"
website_name = "website_name"
first_time = "True" 
```

`[Template]` - w nawiasie mozna umieścić dowolną nazwę, konfiguracji, istotne by się nie powtarzała.

`website_to_scrap` - tutaj umieszczasz link strony z ofertami pracy którą chcesz śledzić i otrzymywać alerty, umieszczasz adres który widzisz w przeglądarce po ustawieniu przez siebie odpowiednich filtrów np. `https://it.pracuj.pl/praca/programista;kw/slask;wp?rd=30` , ilość zastosowanych filtrów nie ma znaczenia gdy pobierana jest cała zawartość strony.

`avatar_url_discord` - tutaj umieszczasz link do zdjęcia który ma być wykorzystywany jako avatar przy wysyłaniu wiadomości.

`url_webhook_discord` - tutaj umieszczasz link do webhooka, dokładny poradnik jak to zrobić znajdziesz pod adresem [https://www.svix.com/resources/guides/how-to-make-webhook-discord/](https://www.svix.com/resources/guides/how-to-make-webhook-discord/)

`website_name` - tutaj umieszczasz nazwę strony z której pobierane są dane, obecnie są to nazwy:
- pracuj
- dla_studenta
- students_pl 
- olx
- nofluffjobs 
- theitprotocol

`first_time = "True"` - to ustawienie to tylko informacja dla skryptu czy jest pierwszym uruchomieniem danej strony, po przetworzeniu wartość się zmieni.

Poprawnie wyglądająca konfiguracja:
```
[pracuj]
website_to_scrap = https://it.pracuj.pl/praca/slask;wp?rd=10&et=1
avatar_url_discord = https://cdn.discordapp.com/avatars/link/zdjecie.gif
url_webhook_discord = https://discord.com/api/webhooks/adres/adres
website_name = pracuj
first_time = True

```


## Uruchomienie

Uruchom skrypt za pomocą `python main.py`.

## Logi

Logi są zapisywane w pliku `latest.log`. Możesz sprawdzić ten plik, aby zobaczyć, co się dzieje podczas działania skryptu.

## Baza danych

Baza danych SQLite (`discord_bot.db`) jest tworzana automatycznie, jeśli nie istnieje. Zawiera ona tabelę `JobsInformation`, która przechowuje informacje o scrapowanych ofertach pracy.

## Skrypty scrapujące

Projekt zawiera skrypty scrapujące dla następujących stron:

- dlastudenta_pl_scrapper.py (dlastudenta.pl)
- nofluffjobs_scrapper.py (nofluffjobs.com)
- olx_pl_scrapper.py (olx.pl)
- pracuj_pl_scrapper.py (pracuj.pl)
- students_pl_scrapper.py (students.pl)
- theitprotocol_scrapper.py (theprotocol.it)