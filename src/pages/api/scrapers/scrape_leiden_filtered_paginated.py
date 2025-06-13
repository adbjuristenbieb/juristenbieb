from playwright.sync_api import sync_playwright
import time
import json

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=100)
        page = browser.new_page()
        page.goto("https://scholarlypublications.universiteitleiden.nl/")
        print("🌐 Open Leiden Scholarly Publications")

        # Klik op 'Search all items'
        locator = page.locator("text=Search all items").first
        locator.scroll_into_view_if_needed()
        locator.click()
        print("🔍 Klik op 'Search all items'")
        time.sleep(3)

        # Wacht tot filters zichtbaar zijn
        page.wait_for_selector("text=Faculty")

        # Klik op 'Show more' bij Faculty
        faculty_show_more = page.locator("xpath=//h4[normalize-space()='Faculty']/following-sibling::div//a[contains(text(), 'Show more')]")
        faculty_show_more.scroll_into_view_if_needed()
        faculty_show_more.click()
        time.sleep(1)

        # Selecteer 'Leiden Law School'
        law_school_checkbox = page.locator("label:has-text('Leiden Law School')")
        law_school_checkbox.scroll_into_view_if_needed()
        law_school_checkbox.click()
        print("🏛️ Leiden Law School geselecteerd")
        time.sleep(2)

        # Selecteer taal 'nl'
        language_checkbox = page.locator("label:has-text('nl')")
        language_checkbox.scroll_into_view_if_needed()
        language_checkbox.click()
        print("🗣️ Taal 'nl' geselecteerd")
        time.sleep(2)

        # Klik op 'Show more' bij Collection
        collection_show_more = page.locator("xpath=//h4[normalize-space()='Collection']/following-sibling::div//a[contains(text(), 'Show more')]")
        collection_show_more.scroll_into_view_if_needed()
        collection_show_more.click()
        time.sleep(1)

        # Selecteer 'Institute of Public Law'
        collection_checkbox = page.locator("label:has-text('Institute of Public Law')")
        collection_checkbox.scroll_into_view_if_needed()
        collection_checkbox.click()
        print("📚 Institute of Public Law geselecteerd")
        time.sleep(3)

        # Wacht tot resultaten geladen zijn
        page.wait_for_selector("div.result-item")
        print("📄 Resultaten geladen, begin scraping")

        urls = []
        max_pages = 3  # Pas dit aan naar 83 of meer
        for i in range(max_pages):
            print(f"🔎 Verwerk pagina {i+1}")
            items = page.locator("div.result-item")
            count = items.count()
            for j in range(count):
                link = items.nth(j).locator("a").get_attribute("href")
                if link:
                    full_url = "https://scholarlypublications.universiteitleiden.nl" + link
                    urls.append(full_url)

            # Ga naar volgende pagina
            next_button = page.locator("li.pager__item--next a")
            if next_button.count() == 0:
                break
            next_button.scroll_into_view_if_needed()
            next_button.click()
            time.sleep(2)
            page.wait_for_selector("div.result-item")

        # Bewaar output
        with open("leiden_permalinks.json", "w", encoding="utf-8") as f:
            json.dump(urls, f, indent=2, ensure_ascii=False)
        print(f"✅ {len(urls)} permalinks opgeslagen in leiden_permalinks.json")

        browser.close()

if __name__ == "__main__":
    run()
