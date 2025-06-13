from sickle import Sickle
from sickle.models import Record
import json
import re

# Initialiseer OAI-endpoint
sickle = Sickle("https://scholarlypublications.universiteitleiden.nl/oai2")

# Ophalen van records uit Scholarly Repository
records = sickle.ListRecords(metadataPrefix="oai_dc", set="hdl_1887_20765")

resultaten = []

print("⏳ Ophalen records... (alleen Nederlandstalig)")

for i, record in enumerate(records):
    try:
        md = record.metadata
        if "language" not in md or "nl" not in md["language"]:
            continue

        title = md.get("title", ["[geen titel]"])[0]
        authors = md.get("creator", [])
        date = md.get("date", [""])[0]
        subjects = md.get("subject", [])
        url_candidates = md.get("identifier", [])
        url = next((u for u in url_candidates if u.startswith("https://hdl.handle.net")), None)

        resultaten.append({
            "titel": title,
            "auteurs": authors,
            "datum": date,
            "url": url,
            "taal": "nl",
            "onderwerpen": subjects,
            "bron": "Leiden Scholarly Publications (OAI)"
        })

        if i % 50 == 0:
            print(f"✅ {i} records verwerkt...")

        if i >= 2000:
            break  # tijdelijk limiet voor snelheid, pas aan naar wens

    except Exception as e:
        print(f"⚠️ Fout bij record {i}: {e}")
        continue

# Opslaan naar JSON
with open("leiden_oai_nl.json", "w", encoding="utf-8") as f:
    json.dump(resultaten, f, indent=2, ensure_ascii=False)

print(f"\n🎉 Klaar! {len(resultaten)} Nederlandstalige publicaties opgeslagen in leiden_oai_nl.json")
