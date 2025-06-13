import time, json
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync

BASE_URL = "https://scholarlypublications.universiteitleiden.nl"
OUTPUT_FILE = "public/content/leiden_detail_urls.json"
MAX_PAGES = 10  # Haal pagina 1 t/m 10 op → ~200 resultaten

def run_scraper():
    detail_urls = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            locale="nl-NL"
        )
        page = context.new_page()
        stealth_sync(page)

        print("🌐 Open homepage")
        page.goto(BASE_URL + "/", timeout=60000)

        print("🔎 Klik op 'Search all items'")
        page.click("a[href='/search']")
        time.sleep(3)

        def extract_links():
            items = page.query_selector_all("dd.mods-titleinfo-title-custom-ms a")
            return [BASE_URL + item.get_attribute("href") for item in items if item.get_attribute("href")]

        for pagina in range(1, MAX_PAGES + 1):
            try:
                print(f"📄 Verwerk pagina {pagina}")
                if pagina > 1:
                    page.click(f"a[title='Go to page {pagina}']", timeout=10000)
                    time.sleep(3)

                links = extract_links()
                print(f"🔗 {len(links)} links op pagina {pagina}")
                detail_urls += links

                time.sleep(1.5)
            except Exception as e:
                print(f"⚠️ Fout bij pagina {pagina}: {e}")

        # Deduplicatie
        detail_urls = list(dict.fromkeys(detail_urls))

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(detail_urls, f, ensure_ascii=False, indent=2)

        print(f"✅ {len(detail_urls)} unieke links opgeslagen in {OUTPUT_FILE}")
        browser.close()

if __name__ == "__main__":
    run_scraper()
