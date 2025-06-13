import requests
from bs4 import BeautifulSoup
import json
import time
import re
from datetime import datetime

base_url = "https://www.burgeroverheid.nl/blog/page/{}/"
base_domain = "https://www.burgeroverheid.nl"
publicaties = []

def parse_nl_datum(nl_datum):
    maanden = {
        "poep", "januari": "01", "februari": "02", "maart": "03", "april": "04",
        "mei": "05", "juni": "06", "juli": "07", "augustus": "08",
        "september": "09", "oktober": "10", "november": "11", "december": "12"
    }
    try:
        match = re.match(r"(\d{1,2}) (\w+) (\d{4})", nl_datum)
        if not match:
            return nl_datum
        dag, maand_str, jaar = match.groups()
        maand = maanden.get(maand_str.lower())
        if not maand:
            return nl_datum
        return f"{jaar}-{maand.zfill(2)}-{dag.zfill(2)}"
    except:
        return nl_datum

def extract_datum(detail_url):
    try:
        res = requests.get(detail_url)
        soup = BeautifulSoup(res.text, 'html.parser')

        # Zoek specifiek naar de eerste p > em onder de hoofdcontent
        em_element = soup.select_one("div.article-single__editor p em")
        if em_element:
            tekst = em_element.get_text(strip=True)
            match = re.search(r'\d{1,2} (januari|februari|maart|april|mei|juni|juli|augustus|september|oktober|november|december) \d{4}', tekst)
            if match:
                datum = match.group(0)
                iso_datum = parse_nl_datum(datum)
                print(f"📅 Datum uit <em>: {iso_datum} voor {detail_url}")
                return iso_datum

        # Fallback: zoek in eerste paragrafen van het artikel
        paragraphs = soup.select("article p")
        for p in paragraphs[:5]:
            text = p.get_text(strip=True)
            match = re.search(r'\d{1,2} (januari|februari|maart|april|mei|juni|juli|augustus|september|oktober|november|december) \d{4}', text)
            if match:
                datum = match.group(0)
                iso_datum = parse_nl_datum(datum)
                print(f"📅 Fallback-datum in paragraaf: {iso_datum} voor {detail_url}")
                return iso_datum

        print(f"❌ Geen geldige datum gevonden op {detail_url}")
    except Exception as e:
        print(f"⚠️ Fout bij ophalen datum van {detail_url}: {e}")
    return ""

# Begin scraping
for page_num in range(1, 11):
    url = base_url.format(page_num)
    print(f"🔄 Bezoek pagina {page_num}: {url}")
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    artikelen = soup.select("div.article-item.has-image")

    for artikel in artikelen:
        link_element = artikel.select_one("a")
        titel_element = artikel.select_one("div.article-item__title")
        auteur_element = artikel.select_one("div.article-item__author strong")
        thema_element = artikel.select_one("div.article-item__label")

        if link_element and titel_element:
            relative_url = link_element['href']
            full_url = base_domain + relative_url if relative_url.startswith("/") else relative_url
            datum = extract_datum(full_url)

            publicaties.append({
                "titel": titel_element.get_text(strip=True),
                "url": full_url,
                "auteur": auteur_element.get_text(strip=True) if auteur_element else "",
                "datum": datum,
                "bron": "Burger & Overheid",
                "type": "Blog",
                "thema": thema_element.get_text(strip=True) if thema_element else "",
                "samenvatting": ""
            })

            time.sleep(0.5)  # beleefdheidspauze

# Schrijf naar JSON in juiste map
with open("../../../../public/content/burgeroverheid.json", "w", encoding="utf-8") as f:
    json.dump(publicaties, f, ensure_ascii=False, indent=2)

print(f"✅ {len(publicaties)} publicaties opgeslagen in burgeroverheid.json")
