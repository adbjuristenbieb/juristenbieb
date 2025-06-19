import json
import os
import requests
from openai import OpenAI
import time
from typing import Dict, List, Optional
import re

class PublicationAnalyzer:
    def __init__(self, api_key: str):
        """Initialize the OpenAI client with API key"""
        self.client = OpenAI(api_key=api_key)
        
        # Load available themes and types
        self.themes = self._load_themes()
        self.types = self._load_types()
        
    def _load_themes(self) -> List[str]:
        """Load available themes from themes.json"""
        try:
            with open('public/content/themes.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('themes', [])
        except FileNotFoundError:
            print("Warning: themes.json not found, using default themes")
            return ["Algemene beginselen van behoorlijk bestuur", "Handhaving", "Omgevingsrecht"]
    
    def _load_types(self) -> List[str]:
        """Load available types from types.json"""
        try:
            with open('public/content/types.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('types', [])
        except FileNotFoundError:
            print("Warning: types.json not found, using default types")
            return ["Blog", "Handreiking"]
    
    def _fetch_webpage_content(self, url: str) -> Optional[str]:
        """Fetch content from a webpage"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"Error fetching {url}: {str(e)}")
            return None
    
    def _clean_html_content(self, html_content: str) -> str:
        """Basic HTML cleaning to extract readable text"""
        # Remove script and style elements
        html_content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
        html_content = re.sub(r'<style[^>]*>.*?</style>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove HTML tags
        html_content = re.sub(r'<[^>]+>', ' ', html_content)
        
        # Clean up whitespace
        html_content = re.sub(r'\s+', ' ', html_content)
        html_content = html_content.strip()
        
        # Limit content length for API efficiency
        return html_content[:8000] if len(html_content) > 8000 else html_content
    
    def _create_analysis_prompt(self, publication: Dict, webpage_content: str) -> str:
        """Create the prompt for OpenAI analysis"""
        themes_list = ", ".join(self.themes)
        types_list = ", ".join(self.types)
        
        prompt = f"""
Analyseer de volgende publicatie en vul de ontbrekende gegevens in op basis van de webpagina-inhoud.

PUBLICATIE INFORMATIE:
Titel: {publication.get('titel', '')}
URL: {publication.get('url', '')}
Huidige datum: {publication.get('datum', '')}
Bron: {publication.get('bron', '')}
Huidig type: {publication.get('type', '')}

WEBPAGINA INHOUD:
{webpage_content}

INSTRUCTIES:
1. THEMA: Kies het meest passende thema uit deze lijst: {themes_list}
2. AUTEUR: Identificeer de hoofdauteur (slechts één naam, de belangrijkste auteur)
3. SAMENVATTING: Schrijf een samenvatting van 5-67 zinnen die de kerninhoud weergeeft
4. TYPE: Bevestig of corrigeer het type uit deze lijst: {types_list}

Geef je antwoord in het volgende JSON-formaat:
{{
    "thema": "gekozen thema",
    "auteur": "hoofdauteur naam",
    "samenvatting": "uitgebreide samenvatting van 5-67 zinnen",
    "type": "gekozen type"
}}

Let op:
- Gebruik alleen thema's uit de gegeven lijst
- Gebruik alleen types uit de gegeven lijst
- Geef slechts één hoofdauteur
- Samenvatting moet informatief en volledig zijn
- Antwoord alleen met geldige JSON
"""
        return prompt
    
    def analyze_publication(self, publication: Dict) -> Dict:
        """Analyze a single publication using OpenAI"""
        url = publication.get('url', '')
        if not url:
            print(f"No URL found for publication: {publication.get('titel', 'Unknown')}")
            return publication
        
        print(f"Analyzing: {publication.get('titel', 'Unknown')}")
        
        # Fetch webpage content
        webpage_content = self._fetch_webpage_content(url)
        if not webpage_content:
            print(f"Could not fetch content for: {url}")
            return publication
        
        # Clean HTML content
        clean_content = self._clean_html_content(webpage_content)
        
        # Create prompt
        prompt = self._create_analysis_prompt(publication, clean_content)
        
        try:
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-4o",  # Using the best chat model
                messages=[
                    {"role": "system", "content": "Je bent een expert in Nederlands bestuursrecht en juridische publicaties. Analyseer publicaties nauwkeurig en geef gestructureerde informatie terug."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1500
            )
            
            # Parse response
            response_text = response.choices[0].message.content.strip()
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                analysis_result = json.loads(json_match.group())
                
                # Update publication with analyzed data
                updated_publication = publication.copy()
                updated_publication['thema'] = analysis_result.get('thema', publication.get('thema', ''))
                updated_publication['auteur'] = analysis_result.get('auteur', publication.get('auteur', ''))
                updated_publication['samenvatting'] = analysis_result.get('samenvatting', publication.get('samenvatting', ''))
                updated_publication['type'] = analysis_result.get('type', publication.get('type', ''))
                
                print(f"✓ Successfully analyzed: {publication.get('titel', 'Unknown')}")
                return updated_publication
            else:
                print(f"Could not parse JSON response for: {publication.get('titel', 'Unknown')}")
                return publication
                
        except Exception as e:
            print(f"Error analyzing publication {publication.get('titel', 'Unknown')}: {str(e)}")
            return publication
    
    def analyze_publications_batch(self, publications: List[Dict], start_index: int = 0, batch_size: int = 10) -> List[Dict]:
        """Analyze publications in batches with rate limiting"""
        analyzed_publications = []
        
        for i, publication in enumerate(publications[start_index:], start_index):
            print(f"\nProcessing {i+1}/{len(publications)}: {publication.get('titel', 'Unknown')}")
            
            # Skip if already has all required fields
            if (publication.get('thema') and 
                publication.get('auteur') and 
                publication.get('samenvatting') and 
                publication.get('type')):
                print("✓ Already complete, skipping")
                analyzed_publications.append(publication)
                continue
            
            analyzed_pub = self.analyze_publication(publication)
            analyzed_publications.append(analyzed_pub)
            
            # Rate limiting - wait between requests
            if i < len(publications) - 1:
                print("Waiting 2 seconds before next request...")
                time.sleep(2)
            
            # Save progress every batch_size publications
            if (i + 1) % batch_size == 0:
                self._save_progress(analyzed_publications, i + 1)
        
        return analyzed_publications
    
    def _save_progress(self, publications: List[Dict], count: int):
        """Save progress to a backup file"""
        backup_filename = f"publications_analyzed_progress_{count}.json"
        try:
            with open(backup_filename, 'w', encoding='utf-8') as f:
                json.dump(publications, f, ensure_ascii=False, indent=2)
            print(f"✓ Progress saved to {backup_filename}")
        except Exception as e:
            print(f"Error saving progress: {str(e)}")

def main():
    """Main function to run the analysis"""
    # Get OpenAI API key from environment variable
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set")
        print("Please set your OpenAI API key: export OPENAI_API_KEY='your-api-key-here'")
        return
    
    # Load publications
    try:
        with open('public/content/publicaties.json', 'r', encoding='utf-8') as f:
            publications = json.load(f)
        print(f"Loaded {len(publications)} publications")
    except FileNotFoundError:
        print("Error: publicaties.json not found")
        return
    except json.JSONDecodeError as e:
        print(f"Error parsing publicaties.json: {str(e)}")
        return
    
    # Initialize analyzer
    analyzer = PublicationAnalyzer(api_key)
    
    # Ask user for batch settings
    print("\nAnalysis Settings:")
    start_index = input("Start from index (default 0): ").strip()
    start_index = int(start_index) if start_index.isdigit() else 0
    
    batch_size = input("Batch size for progress saving (default 10): ").strip()
    batch_size = int(batch_size) if batch_size.isdigit() else 10
    
    max_publications = input("Maximum publications to process (default: all): ").strip()
    if max_publications.isdigit():
        publications = publications[:int(max_publications)]
    
    print(f"\nStarting analysis from index {start_index}")
    print(f"Processing {len(publications)} publications")
    print(f"Saving progress every {batch_size} publications")
    
    # Analyze publications
    analyzed_publications = analyzer.analyze_publications_batch(
        publications, start_index, batch_size
    )
    
    # Save final results
    output_filename = 'publicaties_analyzed_final.json'
    try:
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(analyzed_publications, f, ensure_ascii=False, indent=2)
        print(f"\n✓ Final results saved to {output_filename}")
        print(f"✓ Analyzed {len(analyzed_publications)} publications")
    except Exception as e:
        print(f"Error saving final results: {str(e)}")

if __name__ == "__main__":
    main()
