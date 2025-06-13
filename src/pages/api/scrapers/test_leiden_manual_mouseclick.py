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

        print("🌐 Open Leiden Scholarly Publications")
        page.goto("https://scholarlypublications.universiteitleiden.nl/", timeout=60000)
        take_screenshot(page, "00_homepage")

        print("🔎 Klik op 'Search all items'")
        page.get_by_role("link", name="Search all items").click()
        page.wait_for_url("**/search**", timeout=15000)
        time.sleep(2)
        take_screenshot(page, "01_search_landing")

        print("🔄 Scroll naar filters")
        for _ in range(6):
            page.mouse.wheel(0, 300)
            time.sleep(0.4)

        print("👆 Klik op 'Show more' bij Faculty (via JS)")
        page.evaluate("""() => {
            const divs = Array.from(document.querySelectorAll('div'));
            const fac = divs.find(div => div.textContent.includes('Faculty'));
            const btn = fac?.querySelector('a.soft-limit');
            if (btn) btn.click();
        }""")
        time.sleep(2)
        take_screenshot(page, "02_showmore_faculty")

        print("🎯 Zoek locatie van 'Leiden Law School'")
        try:
            label = page.locator("label:has-text('Leiden Law School')").first
            label.scroll_into_view_if_needed()
            box = label.bounding_box()
            print(f"📐 Bounding box: {box}")

            if box:
                x = box["x"] + box["width"] / 2
                y = box["y"] + box["height"] / 2
                page.mouse.click(x, y)
                print(f"🖱️ Mouse click at ({x}, {y})")

                page.wait_for_selector("div.dc-loading", state="detached", timeout=30000)
        except Exception as e:
            print(f"⚠️ Klik mislukt: {e}")
        take_screenshot(page, "03_lawschool_clicked")

        print("✅ Check nu of resultaat verlaagt")
        time.sleep(2)
        take_screenshot(page, "04_result_check")

        browser.close()

if __name__ == "__main__":
    run_test()
