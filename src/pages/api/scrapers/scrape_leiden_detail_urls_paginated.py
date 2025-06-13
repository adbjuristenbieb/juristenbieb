import json
import time
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

BASE_URL = "https://scholarlypublications.universiteitleiden.nl"
OUTPUT_FILE = "public/content/leiden_detail_urls.json"
MAX_PAGES = 5  # Pas aan naar bijvoorbeeld 1000 zodra stabiel

def run_scraper():
    all_urls = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1280, "height": 900},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            )
        )
        page = context.new_page()
        print("🌐 Open homepage")
        page.goto(BASE_URL, timeout=60000)

        print("🔎 Klik op 'Search all items'")
        page.get_by_role("link", name="Search all items").click()
        page.wait_for_url("**/search**", timeout=15000)

        for pagina in range(1, MAX_PAGES + 1):
            print(f"📄 Verwerk pagina {pagina}")
            try:
                page.wait_for_selector("div.result-item", timeout=20000)
                items = page.query_selector_all("div.result-item")
                print(f"🔗 {len(items)} items gevonden op pagina {pagina}")
                for item in items:
                    a_tag = item.query_selector("dd.mods-titleinfo-title-custom-ms a")
                    if a_tag:
                        href = a_tag.get_attribute("href")
                        if href and href.startswith("/handle/"):
                            full_url = BASE_URL + href
                            all_urls.append(full_url)
            except PlaywrightTimeout:
                print(f"⚠️ Timeout bij pagina {pagina}, resultaten niet gevonden.")
                break

            # Volgende pagina aanklikken
            next_label = f"Go to page {pagina + 1}"
            try:
                next_button = page.get_by_role("link", name=next_label)
                if next_button.count() == 0:
                    print(f"✅ Geen knop gevonden voor pagina {pagina + 1}. Klaar.")
                    break
                next_button.first.click()
                page.wait_for_url(f"**page={pagina + 1}**", timeout=15000)
                time.sleep(1)
            except PlaywrightTimeout:
                print(f"⚠️ Timeout bij klikken op pagina {pagina + 1}")
                break
            except Exception as e:
                print(f"⚠️ Andere fout bij klikken op pagina {pagina + 1}: {e}")
                break

        # Sla resultaten op
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(all_urls, f, ensure_ascii=False, indent=2)
        print(f"✅ {len(all_urls)} links opgeslagen in {OUTPUT_FILE}")

if __name__ == "__main__":
    run_scraper()