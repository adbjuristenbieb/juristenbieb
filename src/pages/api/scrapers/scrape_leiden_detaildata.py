import json, time
from pathlib import Path
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync

INPUT_FILE = "public/content/leiden_detail_urls.json"
OUTPUT_FILE = "public/content/leiden.json"

def run_scraper():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        urls = json.load(f)

    resultaten = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=50)
        context = browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            locale="nl-NL"
        )
        page = context.new_page()
        stealth_sync(page)

        for i, url in enumerate(urls):
            try:
                start = time.time()
                print(f"\n🔎 [{i+1}/{len(urls)}] Verwerk: {url}")
                page.goto(url, timeout=60000)
                page.wait_for_selector("h1", timeout=15000)

                def safe_text(selector, default=""):
                    try:
                        return page.locator(selector).first.inner_text().strip()
                    except:
                        return default

                def all_texts(selector):
                    try:
                        return page.locator(selector).all_inner_texts()
                    except:
                        return []

                resultaat = {
                    "titel": safe_text("h1"),
                    "auteur": ", ".join(all_texts("div.dc-author")),
                    "datum": safe_text("div.dc-date"),
                    "bron": "Leiden Scholarly Publications",
                    "url": url,
                    "thema": ", ".join(all_texts("div.dc-description-tags > a")),
                    "rechtsgebied": "",
                    "collectie": safe_text("div.dc-collections")
                }

                resultaten.append(resultaat)
                print(f"✅ Opgeslagen ({round(time.time() - start, 1)}s)")

                # Tussentijds opslaan
                with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                    json.dump(resultaten, f, indent=2, ensure_ascii=False)

            except Exception as e:
                print(f"⚠️ Fout bij {url[:80]}...: {e}")

        browser.close()
        print(f"\n✅ Totaal {len(resultaten)} publicaties opgeslagen in {OUTPUT_FILE}")

if __name__ == "__main__":
    run_scraper()
