import json
import time
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync

BASE_URL = "https://scholarlypublications.universiteitleiden.nl"
OUTPUT_FILE = "public/content/leiden_detail_urls.json"
MAX_PAGES = 3  # Haal pagina 1 t/m 3 op

def run_scraper():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
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
        page.goto(BASE_URL, timeout=60000)

        print("🔎 Klik op 'Search all items'")
        page.get_by_role("link", name="Search all items").click()
        page.wait_for_selector("div.result-item", timeout=30000)

        detail_urls = []

        for page_num in range(1, MAX_PAGES + 1):
            print(f"📄 Verwerk pagina {page_num}")
            result_items = page.query_selector_all("div.result-item")
            for item in result_items:
                link_elem = item.query_selector("dd.mods-titleinfo-title-custom-ms a")
                if link_elem:
                    href = link_elem.get_attribute("href")
                    if href:
                        full_url = href if href.startswith("http") else BASE_URL + href
                        detail_urls.append(full_url)
            print(f"🔗 {len(result_items)} links op pagina {page_num} (totaal: {len(detail_urls)})")

            # Klik op volgende pagina (indien aanwezig)
            next_label = f"Go to page {page_num + 1}"
            next_link = page.locator(f"a[aria-label='{next_label}']")
            if next_link.count() > 0:
                try:
                    next_link.first.click(timeout=10000)
                    page.wait_for_selector("div.result-item", timeout=15000)
                    time.sleep(1)
                except:
                    print(f"⚠️ Klikken op pagina {page_num + 1} mislukt.")
                    break
            else:
                print(f"✅ Geen volgende pagina gevonden na {page_num}.")
                break

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(detail_urls, f, ensure_ascii=False, indent=2)

        print(f"✅ Totaal {len(detail_urls)} links opgeslagen in {OUTPUT_FILE}")
        browser.close()

if __name__ == "__main__":
    run_scraper()