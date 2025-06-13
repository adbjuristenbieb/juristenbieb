from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync
import os
import time
import json

def take_screenshot(page, filename):
    pad = os.path.join("screenshots", f"{filename}.png")
    os.makedirs("screenshots", exist_ok=True)
    page.screenshot(path=pad, full_page=True)
    print(f"📸 Screenshot opgeslagen: {filename}.png")

def run_test():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=150)
        context = browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            locale="nl-NL"
        )
        page = context.new_page()
        stealth_sync(page)

        print("🌐 Open Leiden Scholarly Publications")
        page.goto("https://scholarlypublications.universiteitleiden.nl/", timeout=60000)
        take_screenshot(page, "00_homepage_loaded")

        print("🔎 Klik op 'Search all items'")
        page.get_by_role("link", name="Search all items").click()
        page.wait_for_url("**/search**", timeout=15000)
        time.sleep(2)
        take_screenshot(page, "01_search_landing")

        print("🔄 Scroll om filters te activeren")
        for _ in range(4):
            page.mouse.wheel(0, 300)
            time.sleep(0.5)

        print("🔍 Scroll naar Faculty")
        page.evaluate("""() => {
            const divs = Array.from(document.querySelectorAll('div'));
            const target = divs.find(div => div.textContent.includes('Faculty'));
            if (target) target.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }""")
        time.sleep(1)
        take_screenshot(page, "02_faculty_visible")

        print("👆 Klik op 'Show more' onder Faculty")
        page.evaluate("""() => {
            const divs = Array.from(document.querySelectorAll('div'));
            const fac = divs.find(div => div.textContent.includes('Faculty'));
            const btn = fac?.querySelector('a.soft-limit');
            btn?.click();
        }""")
        time.sleep(2)
        take_screenshot(page, "03_showmore_faculty")

        print("✅ Selecteer 'Leiden Law School' via JS-event")
        page.evaluate("""() => {
            const labels = Array.from(document.querySelectorAll('label'));
            const label = labels.find(l => l.textContent.includes('Leiden Law School') && l.offsetParent !== null);
            if (label) {
                const checkbox = label.querySelector('input[type="checkbox"]');
                if (checkbox && !checkbox.checked) {
                    checkbox.checked = true;
                    checkbox.dispatchEvent(new Event('change', { bubbles: true }));
                }
            }
        }""")
        page.wait_for_selector("div.dc-loading", state="detached", timeout=30000)
        time.sleep(2)
        take_screenshot(page, "04_lawschool_clicked")

        print("🌍 Selecteer taal 'nl'")
        page.evaluate("""() => {
            const labels = Array.from(document.querySelectorAll('label'));
            const label = labels.find(l => l.textContent.includes('nl') && l.offsetParent !== null);
            if (label) {
                const checkbox = label.querySelector('input[type="checkbox"]');
                if (checkbox && !checkbox.checked) {
                    checkbox.checked = true;
                    checkbox.dispatchEvent(new Event('change', { bubbles: true }));
                }
            }
        }""")
        page.wait_for_selector("div.dc-loading", state="detached", timeout=30000)
        time.sleep(2)
        take_screenshot(page, "05_language_nl")

        print("📚 Klik op 'Show more' bij Collection")
        page.evaluate("""() => {
            const divs = Array.from(document.querySelectorAll('div'));
            const col = divs.find(div => div.textContent.includes('Collection'));
            const btn = col?.querySelector('a.soft-limit');
            btn?.click();
        }""")
        time.sleep(2)
        take_screenshot(page, "06_showmore_collection")

        print("✅ Selecteer 'Institute of Public Law'")
        page.evaluate("""() => {
            const labels = Array.from(document.querySelectorAll('label'));
            const label = labels.find(l => l.textContent.includes('Institute of Public Law') && l.offsetParent !== null);
            if (label) {
                const checkbox = label.querySelector('input[type="checkbox"]');
                if (checkbox && !checkbox.checked) {
                    checkbox.checked = true;
                    checkbox.dispatchEvent(new Event('change', { bubbles: true }));
                }
            }
        }""")
        page.wait_for_selector("div.dc-loading", state="detached", timeout=30000)
        time.sleep(2)
        take_screenshot(page, "07_collection_selected")

        print("📂 Klik op 'Show more' bij Topic")
        page.evaluate("""() => {
            const divs = Array.from(document.querySelectorAll('div'));
            const topic = divs.find(div => div.textContent.includes('Topic'));
            const btn = topic?.querySelector('a.soft-limit');
            btn?.click();
        }""")
        time.sleep(2)
        take_screenshot(page, "08_showmore_topic")

        excluded = [
            "Mensenrechten", "Human rights", "Criminal Law and Criminology",
            "Institute of Tax Law and Economics", "arbeidsrecht", "Fair trial", "References"
        ]

        print("⛔️ Deselecteer ongewenste onderwerpen")
        for item in excluded:
            print(f"⛔️ Deselecteer: {item}")
            page.evaluate(f"""() => {{
                const labels = Array.from(document.querySelectorAll('label'));
                for (const label of labels) {{
                    if (label.textContent.includes('{item}') && label.offsetParent !== null) {{
                        const checkbox = label.querySelector('input[type=checkbox]');
                        if (checkbox && checkbox.checked) {{
                            checkbox.checked = false;
                            checkbox.dispatchEvent(new Event('change', {{ bubbles: true }}));
                            break;
                        }}
                    }}
                }}
            }}""")
            page.wait_for_selector("div.dc-loading", state="detached", timeout=30000)
            time.sleep(1.2)
            take_screenshot(page, f"09_exclude_{item.replace(' ', '_')}")

        print("🏁 Filters voltooid.")

        print("⏳ Wacht tot gefilterde resultaten zijn geladen...")
        page.wait_for_selector("div.dc-loading", state="detached", timeout=30000)
        page.wait_for_selector("div.result-item", state="attached", timeout=20000)
        time.sleep(1)

        print("📄 Verwerk resultaten op pagina")
        publicaties = []

        items = page.locator("div.result-item")
        count = items.count()
        print(f"🔍 Aantal gevonden items: {count}")

        for i in range(count):
            try:
                item = items.nth(i)
                titel = item.locator("h3 > a").inner_text()
                url = item.locator("h3 > a").get_attribute("href")
                if url and not url.startswith("http"):
                    url = "https://scholarlypublications.universiteitleiden.nl" + url

                auteurs = item.locator("div.dc-author").all_inner_texts()
                datum_element = item.locator("div.dc-date").first
                datum = datum_element.inner_text() if datum_element else ""

                publicaties.append({
                    "titel": titel.strip(),
                    "url": url,
                    "auteur": ", ".join(auteurs).strip(),
                    "datum": datum.strip(),
                    "bron": "Leiden Scholarly Publications",
                    "thema": "",
                    "rechtsgebied": ""
                })
            except Exception as e:
                print(f"⚠️ Fout bij item {i+1}: {e}")

        pad = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "public", "content", "leiden.json"))
        os.makedirs(os.path.dirname(pad), exist_ok=True)

        with open(pad, "w", encoding="utf-8") as f:
            json.dump(publicaties, f, indent=2, ensure_ascii=False)

        print(f"✅ {len(publicaties)} publicaties opgeslagen in {pad}")

        browser.close()

if __name__ == "__main__":
    run_test()
