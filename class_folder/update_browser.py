import cloudscraper
import bs4
import time

# Minimalna liczba znaków treści strony po renderze Playwright, aby uznać render za poprawny
DEFAULT_MIN_TEXT_CHARS = 200


class update_browser:
    def __init__(self, min_text_chars: int = DEFAULT_MIN_TEXT_CHARS) -> None:
        self.min_text_chars = min_text_chars

    def is_update_required(self, html: str) -> bool:
        """Publiczna metoda: sprawdza czy HTML sugeruje konieczność aktualizacji przeglądarki.

        Zwraca True gdy znajdzie typowe frazy informujące o aktualizacji przeglądarki,
        włączeniu JavaScriptu lub weryfikacji anty-bot.
        """
        return self._is_browser_update_page(html)

    def fetch_html(self, url: str, timeout: int = 120000) -> str | None:
        """Publiczna metoda: pobiera HTML strony.

        Najpierw próbuje wyrenderować stronę przy pomocy Playwright. Jeśli Playwright
        nie jest dostępny lub renderowanie się nie powiedzie, używa `cloudscraper` jako
        prostszego fallbacku.
        Zwraca HTML lub None jeśli obie metody zawiodą.
        """
        html = self._render_with_playwright(url, timeout=timeout)
        if html:
            return html

        # Fallback: cloudscraper
        try:
            scraper = cloudscraper.create_scraper()
            resp = scraper.get(url, timeout=30)
            if resp.status_code == 200:
                return resp.text
        except Exception:
            pass

        return None

    def _is_browser_update_page(self, html: str) -> bool:
        """Proste heurystyki wykrywające komunikaty o aktualizacji przeglądarki / blokady JS.

        Zwraca True jeśli treść HTML zawiera typowe frazy informujące o konieczności
        aktualizacji przeglądarki, włączenia JavaScriptu lub weryfikacji anty-bot.
        """
        if not html:
            return False

        lower = html.lower()

        phrases = (
            'update your browser',
            'please update your browser',
            'upgrade your browser',
            'browser not supported',
            'unsupported browser',
            'please enable javascript',
            'enable javascript',
            'please verify you are a human',
            'verify you are a human',
            'access denied',
            'zaktualizuj przegl',
            'zaktualizuj przeglądarkę',
            'włącz javascript',
        )

        for p in phrases:
            if p in lower:
                return True

        return False

    def _render_with_playwright(self, url: str, timeout: int = 120000) -> str | None:
        """Spróbuj wyrenderować stronę przy użyciu Playwright i zwróć HTML.

        Zwraca zawartość HTML lub None jeśli Playwright nie jest dostępny lub
        renderowanie się nie powiedzie. Dodaje retry, user-agent oraz auto-scroll
        aby poradzić sobie z lazy-loaded i JS-owymi stronami ofert pracy.
        """
        try:
            from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
        except Exception:
            print("[INFO] Playwright nie jest zainstalowany. Zainstaluj: pip install playwright && playwright install")
            return None

        UA = (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        )

        def _auto_scroll(page):
            page.evaluate("""
                async () => {
                    const distance = 800;
                    const delay = (ms) => new Promise(r => setTimeout(r, ms));
                    for (let i = 0; i < 20; i++) {
                        window.scrollBy(0, distance);
                        await delay(300);
                    }
                }
            """)

        attempts = 2
        for attempt in range(1, attempts + 1):
            try:
                with sync_playwright() as p:
                    browser = p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-dev-shm-usage'])
                    context = browser.new_context(user_agent=UA, viewport={'width': 1280, 'height': 800})
                    page = context.new_page()
                    page.goto(url, timeout=timeout, wait_until='domcontentloaded')

                    try:
                        _auto_scroll(page)
                    except Exception:
                        pass

                    try:
                        page.wait_for_load_state('networkidle', timeout=5000)
                    except Exception:
                        pass

                    content = page.content()
                    text = bs4.BeautifulSoup(content, features="html.parser").get_text(separator=' ', strip=True)
                    if len(text) < self.min_text_chars:
                        print(f"[INFO] Playwright render returned too little text ({len(text)} chars) on attempt {attempt}")
                        browser.close()
                        if attempt < attempts:
                            time.sleep(1)
                            continue
                        return None

                    browser.close()
                    return content

            except PlaywrightTimeout as e:
                print(f"[WARN] Playwright timeout on attempt {attempt}: {e}")
                if attempt == attempts:
                    return None
                time.sleep(1)
                continue
            except Exception as e:
                print(f"[WARN] Playwright render failed on attempt {attempt}: {e}")
                if attempt == attempts:
                    return None
                time.sleep(1)
                continue

