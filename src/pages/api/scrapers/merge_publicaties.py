import json
from pathlib import Path

# Zorg dat we vanaf de projectroot werken
BASE = Path(__file__).resolve().parents[4]

PAD_PUBLICATIES = BASE / "public" / "content" / "publicaties.json"
PAD_VNG = BASE / "public" / "content" / "vng_publicaties.json"
PAD_BO = BASE / "public" / "content" / "burgeroverheid.json"
PAD_STIBBE = BASE / "public" / "content" / "stibbe.json"
PAD_LEIDEN = BASE / "public" / "content" / "leiden.json"

def laad_json(path):
    print(f"📄 Probeer te laden: {path.resolve()}")
    try:
        if path.exists():
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
                print(f"📥 Loaded {len(data)} items uit {path.name}")
                return data
        else:
            print(f"❌ Bestand niet gevonden: {path.name}")
            return []
    except Exception as e:
        print(f"⚠️ Fout bij laden van {path.name}: {e}")
        return []

def main():
    vng_scrape = laad_json(PAD_VNG)
    burger_overheid = laad_json(PAD_BO)
    stibbe = laad_json(PAD_STIBBE)
    leiden = laad_json(PAD_LEIDEN)

    print("\n📊 Samenvatting geladen data:")
    print(f"📥 VNG: {len(vng_scrape)}")
    print(f"📥 Burger & Overheid: {len(burger_overheid)}")
    print(f"📥 Stibbe: {len(stibbe)}")
    print(f"📥 Leiden: {len(leiden)}")

    # Combineer en ontdubbel op URL
    alles = vng_scrape + burger_overheid + stibbe + leiden
    uniek = {item.get("url"): item for item in alles if item.get("url")}
    resultaat = list(uniek.values())

    PAD_PUBLICATIES.parent.mkdir(parents=True, exist_ok=True)
    with open(PAD_PUBLICATIES, "w", encoding="utf-8") as f:
        json.dump(resultaat, f, indent=2, ensure_ascii=False)

    print(f"\n✅ {len(resultaat)} unieke publicaties opgeslagen in {PAD_PUBLICATIES.name}")


if __name__ == "__main__":
    main()
