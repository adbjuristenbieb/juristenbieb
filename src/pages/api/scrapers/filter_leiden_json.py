import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[4]
INPUT_FILE = BASE_DIR / "public" / "content" / "leiden.json"
OUTPUT_FILE = BASE_DIR / "public" / "content" / "leiden_filtered.json"

def run_filter():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    gefilterd = [
        pub for pub in data
        if pub.get("collectie", "").strip() == "Institute of Public Law"
    ]

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(gefilterd, f, indent=2, ensure_ascii=False)

    print(f"✅ {len(gefilterd)} publicaties opgeslagen in {OUTPUT_FILE}")

if __name__ == "__main__":
    run_filter()
