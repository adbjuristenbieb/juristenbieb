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

def extract_publication_data(item):
    """Extract publication data from a result item"""
    try:
        # Try different selectors for title
        title_selectors = [
            "h3 a",
            ".result-title a", 
            "dd.mods-titleinfo-title-custom-ms a",
            "a[href*='/handle/']",
            "a"  # fallback
        ]
        
        titel = ""
        url = ""
        
        for selector in title_selectors:
            title_elem = item.locator(selector).first
            if title_elem.count() > 0:
                try:
                    titel = title_elem.inner_text().strip()
                    url = title_elem.get_attribute("href")
                    if titel and titel != "Leiden University\nScholarly Publications" and titel != "":
                        break
                except:
                    continue
        
        # Clean up title
        if titel:
            titel = titel.replace("\n", " ").strip()
        
        # Ensure full URL
        if url and not url.startswith("http"):
            url = "https://scholarlypublications.universiteitleiden.nl" + url
        
        # Try different selectors for author
        author_selectors = [
            ".dc-author",
            ".result-author",
            "dd.mods-name-personal-ms",
            "[class*='author']"
        ]
        
        auteurs = []
        for selector in author_selectors:
            try:
                author_elems = item.locator(selector)
                if author_elems.count() > 0:
                    for i in range(author_elems.count()):
                        author_text = author_elems.nth(i).inner_text().strip()
                        if author_text:
                            auteurs.append(author_text)
                    if auteurs:
                        break
            except:
                continue
        
        # Try different selectors for date
        date_selectors = [
            ".dc-date",
            ".result-date", 
            "dd.mods-origininfo-dateissued-ms",
            "[class*='date']"
        ]
        
        datum = ""
        for selector in date_selectors:
            try:
                date_elem = item.locator(selector).first
                if date_elem.count() > 0:
                    datum = date_elem.inner_text().strip()
                    if datum:
                        break
            except:
                continue
        
        return {
            "titel": titel,
            "url": url,
            "auteur": ", ".join(auteurs),
            "datum": datum,
            "bron": "Leiden Scholarly Publications",
            "type": "",
            "thema": "",
            "samenvatting": ""
        }
        
    except Exception as e:
        print(f"⚠️ Fout bij extractie: {e}")
        return None

def run_final_nl_scraper():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
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
        time.sleep(3)
        take_screenshot(page, "01_search_landing")

        print("🔄 Scroll om filters te activeren")
        for _ in range(6):
            page.mouse.wheel(0, 400)
            time.sleep(1)
        take_screenshot(page, "02_after_scroll")

        # Step 1: Click the + button for Institute of Public Law (proven working method)
        print("🏛️ Selecteer 'Institute of Public Law' (bewezen werkende methode)")
        
        institute_selected = False
        for attempt in range(3):
            print(f"🔄 Poging {attempt + 1} om Institute of Public Law + te klikken...")
            
            result = page.evaluate("""() => {
                // Find all elements that contain "Institute of Public Law"
                const walker = document.createTreeWalker(
                    document.body,
                    NodeFilter.SHOW_TEXT,
                    null,
                    false
                );
                
                let node;
                while (node = walker.nextNode()) {
                    if (node.textContent.includes('Institute of Public Law')) {
                        // Found text node, now look for nearby clickable elements
                        let parent = node.parentElement;
                        
                        // Go up the DOM tree to find the filter container
                        for (let i = 0; i < 5 && parent; i++) {
                            // Look for + symbols in this container
                            const clickableElements = parent.querySelectorAll('a, button, span, div');
                            
                            for (let elem of clickableElements) {
                                const text = elem.textContent || '';
                                const className = elem.className || '';
                                
                                // Look for the + button (we know this works)
                                if (text.trim() === '+' && className.includes('plus')) {
                                    elem.scrollIntoView({ behavior: 'smooth', block: 'center' });
                                    elem.click();
                                    return 'Clicked Institute of Public Law + button: ' + text + ' (class: ' + className + ')';
                                }
                            }
                            
                            parent = parent.parentElement;
                        }
                    }
                }
                
                return 'Institute of Public Law + button not found';
            }""")
            
            print(f"   Result: {result}")
            
            if result.startswith('Clicked'):
                time.sleep(5)  # Wait for filter to apply
                institute_selected = True
                break
            
            time.sleep(2)
        
        if not institute_selected:
            print("❌ FAILED: Could not click Institute of Public Law + button")
            browser.close()
            return []
        
        take_screenshot(page, "03_institute_selected")
        
        # Check URL to see if filter was applied
        current_url = page.url
        print(f"🔗 URL after Institute: {current_url}")

        # Step 2: Click the + button for Dutch language (nl) - EXACT SAME METHOD as Institute
        print("🌍 Selecteer Nederlandse taal 'nl' (EXACT SAME METHOD als Institute)")
        
        dutch_selected = False
        for attempt in range(5):
            print(f"🔄 Poging {attempt + 1} om Nederlandse taal + te klikken...")
            
            result = page.evaluate("""() => {
                // Find all elements that contain "nl" - EXACT SAME APPROACH as Institute of Public Law
                const walker = document.createTreeWalker(
                    document.body,
                    NodeFilter.SHOW_TEXT,
                    null,
                    false
                );
                
                let node;
                while (node = walker.nextNode()) {
                    const text = node.textContent.trim();
                    
                    // Look for "nl" with a number in parentheses - be very specific
                    if (text.startsWith('nl ') && text.includes('(') && text.includes(')')) {
                        console.log('Found nl text node:', text);
                        
                        // Found text node, now look for nearby clickable elements - EXACT SAME as Institute
                        let parent = node.parentElement;
                        
                        // Go up the DOM tree to find the filter container - EXACT SAME as Institute
                        for (let i = 0; i < 5 && parent; i++) {
                            // Look for + symbols in this container - EXACT SAME as Institute
                            const clickableElements = parent.querySelectorAll('a, button, span, div');
                            
                            for (let elem of clickableElements) {
                                const elemText = elem.textContent || '';
                                const className = elem.className || '';
                                
                                // Look for the + button - EXACT SAME as Institute
                                if (elemText.trim() === '+' && className.includes('plus')) {
                                    console.log('Found + button for nl:', elemText, className);
                                    elem.scrollIntoView({ behavior: 'smooth', block: 'center' });
                                    elem.click();
                                    return 'Clicked Dutch nl + button: ' + elemText + ' (class: ' + className + ') for text: ' + text;
                                }
                            }
                            
                            parent = parent.parentElement;
                        }
                    }
                }
                
                // Also try exact "nl" match
                const walker2 = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, null, false);
                let node2;
                while (node2 = walker2.nextNode()) {
                    const text = node2.textContent.trim();
                    
                    // Try exact match for "nl (number)"
                    if (text === 'nl' || (text.startsWith('nl') && text.includes('(') && text.length < 20)) {
                        console.log('Found exact nl text node:', text);
                        
                        let parent = node2.parentElement;
                        
                        for (let i = 0; i < 5 && parent; i++) {
                            const clickableElements = parent.querySelectorAll('a, button, span, div');
                            
                            for (let elem of clickableElements) {
                                const elemText = elem.textContent || '';
                                const className = elem.className || '';
                                
                                if (elemText.trim() === '+' && className.includes('plus')) {
                                    console.log('Found + button for exact nl:', elemText, className);
                                    elem.scrollIntoView({ behavior: 'smooth', block: 'center' });
                                    elem.click();
                                    return 'Clicked Dutch exact nl + button: ' + elemText + ' (class: ' + className + ') for text: ' + text;
                                }
                            }
                            
                            parent = parent.parentElement;
                        }
                    }
                }
                
                return 'Dutch nl + button not found with exact same method';
            }""")
            
            print(f"   Result: {result}")
            
            if result.startswith('Clicked'):
                time.sleep(5)  # Wait for filter to apply
                dutch_selected = True
                break
            
            # Scroll a bit more to make sure language section is visible
            page.mouse.wheel(0, 200)
            time.sleep(2)
        
        if not dutch_selected:
            print("⚠️ WARNING: Could not click Dutch language + button after all attempts")
            print("🔄 Continuing with current filters...")
        
        take_screenshot(page, "04_all_filters_applied")
        
        # Final URL check
        final_url = page.url
        print(f"🔗 Final URL: {final_url}")

        # Wait for results to load
        print("⏳ Wacht op resultaten...")
        time.sleep(5)
        
        # Verify we have law-related content
        print("🔍 Verificatie van content...")
        sample_titles = page.evaluate("""() => {
            const resultElements = document.querySelectorAll('[class*="result"], .result-item, .search-result, .item');
            const titles = [];
            for (let i = 0; i < Math.min(10, resultElements.length); i++) {
                const titleElement = resultElements[i].querySelector('h3 a, .result-title a, a[href*="/handle/"], a');
                if (titleElement) {
                    const title = titleElement.textContent.trim();
                    if (title && title !== "Leiden University Scholarly Publications") {
                        titles.push(title);
                    }
                }
            }
            return titles;
        }""")
        
        print("📋 Eerste 10 titels:")
        law_count = 0
        dutch_count = 0
        for i, title in enumerate(sample_titles):
            print(f"  {i+1}. {title[:80]}...")
            if any(keyword in title.lower() for keyword in ['law', 'legal', 'recht', 'juridisch', 'court', 'wetgeving', 'grondwet', 'constitutional', 'administrative']):
                law_count += 1
            if any(keyword in title.lower() for keyword in ['recht', 'juridisch', 'wetgeving', 'grondwet', 'artikel', 'wet', 'van', 'de', 'het', 'een']):
                dutch_count += 1
        
        print(f"📊 {law_count}/{len(sample_titles)} titels lijken juridisch gerelateerd")
        print(f"📊 {dutch_count}/{len(sample_titles)} titels lijken Nederlands te zijn")
        
        if law_count >= len(sample_titles) * 0.7:
            print("✅ Content verificatie geslaagd - juridische content!")
        else:
            print("⚠️ Waarschuwing: Mogelijk niet alle filters correct toegepast")

        # Start scraping all pages
        print("📄 Start scraping van alle pagina's...")
        publicaties = []
        page_num = 1
        max_pages = 200
        consecutive_empty_pages = 0
        max_consecutive_empty = 3

        while page_num <= max_pages and consecutive_empty_pages < max_consecutive_empty:
            print(f"📄 Verwerk pagina {page_num} (totaal tot nu toe: {len(publicaties)})")
            
            # Wait for page to be stable
            try:
                page.wait_for_load_state("networkidle", timeout=15000)
            except:
                print("⚠️ Timeout bij wachten op networkidle, ga door...")
            
            time.sleep(2)
            
            # Try multiple selectors for result items
            selectors_to_try = ["div.result-item", ".result", ".search-result", ".item", "[class*='result']"]
            items = None
            count = 0
            
            for selector in selectors_to_try:
                items = page.locator(selector)
                count = items.count()
                if count > 0:
                    print(f"🔍 Aantal gevonden items op pagina {page_num} met selector '{selector}': {count}")
                    break
            
            if count == 0:
                print(f"❌ Geen items gevonden op pagina {page_num}")
                consecutive_empty_pages += 1
                if consecutive_empty_pages < max_consecutive_empty:
                    try:
                        next_button = page.locator(f"a[aria-label='Go to page {page_num + 1}']")
                        if next_button.count() > 0:
                            next_button.first.click()
                            page.wait_for_selector("div.dc-loading", state="detached", timeout=30000)
                            time.sleep(3)
                            page_num += 1
                            continue
                    except:
                        pass
                break

            # Reset consecutive empty pages counter
            consecutive_empty_pages = 0

            # Process items on current page
            page_items_added = 0
            for i in range(count):
                try:
                    item = items.nth(i)
                    pub_data = extract_publication_data(item)
                    if pub_data and pub_data["titel"] and pub_data["titel"] != "Leiden University\nScholarly Publications":
                        # Check for duplicates
                        is_duplicate = False
                        for existing in publicaties:
                            if existing["titel"] == pub_data["titel"] and existing["url"] == pub_data["url"]:
                                is_duplicate = True
                                break
                        
                        if not is_duplicate:
                            publicaties.append(pub_data)
                            page_items_added += 1
                            print(f"✅ Toegevoegd ({len(publicaties)}): {pub_data['titel'][:50]}...")
                        else:
                            print(f"⚠️ Duplicaat overgeslagen: {pub_data['titel'][:50]}...")
                    else:
                        print(f"⚠️ Item {i+1} overgeslagen (geen geldige titel)")
                except Exception as e:
                    print(f"⚠️ Fout bij item {i+1}: {e}")

            print(f"📊 Pagina {page_num} voltooid: {page_items_added} nieuwe items toegevoegd (totaal: {len(publicaties)})")

            # Try to go to next page - improved pagination logic
            next_page_found = False
            
            # Try multiple pagination selectors
            pagination_selectors = [
                f"a[aria-label='Go to page {page_num + 1}']",
                f"a[href*='page={page_num}']",  # Next page in URL
                "a.next",
                "a[rel='next']",
                ".pagination .next",
                ".pager-next",
                "a[title*='Next']",
                "a[title*='next']",
                ".pagination a:last-child",
                f"a:has-text('{page_num + 1}')",  # Page number link
                "a:has-text('Next')",
                "a:has-text('›')",
                "a:has-text('»')"
            ]
            
            for selector in pagination_selectors:
                try:
                    print(f"🔍 Probeer selector: {selector}")
                    next_button = page.locator(selector)
                    if next_button.count() > 0:
                        print(f"✅ Gevonden met selector: {selector}")
                        next_button.first.scroll_into_view_if_needed()
                        time.sleep(1)
                        
                        # Get current URL before clicking
                        current_url = page.url
                        print(f"🔗 Huidige URL: {current_url}")
                        
                        next_button.first.click()
                        
                        # Wait for URL to change or loading to complete
                        try:
                            page.wait_for_function(f"window.location.href !== '{current_url}'", timeout=10000)
                        except:
                            try:
                                page.wait_for_selector("div.dc-loading", state="detached", timeout=10000)
                            except:
                                pass
                        
                        time.sleep(3)
                        
                        # Check if URL actually changed
                        new_url = page.url
                        print(f"🔗 Nieuwe URL: {new_url}")
                        
                        if new_url != current_url:
                            page_num += 1
                            next_page_found = True
                            print(f"✅ Succesvol naar pagina {page_num} gegaan")
                            break
                        else:
                            print(f"⚠️ URL niet veranderd, probeer volgende selector")
                            
                except Exception as e:
                    print(f"⚠️ Fout met selector {selector}: {e}")
                    continue

            # If no pagination button found, try direct URL manipulation
            if not next_page_found:
                try:
                    current_url = page.url
                    print(f"🔗 Probeer directe URL manipulatie vanaf: {current_url}")
                    
                    # Try to construct next page URL
                    if "page=" in current_url:
                        # Replace existing page parameter
                        import re
                        new_url = re.sub(r'page=\d+', f'page={page_num}', current_url)
                    else:
                        # Add page parameter
                        separator = "&" if "?" in current_url else "?"
                        new_url = f"{current_url}{separator}page={page_num}"
                    
                    print(f"🔗 Probeer URL: {new_url}")
                    page.goto(new_url, timeout=30000)
                    time.sleep(3)
                    
                    # Check if we got results
                    test_items = page.locator("[class*='result']")
                    if test_items.count() > 0:
                        page_num += 1
                        next_page_found = True
                        print(f"✅ Succesvol naar pagina {page_num} via directe URL")
                    else:
                        print(f"❌ Geen resultaten op pagina {page_num} via directe URL")
                        
                except Exception as e:
                    print(f"⚠️ Fout bij directe URL manipulatie: {e}")

            if not next_page_found:
                print(f"✅ Geen volgende pagina gevonden na pagina {page_num}")
                break

        print(f"🎯 Scraping voltooid! Totaal aantal publicaties: {len(publicaties)}")
        
        # Check if we got close to the expected 1667 items
        if len(publicaties) >= 1600:
            print("✅ Succesvol! Meer dan 1600 publicaties verzameld.")
        elif len(publicaties) >= 1000:
            print("⚠️ Gedeeltelijk succesvol. Meer dan 1000 publicaties verzameld.")
        elif len(publicaties) >= 100:
            print("⚠️ Beperkt succesvol. Meer dan 100 publicaties verzameld.")
        else:
            print("❌ Mogelijk probleem. Minder dan 100 publicaties verzameld.")

        # Save results
        pad = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "public", "content", "leiden.json"))
        os.makedirs(os.path.dirname(pad), exist_ok=True)

        with open(pad, "w", encoding="utf-8") as f:
            json.dump(publicaties, f, indent=2, ensure_ascii=False)

        print(f"✅ {len(publicaties)} publicaties opgeslagen in {pad}")

        browser.close()
        
        # Run merge to update main publicaties.json
        try:
            import subprocess
            subprocess.run(["python", "merge_publicaties.py"], cwd=os.path.dirname(__file__))
            print("🔄 Merge publicaties uitgevoerd")
        except Exception as e:
            print(f"⚠️ Fout bij merge: {e}")
        
        return publicaties

if __name__ == "__main__":
    run_final_nl_scraper()
