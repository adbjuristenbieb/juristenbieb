import json
import os
from publication_analyzer_function import analyze_publication_from_config

def test_single_publication():
    """Test the analysis on a single publication"""
    
    # Load publications
    try:
        with open('../../../../public/content/publicaties.json', 'r', encoding='utf-8') as f:
            publications = json.load(f)
        print(f"Loaded {len(publications)} publications")
    except FileNotFoundError:
        print("Error: publicaties.json not found")
        return
    
    # Test with the first publication that has empty fields
    test_publication = None
    for pub in publications:
        if not pub.get('thema') or not pub.get('auteur') or not pub.get('samenvatting'):
            test_publication = pub
            break
    
    if not test_publication:
        print("No publications found with empty fields to test")
        return
    
    print(f"\nTesting with publication: {test_publication.get('titel', 'Unknown')}")
    print(f"URL: {test_publication.get('url', 'No URL')}")
    
    # Analyze the publication
    analyzed_pub = analyze_publication_from_config(test_publication)
    
    # Show results
    print("\n" + "="*80)
    print("ANALYSIS RESULTS:")
    print("="*80)
    print(f"Titel: {analyzed_pub.get('titel', '')}")
    print(f"Datum: {analyzed_pub.get('datum', '')}")
    print(f"Bron: {analyzed_pub.get('bron', '')}")
    print(f"Type: {analyzed_pub.get('type', '')}")
    print(f"Thema: {analyzed_pub.get('thema', '')}")
    print(f"Auteur: {analyzed_pub.get('auteur', '')}")
    print(f"\nSamenvatting:")
    print(analyzed_pub.get('samenvatting', ''))
    print("="*80)
    
    # Save test result
    with open('test_analysis_result.json', 'w', encoding='utf-8') as f:
        json.dump(analyzed_pub, f, ensure_ascii=False, indent=2)
    print("\n✓ Test result saved to test_analysis_result.json")

def test_multiple_publications(count=3):
    """Test the analysis on multiple publications"""
    
    # Load publications
    try:
        with open('../../../../public/content/publicaties.json', 'r', encoding='utf-8') as f:
            publications = json.load(f)
        print(f"Loaded {len(publications)} publications")
    except FileNotFoundError:
        print("Error: publicaties.json not found")
        return
    
    # Find publications with empty fields
    test_publications = []
    for pub in publications:
        if not pub.get('thema') or not pub.get('auteur') or not pub.get('samenvatting'):
            test_publications.append(pub)
            if len(test_publications) >= count:
                break
    
    if not test_publications:
        print("No publications found with empty fields to test")
        return
    
    print(f"\nTesting with {len(test_publications)} publications")
    
    analyzed_publications = []
    for i, pub in enumerate(test_publications):
        print(f"\n--- Testing publication {i+1}/{len(test_publications)} ---")
        analyzed_pub = analyze_publication_from_config(pub)
        analyzed_publications.append(analyzed_pub)
        
        # Show brief results
        print(f"✓ Analyzed: {analyzed_pub.get('titel', 'Unknown')}")
        print(f"  Thema: {analyzed_pub.get('thema', 'Not found')}")
        print(f"  Auteur: {analyzed_pub.get('auteur', 'Not found')}")
        print(f"  Type: {analyzed_pub.get('type', 'Not found')}")
    
    # Save test results
    with open('test_multiple_analysis_results.json', 'w', encoding='utf-8') as f:
        json.dump(analyzed_publications, f, ensure_ascii=False, indent=2)
    print(f"\n✓ Test results saved to test_multiple_analysis_results.json")

if __name__ == "__main__":
    print("OpenAI Publication Analysis Test")
    print("="*50)
    
    choice = input("Choose test type:\n1. Single publication\n2. Multiple publications (3)\nEnter choice (1 or 2): ").strip()
    
    if choice == "1":
        test_single_publication()
    elif choice == "2":
        test_multiple_publications(3)
    else:
        print("Invalid choice. Running single publication test...")
        test_single_publication()
