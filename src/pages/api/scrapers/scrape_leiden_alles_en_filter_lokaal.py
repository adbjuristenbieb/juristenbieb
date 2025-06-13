from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync
import json
import time
import os

# Configureer deze naar wens
MAX_PAGES = 5  # Test eerst met 5 pagina’s

# Uitsluitingen op onderwerp
UITGESLOTEN_ONDERWERPEN = [
    "Mensenrechten", "Human rights", "arbeidsrecht", "Fair trial", "References"
]

def extract_metadata(result):
    try:
        titel = result.query_selector("h3").inner_text().strip()
        url = result.query_selector("a").get_attribute("href")
        if not url.startswith("http"):
            url = "https://scholarlypublications.universiteitleiden.nl" + url
        auteurs = result.query_selector(".dc-author") or result.query_selector(".author")
        auteur = auteurs.inner_text().strip() if auteurs else ""
        datum = result.query_selector(".dc-date") or result.query_selector(".date")
        date_text = datum.inner_text().strip() if datum else ""
        collection_el = result.query_selector(".dc-collection")
        collectie = collection_el.inner_text().strip() if collection_el else ""
        taal_el = result.query_selector(".language")
        taal = taal_el.inner_text().strip() if taal_el else ""
        topics = [el.inner_text().strip() for el in result.query_selector_all(".dc-subject")]
        return {
            "titel": titel,
            "url": url,
            "auteur": auteur,
            "datum": date_text,
            "bron": "Universiteit Leiden",
            "type": "Scholarly publication",
            "thema": topics,
            "taal": taal,
            "collectie": collectie
        }
    except Exception as e:
        return None

def filter_result(item):
    if item is None:
        return False
    if item["taal"].lower() != "nl":
        return False
    if "Institute of Public Law" not in item.get("collectie", ""):
        return False
    for onderwerp in UITGESLOTEN_ONDERWERPEN:
        if onderwerp in item.get("thema", []):
            return False
    return True

def run_scraper():
    all_results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=150)
        context = browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            locale="nl-NL"
        )
        page = context.new_page()
        stealth_sync(page)

        for page_num in range(1, MAX_PAGES + 1):
            print(f"🔄 Bezoek pagina {page_num}")
            page.goto(f"https://scholarlypublications.universiteitleiden.nl/search?page={page_num}", timeout=60000)
            page.wait_for_selector("div.result-item", timeout=20000)
            time.sleep(1)
            items = page.query_selector_all("div.result-item")
            for item in items:
                metadata = extract_metadata(item)
                if filter_result(metadata):
                    all_results.append(metadata)

        browser.close()

    print(f"✅ Totaal gefilterde resultaten: {len(all_results)}")
    os.makedirs("public/content", exist_ok=True)
    with open("public/content/leiden_filtered.json", "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    print("📄 Bestand opgeslagen: public/content/leiden_filtered.json")

if __name__ == "__main__":
    run_scraper()
