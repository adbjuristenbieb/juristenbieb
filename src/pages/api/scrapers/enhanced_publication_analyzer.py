import json
import os
import requests
from openai import OpenAI
import re
from typing import Dict, List, Optional
import time

# Import OpenAI API key from config
from config import OPENAI_API_KEY

def load_themes() -> List[str]:
    """Load available themes from themes.json"""
    try:
        with open('../../../../public/content/themes.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('themes', [])
    except FileNotFoundError:
        return ["Algemene beginselen van behoorlijk bestuur", "Handhaving", "Omgevingsrecht"]

def load_types() -> List[str]:
    """Load available types from types.json"""
    try:
        with open('../../../../public/content/types.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('types', [])
    except FileNotFoundError:
        return ["Blog", "Handreiking"]

def fetch_webpage_content(url: str) -> Optional[str]:
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

def clean_html_content(html_content: str) -> str:
    """Basic HTML cleaning to extract readable text"""
    # Remove script and style elements
    html_content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
    html_content = re.sub(r'<style[^>]*>.*?</style>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
    
    # Remove HTML tags
    html_content = re.sub(r'<[^>]+>', ' ', html_content)
    
    # Clean up whitespace
    html_content = re.sub(r'\s+', ' ', html_content)
    html_content = html_content.strip()
    
    # Limit content length for API efficiency (increased for enhanced analysis)
    return html_content[:12000] if len(html_content) > 12000 else html_content

def create_enhanced_analysis_prompt(publication: Dict, webpage_content: str, themes: List[str], types: List[str]) -> str:
    """Create the enhanced prompt for OpenAI analysis"""
    themes_list = ", ".join(themes)
    types_list = ", ".join(types)
    
    prompt = f"""
Analyseer de volgende Nederlandse juridische/bestuurlijke publicatie zeer uitgebreid en vul alle ontbrekende gegevens in op basis van de webpagina-inhoud.

PUBLICATIE INFORMATIE:
Titel: {publication.get('titel', '')}
URL: {publication.get('url', '')}
Huidige datum: {publication.get('datum', '')}
Bron: {publication.get('bron', '')}
Huidig type: {publication.get('type', '')}

WEBPAGINA INHOUD:
{webpage_content}

INSTRUCTIES - Analyseer en vul ALLE volgende velden in:

1. THEMA: Kies het meest passende thema uit: {themes_list}
2. AUTEUR: Identificeer de hoofdauteur (één naam/organisatie)
3. SAMENVATTING: Uitgebreide samenvatting van 5-67 zinnen
4. TYPE: Bevestig/corrigeer uit: {types_list}
5. KEYWORDS: 3-8 kernwoorden voor filtering/SEO (komma-gescheiden)
6. AUDIENCE: Doelgroep (bv. "Beleidsmedewerkers", "Juridisch adviseurs", "Gemeenten")
7. IMPACT: Korte inschatting van relevantie/impact op beleid
8. READ_TIME: Geschatte leestijd in minuten (bv. "5 min")
9. TAKEAWAYS: 3-5 belangrijkste punten als bulletpoints
10. SUMMARY_ONE_LINER: Samenvatting in één zin voor previews
11. EMBARGO_STATUS: Controleer of publicatie onder embargo valt - "Embargo tot [datum]" of "Geen embargo"
12. SUBTYPE: Meer specifiek dan type (bv. "Modelverordening", "Raadsvoorstel", "Nieuwsbericht")
13. LANGUAGE_LEVEL: "Beleidsmatig", "Juridisch technisch", of "Toegankelijk voor leken"
14. EXPIRY_OR_VALIDITY: Tijdgevoeligheid (bv. "Geldig tot [datum]" of "Structureel toepasbaar")
15. RELEVANCE_SCORE: Relevantiescore 1-10 voor beleidsrelevantie

Geef je antwoord in het volgende JSON-formaat:
{{
    "thema": "gekozen thema",
    "auteur": "hoofdauteur naam",
    "samenvatting": "uitgebreide samenvatting van 5-67 zinnen",
    "type": "gekozen type",
    "keywords": "keyword1, keyword2, keyword3, keyword4",
    "audience": "doelgroep beschrijving",
    "impact": "korte impact inschatting",
    "read_time": "X min",
    "takeaways": [
        "Belangrijk punt 1",
        "Belangrijk punt 2", 
        "Belangrijk punt 3"
    ],
    "summary_one_liner": "korte samenvatting in één zin",
    "embargo_status": "Embargo tot [datum]" of "Geen embargo",
    "subtype": "specifieke categorie",
    "language_level": "taalniveau",
    "expiry_or_validity": "tijdgevoeligheid",
    "relevance_score": 8
}}

Let op:
- Gebruik alleen thema's en types uit de gegeven lijsten
- Keywords moeten relevant zijn voor Nederlandse bestuursrecht
- Impact moet specifiek zijn over beleidsrelevantie
- Takeaways als array van strings
- Relevance_score als getal 1-10
- Embargo_status: Zoek naar embargo-informatie in de tekst, anders "Geen embargo"
- Alle velden zijn verplicht
- Antwoord alleen met geldige JSON
"""
    return prompt

def analyze_enhanced_publication(publication: Dict, api_key: str) -> Dict:
    """
    Analyze a single publication with enhanced attributes using OpenAI API
    
    Args:
        publication: Dictionary containing publication data
        api_key: OpenAI API key
        
    Returns:
        Updated publication dictionary with all analyzed data
    """
    client = OpenAI(api_key=api_key)
    themes = load_themes()
    types = load_types()
    
    url = publication.get('url', '')
    if not url:
        print(f"No URL found for publication: {publication.get('titel', 'Unknown')}")
        return publication
    
    print(f"Analyzing (Enhanced): {publication.get('titel', 'Unknown')}")
    
    # Fetch webpage content
    webpage_content = fetch_webpage_content(url)
    if not webpage_content:
        print(f"Could not fetch content for: {url}")
        return publication
    
    # Clean HTML content
    clean_content = clean_html_content(webpage_content)
    
    # Create enhanced prompt
    prompt = create_enhanced_analysis_prompt(publication, clean_content, themes, types)
    
    try:
        # Call OpenAI API with higher token limit for enhanced analysis
        response = client.chat.completions.create(
            model="gpt-4o",  # Using the best chat model
            messages=[
                {"role": "system", "content": "Je bent een expert in Nederlands bestuursrecht en juridische publicaties. Analyseer publicaties zeer uitgebreid en geef gestructureerde, complete informatie terug voor alle gevraagde velden."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=2000  # Increased for enhanced analysis
        )
        
        # Parse response
        response_text = response.choices[0].message.content.strip()
        
        # Extract JSON from response
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            analysis_result = json.loads(json_match.group())
            
            # Update publication with all analyzed data
            updated_publication = publication.copy()
            
            # Basic fields
            updated_publication['thema'] = analysis_result.get('thema', publication.get('thema', ''))
            updated_publication['auteur'] = analysis_result.get('auteur', publication.get('auteur', ''))
            updated_publication['samenvatting'] = analysis_result.get('samenvatting', publication.get('samenvatting', ''))
            updated_publication['type'] = analysis_result.get('type', publication.get('type', ''))
            
            # Enhanced fields
            updated_publication['keywords'] = analysis_result.get('keywords', '')
            updated_publication['audience'] = analysis_result.get('audience', '')
            updated_publication['impact'] = analysis_result.get('impact', '')
            updated_publication['read_time'] = analysis_result.get('read_time', '')
            updated_publication['takeaways'] = analysis_result.get('takeaways', [])
            updated_publication['summary_one_liner'] = analysis_result.get('summary_one_liner', '')
            updated_publication['embargo_status'] = analysis_result.get('embargo_status', 'Geen embargo')
            updated_publication['subtype'] = analysis_result.get('subtype', '')
            updated_publication['language_level'] = analysis_result.get('language_level', '')
            updated_publication['expiry_or_validity'] = analysis_result.get('expiry_or_validity', '')
            updated_publication['relevance_score'] = analysis_result.get('relevance_score', 5)
            
            print(f"✓ Successfully analyzed (Enhanced): {publication.get('titel', 'Unknown')}")
            return updated_publication
        else:
            print(f"Could not parse JSON response for: {publication.get('titel', 'Unknown')}")
            return publication
            
    except Exception as e:
        print(f"Error analyzing publication {publication.get('titel', 'Unknown')}: {str(e)}")
        return publication

def test_enhanced_analysis():
    """Test the enhanced analysis on a single publication"""
    
    # Load publications
    try:
        with open('../../../../public/content/publicaties.json', 'r', encoding='utf-8') as f:
            publications = json.load(f)
        print(f"Loaded {len(publications)} publications")
    except FileNotFoundError:
        print("Error: publicaties.json not found")
        return
    
    # Test with the first publication
    test_publication = publications[0]
    
    print(f"\nTesting enhanced analysis with: {test_publication.get('titel', 'Unknown')}")
    print(f"URL: {test_publication.get('url', 'No URL')}")
    
    # Analyze the publication
    analyzed_pub = analyze_enhanced_publication(test_publication, OPENAI_API_KEY)
    
    # Show results
    print("\n" + "="*100)
    print("ENHANCED ANALYSIS RESULTS:")
    print("="*100)
    print(f"Titel: {analyzed_pub.get('titel', '')}")
    print(f"Datum: {analyzed_pub.get('datum', '')}")
    print(f"Bron: {analyzed_pub.get('bron', '')}")
    print(f"Type: {analyzed_pub.get('type', '')}")
    print(f"Subtype: {analyzed_pub.get('subtype', '')}")
    print(f"Thema: {analyzed_pub.get('thema', '')}")
    print(f"Auteur: {analyzed_pub.get('auteur', '')}")
    print(f"Keywords: {analyzed_pub.get('keywords', '')}")
    print(f"Audience: {analyzed_pub.get('audience', '')}")
    print(f"Impact: {analyzed_pub.get('impact', '')}")
    print(f"Read Time: {analyzed_pub.get('read_time', '')}")
    print(f"Language Level: {analyzed_pub.get('language_level', '')}")
    print(f"Expiry/Validity: {analyzed_pub.get('expiry_or_validity', '')}")
    print(f"Relevance Score: {analyzed_pub.get('relevance_score', '')}")
    print(f"Embargo Status: {analyzed_pub.get('embargo_status', '')}")
    print(f"\nOne-liner: {analyzed_pub.get('summary_one_liner', '')}")
    print(f"\nTakeaways:")
    for i, takeaway in enumerate(analyzed_pub.get('takeaways', []), 1):
        print(f"  {i}. {takeaway}")
    print(f"\nSamenvatting:")
    print(analyzed_pub.get('samenvatting', ''))
    print("="*100)
    
    # Save test result
    with open('enhanced_test_result.json', 'w', encoding='utf-8') as f:
        json.dump(analyzed_pub, f, ensure_ascii=False, indent=2)
    print("\n✓ Enhanced test result saved to enhanced_test_result.json")

if __name__ == "__main__":
    print("Enhanced OpenAI Publication Analysis Test")
    print("=" * 60)
    print("This will test the enhanced analysis with all additional attributes:")
    print("- Keywords, Audience, Impact, Read Time")
    print("- Takeaways, One-liner Summary, Source URL")
    print("- Subtype, Language Level, Expiry/Validity")
    print("- Relevance Score")
    print("\nEstimated cost per publication: $0.03-0.04")
    print("=" * 60)
    
    confirm = input("\nRun enhanced analysis test? (y/n): ").strip().lower()
    if confirm == 'y':
        test_enhanced_analysis()
    else:
        print("Test cancelled.")
