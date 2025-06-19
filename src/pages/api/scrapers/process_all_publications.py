import json
import os
from publication_analyzer_function import analyze_publication_from_config
import time


def process_all_publications():
    """Process all publications that need analysis"""
    
    # Load publications
    try:
        with open('../../../../public/content/publicaties.json', 'r', encoding='utf-8') as f:
            publications = json.load(f)
        print(f"Loaded {len(publications)} publications")
    except FileNotFoundError:
        print("Error: publicaties.json not found")
        return
    except json.JSONDecodeError as e:
        print(f"Error parsing publicaties.json: {str(e)}")
        return
    
    # Find publications that need analysis
    publications_to_analyze = []
    for pub in publications:
        if not pub.get('thema') or not pub.get('auteur') or not pub.get('samenvatting'):
            publications_to_analyze.append(pub)
    
    print(f"Found {len(publications_to_analyze)} publications that need analysis")
    
    if not publications_to_analyze:
        print("All publications already have complete data!")
        return
    
    # Ask user for confirmation and settings
    print(f"\nThis will analyze {len(publications_to_analyze)} publications using OpenAI API.")
    print("Each request costs approximately $0.01-0.03 depending on content length.")
    print(f"Estimated total cost: ${len(publications_to_analyze) * 0.02:.2f}")
    
    confirm = input("\nDo you want to proceed? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Analysis cancelled.")
        return
    
    # Get batch settings
    start_index = input("Start from index (default 0): ").strip()
    start_index = int(start_index) if start_index.isdigit() else 0
    
    batch_size = input("Save progress every N publications (default 10): ").strip()
    batch_size = int(batch_size) if batch_size.isdigit() else 10
    
    max_to_process = input("Maximum publications to process (default: all): ").strip()
    if max_to_process.isdigit():
        publications_to_analyze = publications_to_analyze[:int(max_to_process)]
    
    print(f"\nStarting analysis...")
    print(f"Processing {len(publications_to_analyze)} publications")
    print(f"Starting from index {start_index}")
    print(f"Saving progress every {batch_size} publications")
    
    # Create a copy of all publications for updating
    updated_publications = publications.copy()
    
    # Process publications
    processed_count = 0
    for i, pub_to_analyze in enumerate(publications_to_analyze[start_index:], start_index):
        print(f"\n--- Processing {i+1}/{len(publications_to_analyze)} ---")
        print(f"Title: {pub_to_analyze.get('titel', 'Unknown')}")
        
        # Find the index in the original publications list
        original_index = None
        for j, original_pub in enumerate(updated_publications):
            if (original_pub.get('titel') == pub_to_analyze.get('titel') and 
                original_pub.get('url') == pub_to_analyze.get('url')):
                original_index = j
                break
        
        if original_index is None:
            print("Warning: Could not find publication in original list")
            continue
        
        # Analyze the publication
        analyzed_pub = analyze_publication_from_config(pub_to_analyze)
        
        # Update the publication in the main list
        updated_publications[original_index] = analyzed_pub
        processed_count += 1
        
        # Show brief results
        print(f"✓ Thema: {analyzed_pub.get('thema', 'Not found')}")
        print(f"✓ Auteur: {analyzed_pub.get('auteur', 'Not found')}")
        print(f"✓ Type: {analyzed_pub.get('type', 'Not found')}")
        
        # Save progress periodically
        if processed_count % batch_size == 0:
            backup_filename = f'publicaties_progress_{processed_count}.json'
            try:
                with open(backup_filename, 'w', encoding='utf-8') as f:
                    json.dump(updated_publications, f, ensure_ascii=False, indent=2)
                print(f"✓ Progress saved to {backup_filename}")
            except Exception as e:
                print(f"Error saving progress: {str(e)}")
        
        # Rate limiting - wait between requests
        if i < len(publications_to_analyze) - 1:
            print("Waiting 2 seconds before next request...")
            time.sleep(2)
    
    # Save final results
    try:
        # Backup original file
        backup_original = 'publicaties_original_backup.json'
        with open('../../../../public/content/publicaties.json', 'r', encoding='utf-8') as f:
            original_data = f.read()
        with open(backup_original, 'w', encoding='utf-8') as f:
            f.write(original_data)
        print(f"✓ Original file backed up to {backup_original}")
        
        # Save updated publications
        with open('../../../../public/content/publicaties.json', 'w', encoding='utf-8') as f:
            json.dump(updated_publications, f, ensure_ascii=False, indent=2)
        print(f"✓ Updated publicaties.json with {processed_count} analyzed publications")
        
        # Also save a copy in the current directory
        with open('publicaties_final_analyzed.json', 'w', encoding='utf-8') as f:
            json.dump(updated_publications, f, ensure_ascii=False, indent=2)
        print(f"✓ Copy saved to publicaties_final_analyzed.json")
        
    except Exception as e:
        print(f"Error saving final results: {str(e)}")
        print("Your progress files are still available for manual recovery.")

def show_analysis_stats():
    """Show statistics about publications that need analysis"""
    try:
        with open('../../../../public/content/publicaties.json', 'r', encoding='utf-8') as f:
            publications = json.load(f)
    except FileNotFoundError:
        print("Error: publicaties.json not found")
        return
    
    total = len(publications)
    missing_thema = sum(1 for pub in publications if not pub.get('thema'))
    missing_auteur = sum(1 for pub in publications if not pub.get('auteur'))
    missing_samenvatting = sum(1 for pub in publications if not pub.get('samenvatting'))
    missing_any = sum(1 for pub in publications if not pub.get('thema') or not pub.get('auteur') or not pub.get('samenvatting'))
    
    print(f"Publication Analysis Statistics:")
    print(f"================================")
    print(f"Total publications: {total}")
    print(f"Missing thema: {missing_thema}")
    print(f"Missing auteur: {missing_auteur}")
    print(f"Missing samenvatting: {missing_samenvatting}")
    print(f"Missing any field: {missing_any}")
    print(f"Complete publications: {total - missing_any}")
    print(f"Completion rate: {((total - missing_any) / total * 100):.1f}%")

if __name__ == "__main__":
    print("OpenAI Publication Analysis - Batch Processor")
    print("=" * 60)
    
    choice = input("Choose action:\n1. Show analysis statistics\n2. Process all publications\nEnter choice (1 or 2): ").strip()
    
    if choice == "1":
        show_analysis_stats()
    elif choice == "2":
        process_all_publications()
    else:
        print("Invalid choice. Showing statistics...")
        show_analysis_stats()
