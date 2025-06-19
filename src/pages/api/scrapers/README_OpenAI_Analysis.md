# OpenAI Publication Analysis System

This system uses OpenAI's GPT-4o model to automatically analyze publications and fill in missing attributes: `thema`, `auteur`, `samenvatting`, and `type`.

## Files Overview

- `publication_analyzer_function.py` - Core analysis functions (reusable for automation)
- `analyze_publications_openai.py` - Full-featured batch analysis script with interactive settings
- `test_analysis.py` - Test script to analyze single or multiple publications
- `process_all_publications.py` - Comprehensive batch processor with statistics and progress saving
- `requirements.txt` - Python dependencies

## Setup

1. **Create virtual environment:**
   ```bash
   cd src/pages/api/scrapers
   python3 -m venv venv
   ```

2. **Install dependencies:**
   ```bash
   ./venv/bin/pip install -r requirements.txt
   ```

3. **Set OpenAI API key:**
   Copy the config template and add your API key:
   ```bash
   cp config.example.py config.py
   # Edit config.py and add your actual OpenAI API key
   ```

## Current Statistics

- **Total publications:** 2,213
- **Missing thema:** 2,139
- **Missing auteur:** 481
- **Missing samenvatting:** 2,203
- **Missing any field:** 2,213 (100% need analysis)
- **Estimated cost:** ~$44.26 (at $0.02 per publication)

## Usage

### 1. Test Analysis (Recommended First Step)

Test the system with a single publication:
```bash
cd src/pages/api/scrapers
echo "1" | ./venv/bin/python test_analysis.py
```

Test with multiple publications:
```bash
echo "2" | ./venv/bin/python test_analysis.py
```

### 2. View Statistics

Check current completion status:
```bash
echo "1" | ./venv/bin/python process_all_publications.py
```

### 3. Process All Publications

Run the full batch analysis:
```bash
echo "2" | ./venv/bin/python process_all_publications.py
```

The script will:
- Show cost estimates
- Ask for confirmation
- Allow you to set batch size and starting index
- Save progress every N publications
- Create backups of original data
- Update the main publicaties.json file

### 4. For Automation (New Articles)

Use the `process_new_article()` function from `publication_analyzer_function.py`:

```python
from publication_analyzer_function import process_new_article

# Example new article
new_article = {
    "titel": "New Publication Title",
    "url": "https://example.com/publication",
    "datum": "2024-01-15",
    "bron": "Source Name",
    "type": "Handreiking"
}

# Analyze it
analyzed_article = process_new_article(new_article, OPENAI_API_KEY)
print(analyzed_article)
```

## Analysis Process

For each publication, the system:

1. **Fetches webpage content** from the publication URL
2. **Cleans HTML** to extract readable text
3. **Sends to OpenAI** with structured prompt including:
   - Available themes from `themes.json`
   - Available types from `types.json`
   - Instructions for Dutch legal content analysis
4. **Parses response** and extracts structured data
5. **Updates publication** with analyzed attributes

## Output Fields

- **thema**: Selected from predefined themes (e.g., "Handhaving", "Omgevingsrecht")
- **auteur**: Main author name (single person/organization)
- **samenvatting**: Comprehensive summary (5-67 sentences)
- **type**: Publication type from predefined types ("Blog", "Handreiking")

## Safety Features

- **Progress saving**: Automatic backups every N publications
- **Original backup**: Creates backup before modifying main file
- **Error handling**: Continues processing if individual publications fail
- **Rate limiting**: 2-second delays between API calls
- **Cost estimation**: Shows estimated costs before processing

## Batch Processing Options

- **Start index**: Resume from specific publication
- **Batch size**: How often to save progress (default: 10)
- **Maximum count**: Limit number of publications to process
- **Interactive confirmation**: Requires user approval before processing

## File Locations

The scripts expect these file paths (relative to the scrapers directory):
- `../../../../public/content/publicaties.json` - Main publications file
- `../../../../public/content/themes.json` - Available themes
- `../../../../public/content/types.json` - Available types

## Error Recovery

If processing is interrupted:
1. Check for progress files: `publicaties_progress_N.json`
2. Use the start index option to resume from where you left off
3. Original data is always backed up as `publicaties_original_backup.json`

## Cost Management

- Each publication costs approximately $0.01-0.03
- Total estimated cost for all 2,213 publications: ~$44.26
- You can process in smaller batches to manage costs
- Set maximum count to limit spending per session

## Quality Assurance

The system:
- Only uses predefined themes and types
- Validates JSON responses from OpenAI
- Provides detailed logging of each analysis
- Saves individual results for review
- Maintains original data structure

## Integration with Existing System

The analyzed data integrates seamlessly with your existing publication system:
- Maintains all existing fields
- Adds missing `thema`, `auteur`, `samenvatting` data
- Compatible with current filtering and search functionality
- No changes needed to frontend code
