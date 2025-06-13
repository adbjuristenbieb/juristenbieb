from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync
import os
import time

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

        print("🌐 Ga naar Leiden Scholarly Publications")
        page.goto("https://scholarlypublications.universiteitleiden.nl/", timeout=60000)
        take_screenshot(page, "00_homepage")

        print("🔎 Klik op 'Search all items'")
        page.get_by_role("link", name="Search all items").click()
        page.wait_for_url("**/search**", timeout=15000)
        time.sleep(2)
        take_screenshot(page, "01_search_landing")

        print("🔄 Scroll naar filters en maak Faculty zichtbaar")
        for _ in range(6):
            page.mouse.wheel(0, 300)
            time.sleep(0.4)

        print("👆 Klik op 'Show more' onder Faculty (via JS-fallback)")
        page.evaluate("""() => {
            const divs = Array.from(document.querySelectorAll('div'));
            const fac = divs.find(div => div.textContent.includes('Faculty'));
            const btn = fac?.querySelector('a.soft-limit');
            if (btn) btn.click();
        }""")
        time.sleep(2)

        print("✅ Klik op 'Leiden Law School'")
        label = page.locator("label:has-text('Leiden Law School')").first
        label.scroll_into_view_if_needed()
        label.click(force=True)
        page.wait_for_selector("div.dc-loading", state="detached", timeout=30000)
        take_screenshot(page, "02_lawschool_clicked")

        print("🌍 Selecteer taal 'nl'")
        label = page.locator("label:has-text('nl')").first
        label.scroll_into_view_if_needed()
        label.click(force=True)
        page.wait_for_selector("div.dc-loading", state="detached", timeout=30000)
        take_screenshot(page, "03_language_nl")

        print("📚 Collection: Show more")
        col_box = page.locator("div.dc-facet-wrapper:has(h3:has-text('Collection'))")
        col_btn = col_box.locator("a.soft-limit").first
        col_btn.scroll_into_view_if_needed()
        col_btn.click(force=True)
        time.sleep(1)

        print("✅ Klik op 'Institute of Public Law'")
        label = page.locator("label:has-text('Institute of Public Law')").first
        label.scroll_into_view_if_needed()
        label.click(force=True)
        page.wait_for_selector("div.dc-loading", state="detached", timeout=30000)
        take_screenshot(page, "04_collection_selected")

        print("🎯 Als dit werkt, verschijnt < 10.000 resultaten")
        time.sleep(2)
        take_screenshot(page, "05_resultaat_check")

        browser.close()

if __name__ == "__main__":
    run_test()
