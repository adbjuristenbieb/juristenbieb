import time, json
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync

BASE_URL = "https://scholarlypublications.universiteitleiden.nl"
OUTPUT_FILE = "public/content/leiden_detail_urls.json"
MAX_PAGES = 1000

def run_scraper():
    detail_urls = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/124.0.0.0 Safari/537.36"),
            locale="nl-NL"
        )
        page = context.new_page()
        stealth_sync(page)

        print("🌐 Open homepage")
        page.goto(BASE_URL + "/", timeout=60000)

        print("🔎 Klik op 'Search all items'")
        page.click("a[href='/search']")
        time.sleep(3)  # wacht even op frontend JS

        current_page = 1
        while current_page <= MAX_PAGES:
            print(f"📄 Verwerk pagina {current_page}")
            html = page.content()
            links = page.query_selector_all("dd.mods-titleinfo-title-custom-ms a")
            found = 0
            for link in links:
                href = link.get_attribute("href")
                if href and "/handle/" in href:
                    detail_urls.append(BASE_URL + href)
                    found += 1
            print(f"🔗 {found} links op pagina {current_page} (totaal: {len(detail_urls)})")

            next_locator = page.locator(f"a[aria-label='Go to page {current_page + 1}']")
            if next_locator.count() == 0:
                print("✅ Geen volgende pagina gevonden.")
                break

            try:
                next_locator.click()
                time.sleep(2)
                current_page += 1
            except Exception as e:
                print(f"⚠️ Fout bij klikken op volgende pagina: {e}")
                break

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(detail_urls, f, ensure_ascii=False, indent=2)
        print(f"✅ {len(detail_urls)} links opgeslagen in {OUTPUT_FILE}")
        browser.close()

if __name__ == "__main__":
    run_scraper()
