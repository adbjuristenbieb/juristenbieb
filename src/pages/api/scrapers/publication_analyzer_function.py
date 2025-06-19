import json
import os
import requests
from openai import OpenAI
import re
from typing import Dict, List, Optional

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
    
    # Limit content length for API efficiency
    return html_content[:8000] if len(html_content) > 8000 else html_content

def create_analysis_prompt(publication: Dict, webpage_content: str, themes: List[str], types: List[str]) -> str:
    """Create the prompt for OpenAI analysis"""
    themes_list = ", ".join(themes)
    types_list = ", ".join(types)
    
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

def analyze_single_publication(publication: Dict, api_key: str) -> Dict:
    """
    Analyze a single publication using OpenAI API
    
    Args:
        publication: Dictionary containing publication data
        api_key: OpenAI API key
        
    Returns:
        Updated publication dictionary with analyzed data
    """
    client = OpenAI(api_key=api_key)
    themes = load_themes()
    types = load_types()
    
    url = publication.get('url', '')
    if not url:
        print(f"No URL found for publication: {publication.get('titel', 'Unknown')}")
        return publication
    
    print(f"Analyzing: {publication.get('titel', 'Unknown')}")
    
    # Fetch webpage content
    webpage_content = fetch_webpage_content(url)
    if not webpage_content:
        print(f"Could not fetch content for: {url}")
        return publication
    
    # Clean HTML content
    clean_content = clean_html_content(webpage_content)
    
    # Create prompt
    prompt = create_analysis_prompt(publication, clean_content, themes, types)
    
    try:
        # Call OpenAI API
        response = client.chat.completions.create(
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

def analyze_new_publications(new_publications: List[Dict], api_key: str) -> List[Dict]:
    """
    Analyze a list of new publications
    
    Args:
        new_publications: List of publication dictionaries
        api_key: OpenAI API key
        
    Returns:
        List of analyzed publication dictionaries
    """
    analyzed_publications = []
    
    for i, publication in enumerate(new_publications):
        print(f"\nProcessing {i+1}/{len(new_publications)}")
        analyzed_pub = analyze_single_publication(publication, api_key)
        analyzed_publications.append(analyzed_pub)
        
        # Small delay between requests to respect rate limits
        if i < len(new_publications) - 1:
            import time
            time.sleep(1)
    
    return analyzed_publications

# Example usage function for automation
def process_new_article(article_data: Dict, openai_api_key: str = None) -> Dict:
    """
    Process a single new article - this is the main function to call for automation
    
    Args:
        article_data: Dictionary with at least 'titel', 'url', 'datum', 'bron'
        openai_api_key: OpenAI API key (optional, uses config if not provided)
        
    Returns:
        Complete article data with thema, auteur, samenvatting, type filled in
    """
    api_key = openai_api_key or OPENAI_API_KEY
    return analyze_single_publication(article_data, api_key)

# Convenience functions that use config automatically
def analyze_publication_from_config(publication: Dict) -> Dict:
    """
    Analyze a single publication using API key from config
    
    Args:
        publication: Dictionary containing publication data
        
    Returns:
        Updated publication dictionary with analyzed data
    """
    return analyze_single_publication(publication, OPENAI_API_KEY)

def analyze_publications_from_config(publications: List[Dict]) -> List[Dict]:
    """
    Analyze a list of publications using API key from config
    
    Args:
        publications: List of publication dictionaries
        
    Returns:
        List of analyzed publication dictionaries
    """
    return analyze_new_publications(publications, OPENAI_API_KEY)
