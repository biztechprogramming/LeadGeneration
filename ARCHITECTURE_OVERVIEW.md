# Sales Intelligence AI-Driven Workflow - Comprehensive Architecture Overview

**Created:** 2025-10-24  
**Project:** Lead Generation - Sales Intelligence Research System  
**Status:** Current Implementation Analysis + Integration Points for Iterative AI Workflow

---

## Executive Summary

The Sales Intelligence Research System is a batch-oriented pipeline that transforms 122 company leads into comprehensive sales intelligence reports using AI analysis. The system currently operates in **linear mode** (company → AI → report), with two AI provider options (Claude Code or Cerebras).

This document provides a **comprehensive blueprint** for designing an **iterative AI-driven workflow** that leverages AI to guide data collection, identify missing information, and progressively enhance research quality through multi-stage analysis.

---

## Current Architecture Overview

### High-Level Data Flow

```
CSV Input (122 companies)
    ↓
Load Company Data [Title, Address, Phone, Website]
    ↓
For Each Company:
    ├─ Build Research Prompt
    ├─ Send to AI (Claude or Cerebras)
    ├─ Parse AI Output (3 delimited sections)
    └─ Save 3 Markdown Files
    ↓
Output: 366 Markdown Files + Summary JSON
```

### Current Files and Modules

#### Root Level Scripts (Primary Entry Points)

```
/mnt/c/dev/sales/Lead-Generation/
├── sales_intelligence_cerebras.py    (590 lines) - Fast batch processing via Cerebras API
├── sales_intelligence_research.py    (494 lines) - High-quality analysis via Claude CLI
├── test_cerebras.py                  (51 lines)  - Test harness for Cerebras version
├── test_sales_intelligence.py        (51 lines)  - Test harness for Claude version
├── google_maps_leads.csv             (122 records) - Input data source
└── requirements.txt                  - Dependencies
```

#### py_lead_generation Package (Data Collection Infrastructure)

```
py_lead_generation/
├── src/
│   ├── engines/
│   │   ├── base.py                   - BaseEngine class with common functionality
│   │   ├── abstract.py               - AbstractEngine interface definition
│   │   └── playwright_config.py      - Browser automation configuration
│   │
│   ├── google_maps/
│   │   └── engine.py                 - GoogleMapsEngine: web scraping + parsing
│   │
│   ├── yelp/
│   │   └── engine.py                 - YelpEngine: Yelp data extraction
│   │
│   ├── google_search/
│   │   └── [search engine integration]
│   │
│   └── misc/
│       ├── writer.py                 - CsvWriter: CSV file I/O utilities
│       └── utils.py                  - Geolocation utilities (Nominatim)
```

---

## Detailed Component Analysis

### 1. Input Data Structure

**Source File:** `google_maps_leads.csv` (122 companies)

**Schema:**
```csv
Title,Address,PhoneNumber,WebsiteURL
"Triangle Manufacturing Co., Inc.","25 Park Way, Upper Saddle River, NJ 07458",2018251212,trianglemfg.com
```

**Field Mapping:**
- **Title** → Company name (mandatory)
- **Address** → Physical location (used for context)
- **PhoneNumber** → Contact phone (10-digit format)
- **WebsiteURL** → Company website (may be N/A)

**Data Quality Notes:**
- 122 total records (1 header + 121 companies)
- ~85-90% have website URLs
- ~15% missing website data
- Phone numbers are numeric strings

---

### 2. AI Analysis Layer

#### Option A: Cerebras Intelligence Research (`sales_intelligence_cerebras.py`)

**API Details:**
- **Provider:** Cerebras AI
- **Model:** `llama-3.3-70b`
- **API Endpoint:** `https://api.cerebras.ai/v1/chat/completions`
- **Speed:** 10-30 seconds per company
- **Cost:** ~$0.10 per 1M tokens (~$1-3 for all 122)
- **Authentication:** Bearer token via `CEREBRAS_API_KEY` env var

**Key Methods:**
```python
class CerebrasSalesIntelligenceResearcher:
    def __init__(csv_path, output_dir)          # Initialize with CSV and output dir
    def load_companies() → List[Dict]           # Load from CSV
    def build_research_prompt(company) → str    # Generate AI prompt
    def analyze_with_cerebras(prompt) → str    # Call API and get response
    def parse_and_save_reports(...)             # Split by delimiters, save files
    def process_company(company, idx, total)    # Orchestrate single company
    def run_batch_analysis(limit, start_index)  # Batch processing loop
    def _save_summary_report(results)           # Save JSON summary
```

**Prompt Structure:**
- System role: "Sales Intelligence Analyst"
- Input data: Company name, website, address, phone
- Optional: Scraped website content (not implemented)
- Output format: 3 delimiter-separated sections

**Delimiter Tags (Used for Output Parsing):**
```
<FILE_1_CONTACT_ORG_CHART>     # Section 1: Contacts & Org Chart
<FILE_2_PAIN_POINTS_STRATEGY>  # Section 2: Pain Points & Strategy
<FILE_3_CALL_PREP_STARTERS>    # Section 3: Call Prep & Conversation Starters
```

#### Option B: Claude Code Intelligence Research (`sales_intelligence_research.py`)

**API Details:**
- **Provider:** Anthropic Claude (via CLI)
- **Model:** Claude Sonnet 4.5 (via `claude` command)
- **Speed:** 3-5 minutes per company
- **Cost:** Deducted from Claude Code subscription
- **Authentication:** OAuth token (automatic)

**Key Differences from Cerebras:**
- Uses subprocess to call `claude --print` CLI
- Same prompt structure and delimiter parsing
- Better output quality, slower processing
- No API key needed (uses existing authentication)

---

### 3. Report Generation Pipeline

#### File Output Structure

**Pattern:** `[SanitizedCompanyName]_[REPORT_TYPE].md`

**Sanitization Logic:**
```python
def sanitize_filename(company_name: str) -> str:
    sanitized = re.sub(r'[^\w\s-]', '', company_name)  # Remove special chars
    sanitized = re.sub(r'\s+', '_', sanitized)          # Spaces → underscores
    sanitized = re.sub(r'_+', '_', sanitized)           # Collapse underscores
    return sanitized.strip('_')
```

**Example Output:**
```
Triangle_Manufacturing_Co_Inc_CONTACTS.md
Triangle_Manufacturing_Co_Inc_PAIN_POINTS.md
Triangle_Manufacturing_Co_Inc_CALL_PREP.md
Rockleigh_Industries_Inc_CONTACTS.md
... (122 companies × 3 files = 366 files)
```

#### Report File Contents

**1. CONTACTS.md (Contact & Org Chart)**
```markdown
| Name | Title | Buying Role | Email Format | Source |
|------|-------|-------------|--------------|--------|
| [Real or inferred name] | [Title] | [Decision Maker/Influencer/User] | [email@company.com] | [URL] |

**Org Structure Notes:**
- Key Departments: ...
- Growth Signals: ...
```

**2. PAIN_POINTS.md (Strategic Analysis)**
```markdown
**Top 3-5 Inferred Pain Points:**
1. **[Problem]:** [Evidence/reasoning]
2. **[Problem]:** [Evidence/reasoning]

**Strategic Sales Thesis:**
- Primary Sales Angle: ...
- Competition Clues: ...
```

**3. CALL_PREP.md (Sales Conversation)**
```markdown
**Pre-Call Checklist:**
- Current News: ...
- Call Goal: ...

**Conversation Starters (Use these!):**
- High-Value Question (Needs Analysis): ...
- Bold Statement (Value Proposition): ...
- Closing Question: ...
```

#### Batch Summary Report

**File:** `_batch_summary.json` or `_batch_summary_cerebras.json`

```json
{
  "timestamp": "2025-10-24T...",
  "provider": "cerebras" | "claude",
  "model": "llama-3.3-70b" | "claude-4.5",
  "total_processed": 122,
  "successful": 118,
  "failed": 4,
  "results": [
    {
      "company": "Triangle Manufacturing",
      "website": "trianglemfg.com",
      "success": true,
      "files_created": ["/path/to/file1.md", ...],
      "error": null
    }
  ]
}
```

---

### 4. Data Collection Infrastructure (py_lead_generation)

#### Lead Generation Engines

**BaseEngine (Abstract Base)**
```python
class BaseEngine:
    async run()                                    # Orchestrate scraping
    def save_to_csv(filename=None)                 # Persist entries to CSV
    async _open_url_and_wait(url, sleep_duration_s)
    async _get_search_results_entries(urls)        # Fetch data from URLs
    def _parse_data_with_soup(html)               # Parse HTML with BeautifulSoup
```

**GoogleMapsEngine (Concrete Implementation)**
- **Purpose:** Extract business data from Google Maps search results
- **Method:** Playwright browser automation + BeautifulSoup parsing
- **Output Schema:** `['Title', 'Address', 'PhoneNumber', 'WebsiteURL']`

**Key Parameters:**
```python
SCROLL_TIME_DURATION_S = 200    # Max scroll time before scraping
SLEEP_PER_SCROLL_S = 5          # Wait between scroll actions (avoid detection)
BASE_URL = 'https://www.google.com/maps/search/{query}/@{coords},{zoom}z/...'
```

**HTML Selectors for Parsing:**
```python
{
    'title': '.DUwDvf.lfPIob',
    'address': '[data-item-id="address"]',
    'phone_number': '[data-item-id^="phone:"]',
    'website_url': '[data-item-id="authority"]'
}
```

**YelpEngine (Similar Pattern)**
- Purpose: Extract data from Yelp business listings
- Output: Same schema as GoogleMapsEngine

#### CSV I/O Utilities

**CsvWriter Class**
```python
class CsvWriter:
    def __init__(filename: str, fieldnames: list[str])  # Initialize with schema
    def append(data: list[dict])                          # Append rows to CSV
```

**Features:**
- Creates file with headers if doesn't exist
- Appends new data to existing files
- Handles UTF-8 encoding

#### Geolocation Utilities

**Location Helper (geopy)**
```python
def get_coords_by_location(location: str) -> tuple[str]:
    # Converts "New York" → ("40.7128", "-74.0060")
    # Uses Nominatim geocoder (OpenStreetMap data)
```

---

## Current Processing Flow (Linear Model)

### Single Company Processing

```
Input: Company Dict {Title, Address, Phone, Website}
    ↓
1. Build Prompt
   - Company metadata
   - Website URL (if available)
   - Optional: scraped website content
   - AI instructions + delimiter guidance
    ↓
2. Send to AI
   - Cerebras API OR Claude CLI
   - Prompt + max_tokens + temperature settings
    ↓
3. Receive Response
   - Raw AI output with delimiter-separated sections
    ↓
4. Parse Output
   - Extract section 1 (delimiters: TAG1 to TAG2)
   - Extract section 2 (delimiters: TAG2 to TAG3)
   - Extract section 3 (delimiters: TAG3 to EOF)
    ↓
5. Save Reports
   - [Company]_CONTACTS.md
   - [Company]_PAIN_POINTS.md
   - [Company]_CALL_PREP.md
    ↓
Output: 3 Markdown Files + Success Status
```

### Batch Processing Loop

```python
for idx, company in enumerate(companies):
    result = process_company(company, idx, total)
    results.append(result)
    sleep(1 or 2 seconds)  # Rate limiting

# After all companies:
save_summary_report(results)  # Save JSON summary
print_statistics()            # Print success/failure counts
```

**Rate Limiting:**
- Cerebras version: 1 second delay between companies
- Claude Code version: 2 second delay between companies
- Reason: Avoid API rate limits and maintain server health

---

## Key Integration Points for Iterative AI Workflow

### 1. Prompt Building & Analysis Loop

**Current State:** Static prompt, no iteration  
**Integration Point:** Make prompt dynamic based on previous results

```python
# ENHANCEMENT: Multi-stage analysis with feedback loop
def iterative_research_loop(company: Dict) -> IterativeResult:
    """Stage 1: Initial Analysis"""
    stage1_result = ai_analyze(company, "initial_analysis")
    missing_data = extract_missing_fields(stage1_result)
    
    """Stage 2: Identify Missing Data"""
    next_steps = ai_identify_missing(missing_data, company)
    
    """Stage 3: Collect Additional Data"""
    additional_data = collect_data_from_sources(next_steps)
    
    """Stage 4: Enrich & Refine"""
    final_result = ai_refine(stage1_result, additional_data)
    
    return IterativeResult(
        initial=stage1_result,
        missing_fields=missing_data,
        additional_data=additional_data,
        final=final_result
    )
```

### 2. Website Scraping (Currently Not Implemented)

**Current State:** Placeholder returns `None`  
**Location:** `sales_intelligence_cerebras.py:94-114`, `sales_intelligence_research.py:184-199`

```python
def scrape_website(self, url: str) -> Optional[str]:
    """TODO: Implement actual Firecrawl integration"""
    if not url or url == 'N/A':
        return None
    try:
        # Note: This requires Firecrawl MCP to be available
        # For now, return None and let AI know website wasn't accessible
        return None
    except Exception as e:
        print(f"    Warning: Could not scrape {url}: {e}")
        return None
```

**Integration Point:** Implement Firecrawl/Puppeteer website scraping

```python
async def scrape_website_content(url: str) -> Optional[str]:
    """Scrape website and return markdown content"""
    # Option 1: Use Firecrawl MCP (if available)
    # Option 2: Use Puppeteer/Playwright directly
    # Option 3: Use requests + BeautifulSoup for simple HTML
    pass
```

### 3. Data Collection from Multiple Sources

**Current Sources:** Google Maps only  
**Enhancement:** Add multi-source data collection

```python
async def collect_company_data(company: Dict) -> EnrichedCompanyData:
    """Collect data from multiple sources"""
    # Source 1: Company Website (Firecrawl/Puppeteer)
    website_data = await scrape_website(company['WebsiteURL'])
    
    # Source 2: Google Search Results
    google_results = await search_google(company['Title'])
    
    # Source 3: LinkedIn Company Page (if available)
    linkedin_data = await scrape_linkedin(company['Title'])
    
    # Source 4: News/Press Releases
    news_data = await search_news(company['Title'])
    
    # Source 5: Business Registrations (Secretary of State, D&B, etc.)
    business_records = await fetch_business_records(company)
    
    return EnrichedCompanyData(
        website=website_data,
        search=google_results,
        linkedin=linkedin_data,
        news=news_data,
        records=business_records
    )
```

### 4. Missing Function Logging & Tracking

**Integration Point:** Create a logging system for AI recommendations

```python
class MissingFunctionsLogger:
    """Track functions AI identifies as missing"""
    
    def __init__(self, output_file: str):
        self.output_file = output_file
        self.missing_functions = []
    
    def log_missing_function(self, company: str, function_name: str, reason: str):
        """Log a function that AI recommends implementing"""
        self.missing_functions.append({
            'company': company,
            'function': function_name,
            'reason': reason,
            'timestamp': datetime.now()
        })
    
    def save_report(self):
        """Save missing functions report"""
        with open(self.output_file, 'w') as f:
            json.dump(self.missing_functions, f, indent=2)
```

### 5. Image Handling & People Detection

**Integration Point:** Add support for scraping and organizing profile images

```python
class ImageManager:
    """Manage company and people images"""
    
    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    async def download_image(self, url: str, company_name: str, person_name: str):
        """Download and save image with metadata"""
        # Create directory: images/[company]/
        # Save as: [person_name]_[timestamp].jpg
        pass
    
    async def detect_people_in_images(self, image_path: str):
        """Use AI to detect and identify people in images"""
        # Option 1: Use Claude's vision API
        # Option 2: Use Google Vision API
        # Option 3: Use local ML model (dlib, face_recognition)
        pass
    
    def tag_image(self, image_path: str, person_name: str, role: str):
        """Add metadata tags to images"""
        # Store metadata in YAML/JSON file alongside image
        pass
```

### 6. Iterative Data Enrichment

**Integration Point:** Progressive enhancement through multiple AI calls

```python
class IterativeEnricher:
    """Progressively enrich company data through multiple AI iterations"""
    
    def __init__(self, ai_provider):
        self.ai = ai_provider
        self.iteration_history = []
    
    async def enrich_company(self, company: Dict, max_iterations: int = 3):
        """
        Stage 1: Initial Analysis
        Stage 2: Identify Gaps
        Stage 3: Collect Missing Data
        Stage 4: Refine Analysis
        Stage 5: Validate Quality
        """
        
        current_data = company.copy()
        
        for iteration in range(max_iterations):
            # Analyze current data
            analysis = await self.ai.analyze(current_data)
            
            # Identify what's missing
            gaps = self.identify_gaps(analysis)
            
            if not gaps or iteration == max_iterations - 1:
                break
            
            # Collect missing data
            new_data = await self.collect_missing_data(gaps)
            current_data.update(new_data)
            
            # Log iteration
            self.iteration_history.append({
                'iteration': iteration,
                'gaps_found': gaps,
                'data_collected': new_data
            })
        
        return current_data, self.iteration_history
```

### 7. Output Tagging & Organization

**Integration Point:** Add metadata tagging to reports

```python
class ReportManager:
    """Manage report generation with metadata and tagging"""
    
    async def generate_report(self, company: Dict, analysis_data: Dict):
        """Generate reports with additional metadata"""
        
        report_metadata = {
            'company_name': company['Title'],
            'website': company['WebsiteURL'],
            'processed_at': datetime.now(),
            'confidence_scores': {
                'contacts': 0.85,
                'pain_points': 0.75,
                'call_prep': 0.90
            },
            'data_sources_used': [
                'website_scrape',
                'google_search',
                'linkedin'
            ],
            'missing_data': [],
            'ai_iterations': 2
        }
        
        # Save metadata alongside reports
        await self.save_report_metadata(company['Title'], report_metadata)
```

---

## Data Flow: Proposed Iterative Architecture

```
CSV Input (122 companies)
    ↓
For Each Company:
    │
    ├─ ITERATION 1: INITIAL ANALYSIS
    │  ├─ Build research prompt
    │  ├─ Call AI (Cerebras/Claude)
    │  ├─ Parse output
    │  └─ Extract gaps
    │
    ├─ ITERATION 2: IDENTIFY MISSING DATA
    │  ├─ AI recommends data sources
    │  ├─ Log missing functions
    │  └─ Create data collection tasks
    │
    ├─ ITERATION 3: COLLECT DATA
    │  ├─ Scrape company website
    │  ├─ Search Google
    │  ├─ Check LinkedIn
    │  ├─ Find press releases/news
    │  ├─ Download images
    │  └─ Tag/organize results
    │
    ├─ ITERATION 4: ENRICH & REFINE
    │  ├─ Send collected data to AI
    │  ├─ AI refines analysis
    │  ├─ Detects people in images
    │  └─ Enhances contact info
    │
    ├─ ITERATION 5: VALIDATE & FINALIZE
    │  ├─ AI validates data quality
    │  ├─ Check confidence scores
    │  ├─ Save final reports
    │  └─ Generate metadata
    │
    └─ OUTPUT:
       ├─ [Company]_CONTACTS.md (enriched)
       ├─ [Company]_PAIN_POINTS.md (enriched)
       ├─ [Company]_CALL_PREP.md (enriched)
       ├─ [Company]_METADATA.json (new)
       ├─ [Company]_IMAGES/ (new)
       └─ iterations_log.json (new)
    
Final Summary:
    ├─ _batch_summary.json (enhanced with iterations)
    ├─ _missing_functions_report.json (new)
    └─ _data_quality_report.json (new)
```

---

## Key Files for Integration Points

### Core AI Analysis Files

| File | Purpose | Key Methods | Integration Point |
|------|---------|-------------|-------------------|
| `sales_intelligence_cerebras.py` | Cerebras API integration | `analyze_with_cerebras()` | Add multi-stage analysis loop |
| `sales_intelligence_research.py` | Claude CLI integration | `analyze_with_ai()` | Add iteration tracking |
| `build_research_prompt()` | Prompt generation | Both | Make dynamic based on iteration |
| `parse_and_save_reports()` | Output parsing | Both | Add metadata tagging |

### Data Collection Files

| File | Purpose | Key Methods | Enhancement Needed |
|------|---------|-------------|-------------------|
| `py_lead_generation/src/engines/base.py` | Browser automation | `_parse_data_with_soup()` | Add image scraping |
| `py_lead_generation/src/google_maps/engine.py` | Google Maps scraping | `_get_search_results_urls()` | Extend to other sources |
| `py_lead_generation/src/misc/writer.py` | CSV I/O | `append()` | Add metadata columns |
| `scrape_website()` | Website content | Currently placeholder | **Implement Firecrawl/Puppeteer** |

### Configuration & Utilities

| File | Purpose | Enhancement |
|------|---------|-------------|
| `requirements.txt` | Dependencies | Add: `aiohttp`, `redis`, `pillow`, `face-recognition` |
| `test_*.py` | Test scripts | Add iterative workflow tests |

---

## Missing/TODO Functions (Identified)

### High Priority

1. **Website Content Scraping** (`scrape_website()`)
   - Currently returns `None`
   - Needs: Firecrawl MCP or Puppeteer integration
   - Impact: ~85% of companies have websites

2. **Multi-Source Data Collection**
   - Google Search results
   - LinkedIn company pages
   - News/press releases
   - Business registration records

3. **Image Download & Management**
   - Download images from company websites
   - Download team/leadership photos
   - Organize by company/person

4. **AI-Guided Iteration System**
   - AI recommends what data is missing
   - Programmatic data collection tasks
   - Quality scoring

### Medium Priority

5. **Image Analysis & People Detection**
   - Detect faces in images
   - Identify leadership photos
   - Extract names/titles from context

6. **Contact Information Enhancement**
   - Email format detection
   - Phone number verification
   - LinkedIn profile linking

7. **Metadata & Tagging System**
   - Confidence scores per field
   - Data source attribution
   - Iteration tracking

### Low Priority

8. **Performance Optimization**
   - Parallel processing (async)
   - Caching mechanisms
   - Database backend instead of files

9. **CRM Integration**
   - Salesforce export
   - HubSpot integration
   - CSV reformatting

---

## Technology Stack & Dependencies

### Current Stack
- **Language:** Python 3.12
- **Web Scraping:** Playwright (async browser automation), BeautifulSoup4 (HTML parsing)
- **APIs:** Cerebras (inference), Claude CLI (AI), Geopy (geocoding)
- **Data:** CSV files, JSON
- **File I/O:** pathlib, csv, json modules

### Recommended Additions
- **Async Framework:** `aiohttp` (HTTP requests), `asyncio` (async task management)
- **Image Processing:** `pillow` (image manipulation), `face-recognition` (face detection)
- **Database:** `redis` or `sqlite3` (caching, state management)
- **Vision API:** Claude Vision, Google Vision, or local model
- **Web Scraping:** Firecrawl (premium), `httpx` (HTTP client)
- **Data Validation:** `pydantic` (type validation)
- **Testing:** `pytest`, `pytest-asyncio`

---

## Current Output Examples

### From `test_reports_cerebras/`

**Triangle_Manufacturing_Co_Inc_CONTACTS.md**
```markdown
| Name | Title | Buying Role | Email Format | Source |
| :--- | :--- | :--- | :--- | :--- |
| John Smith | CEO | Decision Maker | jsmith@trianglemfg.com | Company Website |
| Sarah Johnson | VP Operations | Decision Maker | sjohnson@trianglemfg.com | LinkedIn |
```

**Triangle_Manufacturing_Co_Inc_PAIN_POINTS.md**
```markdown
1. **Production Efficiency**: Manufacturing processes appear outdated based on career page job descriptions
2. **Supply Chain Visibility**: Multiple postings for supply chain management roles suggest growth challenges
3. **Quality Control**: Job postings emphasize quality assurance roles indicating scaling needs
```

**Triangle_Manufacturing_Co_Inc_CALL_PREP.md**
```markdown
**Conversation Starters:**
- "I noticed you've been actively hiring for operations roles. What's driving that expansion?"
- "Companies in precision manufacturing typically face supply chain bottlenecks. Is that something your team is working on?"
```

---

## Performance Metrics

### Processing Speed
- **Cerebras:** 10-30 seconds per company (~20 minutes for all 122)
- **Claude Code:** 3-5 minutes per company (~6-10 hours for all 122)
- **Parallelization:** Could reduce to ~2-3 minutes for all 122 with async (5-10x speedup)

### Quality Metrics
- **Current Output:** 3 reports × 122 companies = 366 files
- **Data Completeness:** Depends on website availability (85-90% have websites)
- **Accuracy:** Limited to publicly available information

### Cost Metrics
- **Cerebras:** ~$1-3 for all 122 companies (pay-as-you-go)
- **Claude Code:** Part of subscription (no additional cost)
- **Enhanced Workflow:** Additional costs for Firecrawl, image APIs, etc.

---

## Architecture Strengths

1. **Modular Design:** Clear separation between data loading, AI analysis, and output generation
2. **Flexible AI Backend:** Easy switch between Cerebras and Claude
3. **Batch Processing:** Handles large volumes efficiently
4. **Error Tracking:** Summary reports capture success/failure rates
5. **Rate Limiting:** Built-in delays prevent API throttling
6. **Existing Data Infrastructure:** py_lead_generation provides web scraping foundation

---

## Architecture Weaknesses (Addressed by Iterative Design)

1. **Single-Pass Analysis:** No refinement or data enrichment
2. **Limited Data Sources:** Only uses company name/website URL
3. **No Image Support:** Doesn't collect visual assets
4. **No Iteration:** Can't identify and fix missing data
5. **Static Prompts:** Same prompt for all companies
6. **No Confidence Scoring:** Treats all AI output as equal quality
7. **No State Management:** Can't resume/continue analysis
8. **Minimal Validation:** Relies entirely on AI quality

---

## Next Steps for Implementation

### Phase 1: Foundation (Week 1-2)
- [ ] Implement website scraping (`scrape_website()`)
- [ ] Add iteration history logging
- [ ] Create missing functions tracker
- [ ] Add metadata to reports

### Phase 2: Data Collection (Week 3-4)
- [ ] Add Google Search integration
- [ ] Add LinkedIn scraping (respecting ToS)
- [ ] Implement image downloading
- [ ] Add news/press release search

### Phase 3: AI Iteration (Week 5-6)
- [ ] Design iterative analysis loop
- [ ] Add AI gap identification
- [ ] Implement dynamic prompting
- [ ] Add confidence scoring

### Phase 4: Enhancement (Week 7-8)
- [ ] Image analysis & face detection
- [ ] Contact information enrichment
- [ ] Parallel processing (async)
- [ ] Database backend

### Phase 5: Polish (Week 9-10)
- [ ] CRM integration
- [ ] Advanced reporting
- [ ] Performance optimization
- [ ] Testing & validation

---

## References & Documentation

**Current Documentation:**
- `SALES_INTELLIGENCE_README.md` - User guide for current system
- `CEREBRAS_VS_CLAUDE.md` - Comparison of AI providers
- `QUICKSTART.md` - Quick setup instructions
- `CEREBRAS_SETUP.md` - Cerebras API setup

**Code Architecture:**
- `sales_intelligence_cerebras.py` - Cerebras implementation (590 lines)
- `sales_intelligence_research.py` - Claude implementation (494 lines)
- `py_lead_generation/src/` - Data collection infrastructure

**Input Data:**
- `google_maps_leads.csv` - 122 companies with basic info

---

## Conclusion

The Sales Intelligence Research System provides a solid foundation for automated sales intelligence generation. The proposed iterative AI-driven workflow enhances this by:

1. **Using AI to guide data collection** - AI identifies what's missing
2. **Progressively enriching data** - Multiple iteration stages
3. **Collecting from multiple sources** - Website, LinkedIn, news, images
4. **Managing and tagging images** - Visual asset organization
5. **Tracking quality metrics** - Confidence scores and validation
6. **Enabling continuous improvement** - Logging and learning from gaps

This document provides the **complete architectural blueprint** for implementing this enhanced system while building on the existing infrastructure.

