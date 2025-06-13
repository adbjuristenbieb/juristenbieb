from playwright.sync_api import sync_playwright
import json
import time

def run_scraper():
    base_url = "https://scholarlypublications.universiteitleiden.nl/search"
    all_results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        print("🌐 Ga naar zoekresultatenpagina")
        page.goto(base_url, timeout=60000)
        page.wait_for_selector("div.result-item", timeout=20000)

        for paginanr in [1, 2]:
            print(f"📄 Verwerk pagina {paginanr}")

            # wacht op resultaten
            page.wait_for_selector("div.result-item", timeout=20000)
            items = page.locator("div.result-item")
            count = items.count()

            for i in range(count):
                try:
                    item = items.nth(i)
                    title = item.locator("h3 > a").inner_text()
                    url = item.locator("h3 > a").get_attribute("href")
                    full_url = page.url.split("/search")[0] + url if url.startswith("/handle") else url

                    all_results.append({
                        "titel": title.strip(),
                        "url": full_url.strip()
                    })
                except:
                    continue

            if paginanr == 1:
                print("➡️ Klik op pagina 2")
                try:
                    next_button = page.locator("li.pager-next > a")
                    if next_button.is_visible():
                        next_button.click()
                        time.sleep(3)
                        page.wait_for_selector("div.result-item", timeout=20000)
                    else:
                        print("⚠️ Geen volgende pagina gevonden")
                        break
                except:
                    print("❌ Fout bij klikken op pagina 2")
                    break

        print(f"✅ Totaal verzameld: {len(all_results)} publicaties")
        with open("leiden_paginas_1_en_2.json", "w", encoding="utf-8") as f:
            json.dump(all_results, f, ensure_ascii=False, indent=2)

        browser.close()

if __name__ == "__main__":
    run_scraper()
