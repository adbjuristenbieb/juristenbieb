import time, json
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync

BASE_URL = "https://scholarlypublications.universiteitleiden.nl"
OUTPUT_FILE = "public/content/leiden_detail_urls.json"

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
            items = page.query_selector_all("dd.mods-titleinfo-title-custom-ms a")  # let op kleine i!
            return [BASE_URL + item.get_attribute("href") for item in items if item.get_attribute("href")]

        print("📄 Verwerk pagina 1")
        time.sleep(2)
        links_p1 = extract_links()
        print(f"🔗 {len(links_p1)} links op pagina 1")
        detail_urls += links_p1

        print("➡️ Klik naar pagina 2")
        try:
            page.click("a[title='Go to page 2']", timeout=10000)
            time.sleep(3)
            print("📄 Verwerk pagina 2")
            links_p2 = extract_links()
            print(f"🔗 {len(links_p2)} links op pagina 2")
            detail_urls += links_p2
        except Exception as e:
            print(f"⚠️ Mislukt bij pagina 2: {e}")

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(detail_urls, f, ensure_ascii=False, indent=2)

        print(f"✅ {len(detail_urls)} links opgeslagen in {OUTPUT_FILE}")
        browser.close()

if __name__ == "__main__":
    run_scraper()
