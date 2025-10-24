# Integration Points for Iterative AI-Driven Workflow

**Quick Reference Guide** for implementing the iterative AI research system.

---

## 1. MULTI-STAGE ANALYSIS LOOP

### Current Implementation (Linear)
```
Company Data → Single AI Call → Parse Output → Save Reports
```

### Proposed Enhancement (Iterative)
```
Company Data
    ↓
Stage 1: Initial Analysis
    → AI generates contacts, pain points, call prep
    → Extract identified gaps
    ↓
Stage 2: Gap Identification
    → AI recommends missing data sources
    → Log missing functions/APIs
    ↓
Stage 3: Data Collection
    → Execute AI-recommended data collection
    → Scrape websites, search LinkedIn, etc.
    ↓
Stage 4: Data Enrichment
    → Send collected data back to AI
    → AI refines previous analysis
    ↓
Stage 5: Validation & Quality Scoring
    → AI validates output quality
    → Confidence scores per field
    → Flag low-confidence items for manual review
    ↓
Final Reports + Metadata + Iteration History
```

### Files to Modify
- **`sales_intelligence_cerebras.py`**: Add iteration loop to `process_company()` method
- **`sales_intelligence_research.py`**: Add iteration loop to `process_company()` method

### New Classes Needed
```python
class IterativeAnalyzer:
    async def execute_iteration(self, company, stage_number, previous_result)
    
class GapIdentifier:
    def extract_gaps(self, ai_response) -> List[MissingField]
    
class IterationLogger:
    def log_iteration(self, company, stage, result, gaps)
```

---

## 2. WEBSITE SCRAPING (PRIORITY 1)

### Current Code Location
- **`sales_intelligence_cerebras.py:94-114`** - `scrape_website()` method (placeholder)
- **`sales_intelligence_research.py:184-199`** - `scrape_website()` method (placeholder)

### Current Implementation
```python
def scrape_website(self, url: str) -> Optional[str]:
    """TODO: Implement actual Firecrawl integration"""
    if not url or url == 'N/A':
        return None
    try:
        # Note: This requires Firecrawl MCP to be available
        return None  # ← Returns None instead of content!
    except Exception as e:
        print(f"Warning: Could not scrape {url}: {e}")
        return None
```

### Enhancement Options

**Option A: Firecrawl MCP** (Recommended for quality)
```python
async def scrape_website(self, url: str) -> Optional[str]:
    """Use Firecrawl MCP for high-quality web scraping"""
    try:
        # Call firecrawl.scrapeWebsite(url) via MCP
        # Return markdown content
        pass
    except Exception as e:
        logger.warning(f"Firecrawl failed for {url}: {e}")
        return None
```

**Option B: Playwright Direct** (Built-in, no dependencies)
```python
async def scrape_website(self, url: str) -> Optional[str]:
    """Use existing Playwright browser automation"""
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.goto(url)
            content = await page.content()  # Get raw HTML
            # Convert to markdown using html2text
            markdown = await html_to_markdown(content)
            return markdown
    except Exception as e:
        logger.warning(f"Scraping failed for {url}: {e}")
        return None
```

**Option C: Simple HTTP + BeautifulSoup** (Fast, basic)
```python
async def scrape_website(self, url: str) -> Optional[str]:
    """Simple HTTP-based scraping for basic content"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as resp:
                html = await resp.text()
                soup = BeautifulSoup(html, 'html.parser')
                # Extract text content
                text = soup.get_text()
                return text
    except Exception as e:
        logger.warning(f"HTTP scraping failed for {url}: {e}")
        return None
```

### Integration Steps
1. Choose scraping method (recommend Option A or B)
2. Implement `scrape_website()` method
3. Call in `process_company()` before building prompt
4. Pass content to `build_research_prompt()` as optional parameter
5. Add website content to prompt for AI analysis

### Expected Impact
- Currently ~85% of companies have websites with no content scraped
- Website content will dramatically improve AI analysis quality
- Enable identification of actual (not inferred) contacts and pain points

---

## 3. MISSING FUNCTIONS TRACKING

### Create New Class
```python
class MissingFunctionsLogger:
    """Track functions AI identifies as missing"""
    
    def __init__(self, output_file: str = "missing_functions_report.json"):
        self.output_file = output_file
        self.missing_functions = {}  # {company: [functions]}
        self.recommendations = {}    # {function: [reasons]}
    
    def parse_ai_recommendations(self, ai_response: str, company_name: str):
        """
        Parse AI output to identify missing data/functions.
        
        Look for patterns like:
        - "No contact data available"
        - "Unable to access website"
        - "Would need LinkedIn data"
        - "Missing information on"
        """
        pass
    
    def log_function(self, company: str, function: str, reason: str):
        """Log a missing function that AI recommends"""
        if company not in self.missing_functions:
            self.missing_functions[company] = []
        self.missing_functions[company].append({
            'function': function,
            'reason': reason,
            'timestamp': datetime.now()
        })
        
        # Aggregate across companies
        if function not in self.recommendations:
            self.recommendations[function] = []
        self.recommendations[function].append(company)
    
    def generate_priority_report(self):
        """Identify most commonly missing functions"""
        return sorted(
            self.recommendations.items(),
            key=lambda x: len(x[1]),
            reverse=True
        )
    
    def save_report(self):
        """Save complete report"""
        report = {
            'timestamp': datetime.now(),
            'total_companies': len(self.missing_functions),
            'by_company': self.missing_functions,
            'by_function': {f: len(c) for f, c in self.recommendations.items()},
            'priority': self.generate_priority_report()
        }
        with open(self.output_file, 'w') as f:
            json.dump(report, f, indent=2)
```

### Integration Steps
1. Create `missing_functions_logger.py`
2. Instantiate logger in `__init__()` of AI researcher
3. Call `parse_ai_recommendations()` after each AI response
4. Save report in `_save_summary_report()`
5. Output file: `_missing_functions_report.json`

### Expected Output
```json
{
  "timestamp": "2025-10-24T...",
  "total_companies": 122,
  "priority": [
    ["scrape_website", 122],
    ["linkedin_scraper", 110],
    ["news_aggregator", 95],
    ["image_downloader", 87],
    ["email_finder", 75]
  ],
  "by_company": {
    "Triangle Manufacturing": [
      {"function": "linkedin_scraper", "reason": "No LinkedIn profile found"},
      {"function": "image_downloader", "reason": "Need team photos"}
    ]
  }
}
```

---

## 4. MULTI-SOURCE DATA COLLECTION

### Create New Module: `data_collectors.py`

```python
class DataCollector:
    """Base class for data collection sources"""
    
    async def collect(self, company: Dict) -> Dict:
        """Collect data from this source"""
        raise NotImplementedError

class WebsiteScraper(DataCollector):
    """Already partially implemented - enhance with scrape_website()"""
    async def collect(self, company: Dict) -> Dict:
        content = await self.scrape_website(company['WebsiteURL'])
        return {'website_content': content}

class LinkedInCollector(DataCollector):
    """Scrape LinkedIn company page"""
    async def collect(self, company: Dict) -> Dict:
        # Use company name to find LinkedIn profile
        # Return: employees, founding_date, description, etc.
        pass

class NewsCollector(DataCollector):
    """Search for recent news about company"""
    async def collect(self, company: Dict) -> Dict:
        # Use Google News API or similar
        # Return: recent articles, press releases, announcements
        pass

class GoogleSearchCollector(DataCollector):
    """Search Google for company information"""
    async def collect(self, company: Dict) -> Dict:
        # Return: search results, snippets, featured articles
        pass

class ImageCollector(DataCollector):
    """Download images from company website"""
    async def collect(self, company: Dict) -> Dict:
        # Return: list of image URLs and downloaded images
        pass

class BusinessRecordsCollector(DataCollector):
    """Look up business registration records"""
    async def collect(self, company: Dict) -> Dict:
        # Search Secretary of State, Dun & Bradstreet, etc.
        # Return: registration info, officers, history
        pass

class MultiSourceCollector:
    """Orchestrate collection from multiple sources"""
    
    def __init__(self):
        self.collectors = {
            'website': WebsiteScraper(),
            'linkedin': LinkedInCollector(),
            'news': NewsCollector(),
            'google': GoogleSearchCollector(),
            'images': ImageCollector(),
            'business': BusinessRecordsCollector()
        }
    
    async def collect_all(self, company: Dict) -> Dict:
        """Collect from all sources in parallel"""
        tasks = [
            collector.collect(company) 
            for collector in self.collectors.values()
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return {
            name: result 
            for name, result in zip(self.collectors.keys(), results)
            if not isinstance(result, Exception)
        }
```

### Integration Steps
1. Create `data_collectors.py` module
2. Instantiate `MultiSourceCollector` in AI researcher
3. Call after Stage 1 analysis to collect data for gaps
4. Pass enriched data to Stage 2 AI analysis
5. Store collected data in company output directory

---

## 5. IMAGE MANAGEMENT & TAGGING

### Create New Module: `image_manager.py`

```python
class ImageManager:
    """Manage image downloading, storage, and metadata"""
    
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)
    
    def get_company_image_dir(self, company_name: str) -> Path:
        """Get/create directory for company images"""
        dir_path = self.base_dir / self._sanitize_name(company_name)
        dir_path.mkdir(exist_ok=True)
        return dir_path
    
    async def download_image(self, 
                            url: str, 
                            company_name: str, 
                            person_name: str = None,
                            image_type: str = "general") -> Optional[Path]:
        """Download image from URL and save with metadata"""
        try:
            company_dir = self.get_company_image_dir(company_name)
            filename = f"{person_name or 'company'}_{image_type}_{datetime.now().timestamp()}.jpg"
            filepath = company_dir / filename
            
            # Download image
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status == 200:
                        with open(filepath, 'wb') as f:
                            f.write(await resp.read())
            
            # Save metadata
            metadata = {
                'url': url,
                'company': company_name,
                'person': person_name,
                'type': image_type,
                'downloaded_at': datetime.now(),
                'file_path': str(filepath)
            }
            self.save_metadata(filepath, metadata)
            
            return filepath
        except Exception as e:
            logger.warning(f"Failed to download image {url}: {e}")
            return None
    
    def save_metadata(self, image_path: Path, metadata: Dict):
        """Save image metadata as YAML"""
        meta_path = image_path.with_suffix('.yaml')
        with open(meta_path, 'w') as f:
            yaml.dump(metadata, f)
    
    async def detect_people_in_image(self, image_path: Path) -> Dict:
        """Use AI to detect and describe people in image"""
        # Option 1: Claude Vision API
        with open(image_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode()
        
        response = await claude.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": image_data
                            }
                        },
                        {
                            "type": "text",
                            "text": "Identify any people in this image. For each person, describe: name (if visible), job title, role, and any identifying features."
                        }
                    ]
                }
            ]
        )
        return response.content[0].text
```

### Integration Steps
1. Create `image_manager.py` module
2. Instantiate in AI researcher
3. Download images during data collection stage
4. Detect people in images using Claude Vision
5. Tag images with person names and metadata
6. Create index file mapping people to images

---

## 6. CONFIDENCE SCORING & METADATA

### Enhance `parse_and_save_reports()` Method

**Current Output:**
```
[Company]_CONTACTS.md
[Company]_PAIN_POINTS.md
[Company]_CALL_PREP.md
```

**Enhanced Output:**
```
[Company]_CONTACTS.md
[Company]_PAIN_POINTS.md
[Company]_CALL_PREP.md
[Company]_METADATA.json          (NEW)
[Company]_ITERATIONS.json        (NEW)
images/                          (NEW)
  ├── ceo_profile.jpg
  ├── ceo_profile.yaml
  ├── team_photo.jpg
  └── team_photo.yaml
```

### Create Metadata Structure

```python
class ReportMetadata:
    """Metadata for each company report"""
    
    def __init__(self, company_name: str):
        self.company_name = company_name
        self.processed_at = datetime.now()
        self.confidence_scores = {
            'contacts': 0.0,
            'pain_points': 0.0,
            'call_prep': 0.0
        }
        self.data_sources = []
        self.iterations_completed = 0
        self.missing_fields = []
        self.images_downloaded = 0
    
    def save(self, output_path: Path):
        """Save metadata as JSON"""
        data = {
            'company_name': self.company_name,
            'processed_at': self.processed_at.isoformat(),
            'confidence_scores': self.confidence_scores,
            'data_sources': self.data_sources,
            'iterations_completed': self.iterations_completed,
            'missing_fields': self.missing_fields,
            'images_downloaded': self.images_downloaded
        }
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
```

### Calculate Confidence Scores

```python
def calculate_confidence_score(ai_response: str, section: str) -> float:
    """
    Calculate confidence score for a section (0.0 - 1.0).
    
    High confidence indicators:
    - Specific names and titles
    - Real URLs and emails
    - Recent news and dates
    - Specific metrics and numbers
    
    Low confidence indicators:
    - Generic descriptions
    - "likely", "probably", "possibly"
    - Placeholder data
    - Missing website access note
    """
    score = 0.0
    
    # Check for data availability
    if "no data available" in ai_response.lower():
        return 0.2  # Very low confidence
    
    # Check for specific vs. generic content
    if has_specific_names(ai_response):
        score += 0.3
    if has_dates_and_numbers(ai_response):
        score += 0.2
    if has_urls_and_emails(ai_response):
        score += 0.2
    if not has_generic_language(ai_response):
        score += 0.3
    
    return min(score, 1.0)
```

---

## 7. ITERATION HISTORY TRACKING

### Create Iteration Log

```python
class IterationHistory:
    """Track iterations for each company"""
    
    def __init__(self, company_name: str):
        self.company_name = company_name
        self.iterations = []
    
    def add_iteration(self, stage: int, result: str, gaps: List[str], data_collected: Dict):
        """Record iteration details"""
        self.iterations.append({
            'stage': stage,
            'timestamp': datetime.now(),
            'result_summary': result[:500],  # First 500 chars
            'gaps_identified': gaps,
            'data_sources_used': list(data_collected.keys()),
            'data_summary': {k: len(str(v)) for k, v in data_collected.items()}
        })
    
    def save(self, output_path: Path):
        """Save iteration history"""
        with open(output_path, 'w') as f:
            json.dump({
                'company': self.company_name,
                'total_iterations': len(self.iterations),
                'iterations': self.iterations
            }, f, indent=2)
```

---

## 8. DYNAMIC PROMPT BUILDING

### Enhance `build_research_prompt()` Method

```python
def build_research_prompt(self, 
                         company: Dict[str, str], 
                         iteration: int = 1,
                         previous_result: Optional[str] = None,
                         collected_data: Optional[Dict] = None) -> str:
    """
    Build dynamic prompt based on iteration stage.
    
    Stage 1: Initial analysis (basic info)
    Stage 2: Gap identification (what's missing?)
    Stage 3: Data enrichment (here's new data, refine)
    Stage 4: Validation (check quality, identify remaining gaps)
    Stage 5: Final (polish and prepare for delivery)
    """
    
    if iteration == 1:
        # Initial analysis prompt
        return self._build_initial_prompt(company)
    
    elif iteration == 2:
        # Identify gaps prompt
        return self._build_gap_identification_prompt(company, previous_result)
    
    elif iteration == 3:
        # Data enrichment prompt
        return self._build_enrichment_prompt(company, collected_data, previous_result)
    
    elif iteration == 4:
        # Validation prompt
        return self._build_validation_prompt(company, previous_result)
    
    elif iteration == 5:
        # Final polish prompt
        return self._build_final_prompt(company, previous_result)

def _build_gap_identification_prompt(self, company: Dict, previous_result: str) -> str:
    """Prompt AI to identify what data is missing"""
    return f"""
Based on this previous analysis:
{previous_result}

---

What critical information is still missing to create a complete sales intelligence report?

For each missing piece of information, recommend:
1. Data source (website, LinkedIn, news, etc.)
2. Specific data point needed
3. Why it's important for sales

Format your response as:
MISSING_DATA:
1. [Data Point] - Source: [Website/LinkedIn/News/etc] - Reason: [Why needed]
2. [Next Data Point] - Source: [Source] - Reason: [Reason]
...

RECOMMENDED_ACTIONS:
- Action 1
- Action 2
...
"""

def _build_enrichment_prompt(self, company: Dict, collected_data: Dict, previous_result: str) -> str:
    """Prompt AI to refine analysis with new collected data"""
    
    data_summary = self._summarize_collected_data(collected_data)
    
    return f"""
Here's additional data we collected for {company['Title']}:

{data_summary}

---

Based on this new information, please refine your previous analysis:

ORIGINAL ANALYSIS:
{previous_result}

---

INSTRUCTIONS:
1. Incorporate the new data into your analysis
2. Correct any inaccuracies from the first pass
3. Add specific names, titles, and contact formats where now available
4. Update pain points with actual evidence
5. Enhance conversation starters with real observations

Use the same format as before:
{self.delimiters['contacts']}
[Refined contacts section]

{self.delimiters['pain_points']}
[Refined pain points section]

{self.delimiters['call_prep']}
[Refined call prep section]
"""
```

---

## 9. EXECUTION FLOW DIAGRAM

```
Start Batch Processing
    ↓
For Each Company:
    │
    ├─→ Stage 1: Initial Analysis
    │   ├─ build_research_prompt(company, iteration=1)
    │   ├─ ai.analyze()
    │   ├─ parse_output()
    │   ├─ save_reports(stage=1)
    │   └─ extract_gaps() → gap_list
    │
    ├─→ Stage 2: Gap Identification
    │   ├─ build_research_prompt(company, iteration=2, previous_result)
    │   ├─ ai.analyze()
    │   ├─ parse_output() → [missing_data_sources]
    │   ├─ missing_functions_logger.log()
    │   └─ data_to_collect ← parse AI response
    │
    ├─→ Stage 3: Collect Data
    │   ├─ multi_source_collector.collect_all(company, data_to_collect)
    │   ├─ for each source in [website, linkedin, news, images, etc]:
    │   │   ├─ collector.collect()
    │   │   └─ save results
    │   └─ enriched_data ← merge all sources
    │
    ├─→ Stage 4: Enrich & Refine
    │   ├─ build_research_prompt(company, iteration=3, collected_data=enriched_data)
    │   ├─ ai.analyze()
    │   ├─ parse_output()
    │   ├─ save_reports(stage=2, label="enriched")
    │   ├─ detect_people_in_images()
    │   └─ iteration_history.add(stage=4)
    │
    ├─→ Stage 5: Validate & Score
    │   ├─ build_research_prompt(company, iteration=4)
    │   ├─ ai.analyze() → quality_check
    │   ├─ calculate_confidence_scores()
    │   ├─ metadata.save()
    │   └─ iteration_history.add(stage=5)
    │
    └─→ Output
        ├─ [Company]_CONTACTS.md
        ├─ [Company]_PAIN_POINTS.md
        ├─ [Company]_CALL_PREP.md
        ├─ [Company]_METADATA.json
        ├─ [Company]_ITERATIONS.json
        └─ images/[company]/
            ├─ *.jpg
            ├─ *.yaml
            └─ index.json

After All Companies:
    ├─ _batch_summary.json (with iteration counts)
    ├─ _missing_functions_report.json
    └─ _data_quality_report.json
```

---

## 10. QUICK IMPLEMENTATION CHECKLIST

### Phase 1: Foundation (Week 1)
- [ ] Implement `scrape_website()` method
- [ ] Create `MissingFunctionsLogger` class
- [ ] Add iteration tracking to `process_company()`
- [ ] Create metadata structure

### Phase 2: Data Collection (Week 2)
- [ ] Create `data_collectors.py` module
- [ ] Implement `WebsiteScraper`
- [ ] Implement `LinkedInCollector`
- [ ] Implement `NewsCollector`
- [ ] Add `MultiSourceCollector` orchestrator

### Phase 3: Images & Analysis (Week 3)
- [ ] Create `image_manager.py` module
- [ ] Implement `ImageCollector`
- [ ] Add person detection via Claude Vision
- [ ] Create image tagging system

### Phase 4: Dynamic Prompts (Week 4)
- [ ] Enhance `build_research_prompt()` for multi-stage
- [ ] Create stage-specific prompt templates
- [ ] Implement gap identification logic
- [ ] Add confidence scoring

### Phase 5: Integration & Testing (Week 5)
- [ ] Integrate all components
- [ ] Add comprehensive logging
- [ ] Create test suite
- [ ] Performance optimization

---

## Summary

**7 Key Integration Points:**

1. **Multi-stage analysis loop** - Execute AI multiple times with feedback
2. **Website scraping** - Implement `scrape_website()` method
3. **Missing functions tracking** - Log AI-identified gaps
4. **Multi-source data collection** - Collect from 5+ sources
5. **Image management** - Download and tag images
6. **Confidence scoring** - Quantify data quality
7. **Dynamic prompting** - Tailor prompts to iteration stage

**Expected Outcomes:**

- Dramatically improved data quality through enrichment
- Automated identification of missing information
- Visual assets (images, org charts) collected and tagged
- Quality metrics for each company
- Detailed audit trail of all research iterations

