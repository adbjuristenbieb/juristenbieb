import json
import os
from enhanced_publication_analyzer import analyze_enhanced_publication
import time

# Import OpenAI API key from config
from config import OPENAI_API_KEY

def process_enhanced_publications():
    """Process all publications with enhanced analysis"""
    
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
    
    # Find publications that need enhanced analysis
    publications_to_analyze = []
    for pub in publications:
        # Check if any enhanced fields are missing
        needs_analysis = (
            not pub.get('keywords') or 
            not pub.get('audience') or 
            not pub.get('impact') or 
            not pub.get('takeaways') or 
            not pub.get('summary_one_liner') or
            not pub.get('subtype') or
            not pub.get('language_level') or
            not pub.get('expiry_or_validity') or
            not pub.get('relevance_score')
        )
        if needs_analysis:
            publications_to_analyze.append(pub)
    
    print(f"Found {len(publications_to_analyze)} publications that need enhanced analysis")
    
    if not publications_to_analyze:
        print("All publications already have complete enhanced data!")
        return
    
    # Show cost estimates
    print(f"\n📊 ENHANCED ANALYSIS COST ESTIMATE:")
    print(f"=" * 60)
    print(f"Publications to analyze: {len(publications_to_analyze)}")
    print(f"Cost per publication: $0.03-0.04")
    print(f"Estimated total cost: ${len(publications_to_analyze) * 0.035:.2f}")
    print(f"=" * 60)
    
    print(f"\n🚀 ENHANCED FEATURES INCLUDED:")
    print(f"✅ Keywords (3-8 kernwoorden voor SEO)")
    print(f"✅ Audience (doelgroep identificatie)")
    print(f"✅ Impact (beleidsrelevantie inschatting)")
    print(f"✅ Read Time (geschatte leestijd)")
    print(f"✅ Takeaways (3-5 belangrijkste punten)")
    print(f"✅ One-liner Summary (voor UI previews)")
    print(f"✅ Embargo Status (embargo detectie)")
    print(f"✅ Subtype (gedetailleerde categorisatie)")
    print(f"✅ Language Level (toegankelijkheid)")
    print(f"✅ Expiry/Validity (tijdgevoeligheid)")
    print(f"✅ Relevance Score (1-10 beleidsrelevantie)")
    
    confirm = input(f"\nDo you want to proceed with enhanced analysis? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Enhanced analysis cancelled.")
        return
    
    # Get batch settings
    start_index = input("Start from index (default 0): ").strip()
    start_index = int(start_index) if start_index.isdigit() else 0
    
    batch_size = input("Save progress every N publications (default 5): ").strip()
    batch_size = int(batch_size) if batch_size.isdigit() else 5
    
    max_to_process = input("Maximum publications to process (default: all): ").strip()
    if max_to_process.isdigit():
        publications_to_analyze = publications_to_analyze[:int(max_to_process)]
    
    print(f"\n🔄 STARTING ENHANCED ANALYSIS...")
    print(f"Processing {len(publications_to_analyze)} publications")
    print(f"Starting from index {start_index}")
    print(f"Saving progress every {batch_size} publications")
    print(f"Rate limit: 3 seconds between requests (for enhanced analysis)")
    
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
        
        # Analyze the publication with enhanced features
        analyzed_pub = analyze_enhanced_publication(pub_to_analyze, OPENAI_API_KEY)
        
        # Update the publication in the main list
        updated_publications[original_index] = analyzed_pub
        processed_count += 1
        
        # Show brief results
        print(f"✅ Thema: {analyzed_pub.get('thema', 'Not found')}")
        print(f"✅ Keywords: {analyzed_pub.get('keywords', 'Not found')}")
        print(f"✅ Audience: {analyzed_pub.get('audience', 'Not found')}")
        print(f"✅ Relevance Score: {analyzed_pub.get('relevance_score', 'Not found')}")
        print(f"✅ Read Time: {analyzed_pub.get('read_time', 'Not found')}")
        
        # Save progress periodically
        if processed_count % batch_size == 0:
            backup_filename = f'enhanced_publications_progress_{processed_count}.json'
            try:
                with open(backup_filename, 'w', encoding='utf-8') as f:
                    json.dump(updated_publications, f, ensure_ascii=False, indent=2)
                print(f"💾 Progress saved to {backup_filename}")
            except Exception as e:
                print(f"Error saving progress: {str(e)}")
        
        # Rate limiting - longer wait for enhanced analysis
        if i < len(publications_to_analyze) - 1:
            print("⏳ Waiting 3 seconds before next request...")
            time.sleep(3)
    
    # Save final results
    try:
        # Backup original file
        backup_original = 'enhanced_publicaties_original_backup.json'
        with open('../../../../public/content/publicaties.json', 'r', encoding='utf-8') as f:
            original_data = f.read()
        with open(backup_original, 'w', encoding='utf-8') as f:
            f.write(original_data)
        print(f"💾 Original file backed up to {backup_original}")
        
        # Save updated publications
        with open('../../../../public/content/publicaties.json', 'w', encoding='utf-8') as f:
            json.dump(updated_publications, f, ensure_ascii=False, indent=2)
        print(f"✅ Updated publicaties.json with {processed_count} enhanced publications")
        
        # Also save a copy in the current directory
        with open('enhanced_publicaties_final.json', 'w', encoding='utf-8') as f:
            json.dump(updated_publications, f, ensure_ascii=False, indent=2)
        print(f"💾 Copy saved to enhanced_publicaties_final.json")
        
        # Show completion summary
        print(f"\n🎉 ENHANCED ANALYSIS COMPLETE!")
        print(f"=" * 60)
        print(f"✅ Processed: {processed_count} publications")
        print(f"💰 Estimated cost: ${processed_count * 0.035:.2f}")
        print(f"📊 Enhanced fields added to each publication:")
        print(f"   - Keywords, Audience, Impact, Read Time")
        print(f"   - Takeaways, One-liner Summary, Embargo Status")
        print(f"   - Subtype, Language Level, Expiry/Validity")
        print(f"   - Relevance Score")
        print(f"=" * 60)
        
    except Exception as e:
        print(f"Error saving final results: {str(e)}")
        print("Your progress files are still available for manual recovery.")

def show_enhanced_analysis_stats():
    """Show statistics about publications that need enhanced analysis"""
    try:
        with open('../../../../public/content/publicaties.json', 'r', encoding='utf-8') as f:
            publications = json.load(f)
    except FileNotFoundError:
        print("Error: publicaties.json not found")
        return
    
    total = len(publications)
    
    # Check basic fields
    missing_thema = sum(1 for pub in publications if not pub.get('thema'))
    missing_auteur = sum(1 for pub in publications if not pub.get('auteur'))
    missing_samenvatting = sum(1 for pub in publications if not pub.get('samenvatting'))
    
    # Check enhanced fields
    missing_keywords = sum(1 for pub in publications if not pub.get('keywords'))
    missing_audience = sum(1 for pub in publications if not pub.get('audience'))
    missing_impact = sum(1 for pub in publications if not pub.get('impact'))
    missing_read_time = sum(1 for pub in publications if not pub.get('read_time'))
    missing_takeaways = sum(1 for pub in publications if not pub.get('takeaways'))
    missing_one_liner = sum(1 for pub in publications if not pub.get('summary_one_liner'))
    missing_subtype = sum(1 for pub in publications if not pub.get('subtype'))
    missing_language_level = sum(1 for pub in publications if not pub.get('language_level'))
    missing_expiry = sum(1 for pub in publications if not pub.get('expiry_or_validity'))
    missing_relevance_score = sum(1 for pub in publications if not pub.get('relevance_score'))
    
    # Count publications needing enhanced analysis
    missing_enhanced = sum(1 for pub in publications if (
        not pub.get('keywords') or 
        not pub.get('audience') or 
        not pub.get('impact') or 
        not pub.get('takeaways') or 
        not pub.get('summary_one_liner') or
        not pub.get('subtype') or
        not pub.get('language_level') or
        not pub.get('expiry_or_validity') or
        not pub.get('relevance_score')
    ))
    
    print(f"📊 ENHANCED PUBLICATION ANALYSIS STATISTICS:")
    print(f"=" * 70)
    print(f"Total publications: {total}")
    print(f"")
    print(f"🔍 BASIC FIELDS:")
    print(f"Missing thema: {missing_thema}")
    print(f"Missing auteur: {missing_auteur}")
    print(f"Missing samenvatting: {missing_samenvatting}")
    print(f"")
    print(f"🚀 ENHANCED FIELDS:")
    print(f"Missing keywords: {missing_keywords}")
    print(f"Missing audience: {missing_audience}")
    print(f"Missing impact: {missing_impact}")
    print(f"Missing read_time: {missing_read_time}")
    print(f"Missing takeaways: {missing_takeaways}")
    print(f"Missing summary_one_liner: {missing_one_liner}")
    print(f"Missing subtype: {missing_subtype}")
    print(f"Missing language_level: {missing_language_level}")
    print(f"Missing expiry_or_validity: {missing_expiry}")
    print(f"Missing relevance_score: {missing_relevance_score}")
    print(f"")
    print(f"📈 SUMMARY:")
    print(f"Publications needing enhanced analysis: {missing_enhanced}")
    print(f"Enhanced completion rate: {((total - missing_enhanced) / total * 100):.1f}%")
    print(f"Estimated cost for enhanced analysis: ${missing_enhanced * 0.035:.2f}")
    print(f"=" * 70)

if __name__ == "__main__":
    print("🚀 Enhanced OpenAI Publication Analysis - Batch Processor")
    print("=" * 80)
    
    choice = input("Choose action:\n1. Show enhanced analysis statistics\n2. Process publications with enhanced analysis\nEnter choice (1 or 2): ").strip()
    
    if choice == "1":
        show_enhanced_analysis_stats()
    elif choice == "2":
        process_enhanced_publications()
    else:
        print("Invalid choice. Showing statistics...")
        show_enhanced_analysis_stats()
