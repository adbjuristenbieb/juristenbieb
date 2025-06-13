import time
import json
import os
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync

MAX_PAGES = 5
BASE_URL = "https://scholarlypublications.universiteitleiden.nl"

def scrape_resultaten_van_pagina(page):
    resultaten = []
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

            resultaten.append({
                "titel": title,
                "url": url,
                "auteur": author,
                "jaar": year,
                "type": genre,
                "bron": "Leiden Scholarly Publications"
            })

        except Exception as e:
            print(f"⚠️ Fout bij item: {e}")
    return resultaten

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

        alle_resultaten = []

        for pagina in range(1, MAX_PAGES + 1):
            url = f"{BASE_URL}/search?type=edismax&page={pagina}"
            print(f"🔄 Ga naar pagina {pagina}: {url}")
            try:
                page.goto(url, timeout=60000)
                page.wait_for_selector("div.result-item", timeout=20000)
                time.sleep(1)
                resultaten = scrape_resultaten_van_pagina(page)
                print(f"📄 {len(resultaten)} resultaten op pagina {pagina}")
                alle_resultaten.extend(resultaten)
            except Exception as e:
                print(f"❌ Fout bij pagina {pagina}: {e}")
                continue

        pad = os.path.abspath(os.path.join("public", "content", "leiden_zoekresultaten.json"))
        os.makedirs(os.path.dirname(pad), exist_ok=True)

        with open(pad, "w", encoding="utf-8") as f:
            json.dump(alle_resultaten, f, ensure_ascii=False, indent=2)

        print(f"✅ Totaal {len(alle_resultaten)} publicaties opgeslagen in {pad}")
        browser.close()

if __name__ == "__main__":
    run_scraper()
