import time
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync
import json
import os

BASE_URL = "https://scholarlypublications.universiteitleiden.nl"
START_URL = f"{BASE_URL}/search?type=edismax"
MAX_PAGES = 5  # Pas dit aan voor meer

def scrape_page(page):
    results = []
    items = page.query_selector_all("div.result-item")
    for item in items:
        try:
            title_elem = item.query_selector("dd.mods-titleinfo-title-custom-ms a")
            title = title_elem.inner_text().strip()
            relative_url = title_elem.get_attribute("href")
            url = BASE_URL + relative_url if relative_url.startswith("/") else relative_url

            author_elem = item.query_selector("dd.mods-name-authority-local-ms")
            author = author_elem.inner_text().strip() if author_elem else None

            year_text = item.inner_text()
            year = None
            if "(" in year_text and ")" in year_text:
                try:
                    year = int(year_text.split("(")[-1].split(")")[0])
                except:
                    pass

            genre_elem = item.query_selector("dd.mods-genre-authority-local-ms")
            genre = genre_elem.inner_text().strip() if genre_elem else None

            results.append({
                "titel": title,
                "url": url,
                "auteur": author,
                "jaar": year,
                "type": genre,
                "bron": "Leiden Scholarly Publications"
            })
        except Exception as e:
            print("❌ Fout bij item:", e)
    return results

def run_scraper():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            locale="nl-NL"
        )
        page = context.new_page()
        stealth_sync(page)

        all_results = []

        for page_num in range(1, MAX_PAGES + 1):
            url = f"{START_URL}&page={page_num}"
            print(f"🔄 Bezoek pagina {page_num}: {url}")
            try:
                page.goto(url, timeout=60000)
            except Exception as e:
                print(f"⚠️ Eerste poging mislukt op pagina {page_num}: {e}")
                time.sleep(3)
                try:
                    page.goto(url, timeout=60000)
                except Exception as e2:
                    print(f"❌ Tweede poging ook mislukt: {e2}")
                    continue

            try:
                page.wait_for_selector("div.result-item", timeout=20000)
                page_results = scrape_page(page)
                all_results.extend(page_results)
                time.sleep(1)
            except Exception as e:
                print(f"⚠️ Fout bij verwerken pagina {page_num}: {e}")

        output_path = "public/content/leiden_zoekresultaten.json"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(all_results, f, ensure_ascii=False, indent=2)

        print(f"✅ {len(all_results)} publicaties opgeslagen in {output_path}")
        browser.close()

if __name__ == "__main__":
    run_scraper()
