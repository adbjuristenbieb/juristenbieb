from playwright.sync_api import sync_playwright
import json
from pathlib import Path
import subprocess
import re

# ✅ Hersteld: pad naar project root
BASE = Path(__file__).resolve().parents[4]

# Tijdelijke testinstellingen
MAX_PAGINAS = None # Geen limiet voor testen

# Tijdelijk pad voor tests (niet je echte bestand overschrijven)
PAD_VNG = BASE / "public/content/vng_publicaties.json"

def scrape_vng_filtered(page, base_url, thema=None, type_=None):
    print(f"Start scraping van: {base_url}")
    publicaties = []
    page_nr = 0

    while True:
        if MAX_PAGINAS is not None and page_nr >= MAX_PAGINAS:
            print(f"🛑 Test stop: maximum van {MAX_PAGINAS} pagina's bereikt.\n")
            break

        page_nr += 1
        url = f"{base_url}&page={page_nr - 1}"
        print(f"🔄 Bezoek pagina {page_nr}: {url}")
        page.goto(url)
        page.wait_for_timeout(1000)

        sluiten_button = page.locator("button:has-text('Sluiten')").first
        if sluiten_button.is_visible():
            sluiten_button.click()

        items = page.locator('.node-list__item')
        count = items.count()
        print(f"📦 Aantal items op pagina {page_nr}: {count}")

        if count == 0:
            print("❌ Geen items meer, klaar met deze categorie.\n")
            break

        for i in range(count):
            item = items.nth(i)
            try:
                # 🔍 HTML dump voor analyse
                if i == 0:
                    html = item.inner_html()
                    print(f"🧩 HTML-inhoud eerste item op pagina {page_nr}:\n{html}\n")

                title_locator = item.locator('h2 a')
                title_locator.wait_for(timeout=7000)
                titel = title_locator.inner_text()
                link = title_locator.get_attribute('href')

                # Nieuw: datum direct boven titel
                datum = ""
                try:
                    datum_locator = item.locator(".field--node-post-date")
                    if datum_locator.count() > 0:
                        datum_text = datum_locator.inner_text(timeout=3000).strip()
                        print(f"📆 Gevonden datumtekst: '{datum_text}'")
                        match = re.search(r'\d{1,2} \w+ \d{4}', datum_text)
                        if match:
                            datum = match.group(0)
                            print(f"✅ Datum geëxtraheerd: {datum}")
                        else:
                            print(f"❌ Geen herkenbare datum in tekst: '{datum_text}'")
                    else:
                        print(f"❌ Geen .field--node-post-date gevonden bij: {titel}")
                except Exception as e:
                    print(f"⚠️ Fout bij extractie datum ({titel}): {e}")


                publicaties.append({
                    "titel": titel,
                    "url": f"https://vng.nl{link}" if link and link.startswith("/") else link,
                    "datum": datum,
                    "bron": "VNG",
                    "type": type_ or "",
                    "thema": thema or "",
                    "auteur": "",
                    "samenvatting": ""
                })

            except Exception as e:
                print(f"⚠️ Fout bij publicatie {i} op pagina {page_nr}: {e}")

    return publicaties


def scrape_vng_publicaties():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=300)
        page = browser.new_page()

        try:
            # Alles met onderwerp 'Recht'
            data_recht = scrape_vng_filtered(
                page,
                "https://vng.nl/publicaties?rubriek[]=380591",
                thema="Recht"
            )

            # Alles met publicatiesoort 'Handreiking'
            data_handreiking = scrape_vng_filtered(
                page,
                "https://vng.nl/publicaties?publicatie-soort=381222",
                type_="Handreiking"
            )

            alle = data_recht + data_handreiking
            uniek = {item["url"]: item for item in alle}
            resultaat = list(uniek.values())

            print(f"Totaal gevonden publicaties (voor ontdubbelen): {len(alle)}")
            print(f"Unieke publicaties op URL: {len(uniek)}")

            PAD_VNG.parent.mkdir(parents=True, exist_ok=True)
            with open(PAD_VNG, "w", encoding="utf-8") as f:
                json.dump(resultaat, f, indent=2, ensure_ascii=False)

            print(f"✅ {len(resultaat)} unieke publicaties opgeslagen in {PAD_VNG}")

            # ✅ Merge tijdelijk overslaan tijdens testen
            subprocess.run(["python", "merge_publicaties.py"])
            print("🛑 Merge wordt overgeslagen tijdens test. Draai handmatig merge_publicaties.py als alles goed is.")

        finally:
            browser.close()

if __name__ == "__main__":
    scrape_vng_publicaties()
