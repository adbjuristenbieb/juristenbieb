from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync
import json, time

OUTPUT_FILE = "public/content/leiden_urls_filtered.json"
MAX_PAGES = 83  # We willen pagina 1 t/m 83 aflopen

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

    print("🌐 Open startpagina...")
    page.goto("https://scholarlypublications.universiteitleiden.nl/", timeout=60000)

    # Filters aanklikken
    print("🎯 Pas filters toe...")
    page.click("text=Search all items")
    page.wait_for_selector("text=Show more", timeout=15000)

    page.locator("div.facet-field-faculty >> text=Show more").click()
    page.locator("label:has-text('Leiden Law School')").click()
    page.wait_for_timeout(1000)

    page.locator("div.facet-field-collection >> text=Show more").click()
    page.locator("label:has-text('Institute of Public Law')").click()
    page.wait_for_timeout(1000)

    page.locator("label:has-text('nl')").click()
    page.wait_for_timeout(3000)

    print("📄 Start scraping pagina's...")
    for pagina in range(1, MAX_PAGES + 1):
        print(f"🔁 Pagina {pagina}...")
        if pagina > 1:
            try:
                next_button = page.locator("a.pagination-next")
                if next_button.is_visible():
                    next_button.click()
                    page.wait_for_load_state("networkidle")
                    page.wait_for_timeout(2000)
            except Exception as e:
                print(f"⚠️ Volgende pagina niet gevonden op pagina {pagina}: {e}")
                break

        publicaties = page.locator(".search-result-title a")
        count = publicaties.count()
        for i in range(count):
            try:
                href = publicaties.nth(i).get_attribute("href")
                if href and href.startswith("/handle/1887/"):
                    resultaten.append("https://scholarlypublications.universiteitleiden.nl" + href)
            except:
                continue

    browser.close()

    print(f"✅ Totaal {len(resultaten)} links gevonden. Sla op in {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(resultaten, f, indent=2, ensure_ascii=False)
