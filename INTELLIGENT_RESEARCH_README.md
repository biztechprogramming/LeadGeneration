# Intelligent Research System Documentation

## Overview

The Intelligent Research System is an AI-driven, iterative approach to sales intelligence gathering that goes beyond static prompting. Instead of using predefined templates, it employs an AI decision engine that:

1. Analyzes currently available data
2. Decides what information is relevant
3. Determines what actions to take
4. Suggests next exploration steps
5. Continues iteratively until sufficient intelligence is gathered

This approach mimics how a human researcher would explore a company - starting with basic information and progressively diving deeper into the most promising areas.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                   IterativeResearchOrchestrator              │
│  Main controller coordinating all components                 │
└───────────────┬─────────────────────────────────────────────┘
                │
                ├─────► GeminiCerebrasClient
                │       ├─ Handles API communication
                │       └─ Parses JSON responses
                │
                ├─────► AIDecisionEngine
                │       ├─ Sends accumulated data to AI
                │       ├─ Receives structured decisions
                │       └─ Suggests: relevant_data, actions, next_steps
                │
                ├─────► FunctionRegistry
                │       ├─ Tracks available functions
                │       ├─ Executes requested actions
                │       └─ Logs missing functions for future dev
                │
                ├─────► DataAccumulator
                │       ├─ Stores contacts, pain points, tech stack
                │       ├─ Tracks sources explored
                │       └─ Builds growing context for AI
                │
                ├─────► ImageCollector
                │       ├─ Detects people images in HTML
                │       ├─ Downloads with metadata
                │       └─ Creates image manifest
                │
                └─────► WebsiteExplorer
                        ├─ Explores pages (placeholder)
                        ├─ Searches LinkedIn (placeholder)
                        └─ Searches news (placeholder)
```

## How the AI Decision Loop Works

### 1. Data Accumulation Phase

The system starts with basic company information from CSV:
- Company name
- Website URL
- Address
- Phone number

### 2. AI Analysis Phase

The AI Decision Engine sends accumulated data to Cerebras API with system prompt:

```python
System: "You are an intelligent research assistant that analyzes
         company data and suggests next steps."

User: "Here's what we know so far: [accumulated_data]
       What should we do next?"
```

### 3. Structured Decision Response

The AI returns JSON with four key components:

```json
{
  "relevant_data": [
    "Found CEO name: John Smith",
    "Company focuses on manufacturing automation",
    "Recent expansion mentioned on about page"
  ],
  "actions": [
    {"function": "save_contact", "params": {"name": "John Smith", "title": "CEO"}},
    {"function": "save_pain_point", "params": {"description": "Manual processes"}}
  ],
  "next_steps": [
    {"function": "explore_page", "params": {"url": "/team", "reason": "Find more contacts"}},
    {"function": "search_linkedin", "params": {"company": "ACME Corp"}}
  ],
  "status": "continue"
}
```

### 4. Execution Phase

The orchestrator executes suggested actions:
- **Actions**: Immediate data processing (save contacts, extract pain points)
- **Next Steps**: New exploration tasks (scrape pages, search external sources)

### 5. Iteration

Process repeats with enriched context until:
- AI sets `status: "complete"` (sufficient data collected)
- Maximum iterations reached (default: 10)
- Critical error occurs

## Function Registry System

### Purpose

The Function Registry provides:
1. **Discoverability**: AI can suggest functions by name
2. **Execution**: Registry routes function calls with parameters
3. **Logging**: Missing functions logged for future development
4. **Extensibility**: Easy to add new capabilities

### Currently Implemented Functions

| Function | Parameters | Purpose |
|----------|-----------|---------|
| `save_contact` | name, title, email, phone, source | Store contact information |
| `save_pain_point` | description, evidence, source | Record identified pain point |
| `download_image` | url, person_name, context | Download people images |
| `explore_page` | url, reason | Scrape webpage (placeholder) |
| `search_linkedin` | company, person | LinkedIn search (placeholder) |
| `search_news` | company, topics | News search (placeholder) |
| `extract_tech_stack` | technologies | Record technologies used |
| `save_company_info` | key, value | Store metadata |

### Missing Function Logging

When AI suggests a function that doesn't exist:

1. Registry catches the missing function
2. Logs to `missing_functions.json` with counter
3. Prints warning but continues execution
4. Developers can prioritize implementation based on frequency

Example `missing_functions.json`:
```json
{
  "scrape_glassdoor_reviews": 5,
  "search_twitter": 3,
  "analyze_competitors": 8
}
```

### Adding New Functions

```python
# 1. Implement the function
def new_research_function(param1: str, param2: int):
    """Your function logic."""
    # Do something
    return result

# 2. Register in _register_functions()
self.registry.register("new_research_function", self._new_research_function)

# 3. Create wrapper that accesses accumulator
def _new_research_function(self, param1: str, param2: int):
    result = new_research_function(param1, param2)
    self.current_accumulator.add_something(result)
```

## Image Collection Pipeline

### Detection Strategy

The `ImageCollector` uses heuristics to identify people images:

**Positive Indicators** (likely a person):
- team, staff, employee, founder, ceo, president
- director, manager, headshot, profile, people
- leadership, executive, member, portrait

**Negative Indicators** (not a person):
- logo, icon, banner, background, product
- chart, graph, diagram, screenshot

### Detection Process

1. **Parse HTML**: BeautifulSoup finds all `<img>` tags
2. **Filter Images**: Apply heuristics to src/alt text
3. **Extract Context**: Look for nearby captions, headings
4. **Download Image**: Save with hash-based filename
5. **Store Metadata**: Create JSON manifest with details

### Image Metadata

Each detected image stored with:
```json
{
  "filename": "person_a1b2c3d4e5f6.jpg",
  "source_url": "https://company.com/images/team/john.jpg",
  "page_context": "Team page",
  "person_name": "John Smith",
  "person_title": "CEO",
  "alt_text": "John Smith - Chief Executive Officer",
  "downloaded_at": "2025-01-24T10:30:00"
}
```

### Image Organization

```
output_dir/
└── images/
    └── Company_Name/
        ├── person_abc123def456.jpg
        ├── person_789ghi012jkl.jpg
        └── image_manifest.json
```

## Data Accumulation Strategy

### Why Accumulation Matters

Traditional approaches analyze once and generate static reports. This system:
- **Builds Context**: Each iteration adds to AI's knowledge
- **Enables Refinement**: AI sees previous findings and can dig deeper
- **Prevents Redundancy**: AI tracks explored sources
- **Allows Prioritization**: AI focuses on high-value areas

### Data Structure

```python
{
  "company": {
    "Title": "Company Name",
    "WebsiteURL": "company.com",
    "Address": "123 Main St",
    "PhoneNumber": "555-1234"
  },
  "contacts": [
    {
      "name": "John Smith",
      "title": "CEO",
      "email": "john@company.com",
      "phone": "",
      "source": "About page",
      "added_at": "2025-01-24T10:15:00"
    }
  ],
  "pain_points": [
    {
      "description": "Manual data entry processes",
      "evidence": "Job posting mentions 'reducing manual workflows'",
      "source": "Careers page",
      "added_at": "2025-01-24T10:17:00"
    }
  ],
  "tech_stack": [
    {
      "technology": "Salesforce",
      "category": "CRM",
      "source": "Integration partners page",
      "added_at": "2025-01-24T10:20:00"
    }
  ],
  "news": [],
  "images": [],
  "sources_explored": [
    {
      "source": "company.com",
      "type": "homepage",
      "explored_at": "2025-01-24T10:10:00"
    }
  ],
  "metadata": {
    "started_at": "2025-01-24T10:10:00",
    "iterations": 3
  }
}
```

### Accumulation Benefits

1. **Progressive Enhancement**: Start broad, go deep
2. **Context-Aware Decisions**: AI sees full picture
3. **Audit Trail**: Track when/where data found
4. **Quality Control**: Review sources and evidence

## Configuration Options

### API Configuration

**Environment Variables** (.env file):
```bash
CEREBRAS_API_KEY=your-api-key-here
```

**Model Selection**:
```python
# Default: llama-3.3-70b (fast, capable, cost-effective)
client = GeminiCerebrasClient(api_key, model="llama-3.3-70b")

# Alternative models:
# - llama-3.1-8b (faster, cheaper, less capable)
# - llama-3.1-70b (balanced)
```

### Research Parameters

**Maximum Iterations**:
```python
# Control research depth
orchestrator.research_company(company, max_iterations=10)
```

**Batch Processing**:
```python
# Process subset of companies
orchestrator.run_batch_research(
    limit=5,           # Process first 5 companies
    start_index=0      # Start from beginning
)
```

### AI Decision Parameters

**Temperature**: Controls response randomness
```python
client.send_prompt(
    prompt,
    temperature=0.7,  # Default: balanced creativity/consistency
    max_tokens=4000   # Maximum response length
)
```

## Usage Examples

### Basic Usage

```bash
# Test with first company
python test_intelligent_research.py

# Run full batch
python cerebras_intelligent_research.py --csv google_maps_leads.csv
```

### Advanced Usage

```bash
# Verbose testing with custom iterations
python test_intelligent_research.py --verbose --max-iterations 5

# Process specific subset
python cerebras_intelligent_research.py \
    --csv google_maps_leads.csv \
    --output research_output_jan \
    --limit 10 \
    --start 5 \
    --max-iterations 15
```

### Programmatic Usage

```python
from cerebras_intelligent_research import IterativeResearchOrchestrator

# Initialize
orchestrator = IterativeResearchOrchestrator(
    csv_path='google_maps_leads.csv',
    output_dir='my_research'
)

# Research single company
company = {"Title": "ACME Corp", "WebsiteURL": "acme.com"}
data = orchestrator.research_company(company, max_iterations=10)

# Generate report
orchestrator.generate_final_report("ACME Corp", data)

# Access accumulated data
print(f"Contacts: {len(data['contacts'])}")
print(f"Pain points: {len(data['pain_points'])}")
```

## Output File Structure

### Per-Company Output

```
output_dir/
├── Company_Name_INTELLIGENT_RESEARCH.md
├── images/
│   └── Company_Name/
│       ├── person_*.jpg
│       └── image_manifest.json
├── missing_functions.json
└── _batch_summary.json
```

### Research Report Format

```markdown
# Intelligent Research Report: Company Name

**Generated:** 2025-01-24 10:30:00
**Research Iterations:** 5

---

## 🏢 Company Overview
[Basic company info]

---

## 👥 Contacts Identified (3)
| Name | Title | Email | Phone | Source |
|------|-------|-------|-------|--------|
| John Smith | CEO | john@co.com | 555-1234 | About page |

---

## 💡 Pain Points Identified (2)
### 1. Manual data entry processes
**Evidence:** Job posting mentions "reducing manual workflows"
**Source:** Careers page

---

## 🛠️ Technology Stack (4)
- **Salesforce** (CRM) - Source: Partners page
- **Python** (Backend) - Source: Job posting

---

## 📰 Recent News (1)
[News items if found]

---

## 📸 People Images (5)
### John Smith
**Title:** CEO
**Image:** `person_abc123.jpg`
**Context:** Team page

---

## 🔍 Sources Explored (8)
- [homepage] https://company.com
- [about] https://company.com/about
- [team] https://company.com/team
```

## Troubleshooting Guide

### Common Issues

#### 1. "CEREBRAS_API_KEY not set"

**Solution**:
```bash
# Create .env file
cp .env.example .env

# Add your API key
echo "CEREBRAS_API_KEY=your-key-here" > .env

# Or export directly
export CEREBRAS_API_KEY="your-key-here"
```

#### 2. "API timed out after 120 seconds"

**Cause**: Network issues or API overload

**Solution**:
- Check internet connection
- Retry the request
- Reduce max_tokens if responses are too large

#### 3. "Failed to parse JSON response"

**Cause**: AI returned malformed JSON or unexpected text

**Solution**:
- Check AI logs in verbose mode
- Adjust temperature (lower = more consistent)
- Improve system prompt specificity

#### 4. "No companies found in CSV"

**Cause**: CSV file empty or wrong format

**Solution**:
```bash
# Verify CSV exists and has data
head -5 google_maps_leads.csv

# Check format
# Expected: Title,Address,PhoneNumber,WebsiteURL
```

#### 5. Missing Functions Logged Frequently

**This is expected!** The system logs missing functions to guide development.

**To check**:
```bash
cat output_dir/missing_functions.json

# Example output:
# {
#   "scrape_glassdoor": 12,
#   "analyze_social_media": 8
# }
```

### Debugging Tips

#### Enable Verbose Mode

```bash
python test_intelligent_research.py --verbose
```

Shows:
- All AI decisions with full JSON
- Function execution details
- Data accumulation progression
- Error stack traces

#### Check Test Report

```bash
cat test_output/test_report.json
```

Contains:
- All tests passed/failed
- AI decisions made
- Functions executed
- Missing functions logged
- Data progression snapshots

#### Inspect Missing Functions

```bash
python -c "import json; print(json.dumps(json.load(open('output_dir/missing_functions.json')), indent=2))"
```

#### Monitor API Calls

Add logging to see raw API requests/responses:
```python
# In GeminiCerebrasClient.send_prompt()
print(f"REQUEST: {prompt[:200]}...")
print(f"RESPONSE: {response[:200]}...")
```

## Comparison with Original System

### sales_intelligence_cerebras.py (Static Approach)

**How it works**:
1. Load company data from CSV
2. Build single comprehensive prompt with all sections
3. Send to Cerebras API once
4. Parse response using delimiters
5. Save 3 markdown files (CONTACTS, PAIN_POINTS, CALL_PREP)

**Advantages**:
- Simple, predictable
- Fast (single API call)
- Easy to debug

**Limitations**:
- No iterative refinement
- Limited by single prompt size
- Can't adapt based on available data
- No web scraping integration
- No image collection
- No function extensibility

### cerebras_intelligent_research.py (Iterative Approach)

**How it works**:
1. Load company data from CSV
2. Initialize with basic info
3. **Iteration loop** (up to max_iterations):
   - Send accumulated data to AI
   - AI analyzes and suggests actions
   - Execute suggested functions
   - Explore suggested sources
   - Add findings to accumulator
   - Repeat until AI says "complete"
4. Generate comprehensive markdown report

**Advantages**:
- Iterative refinement based on findings
- AI-driven exploration strategy
- Extensible function registry
- Image collection with metadata
- Data accumulation with audit trail
- Adapts to available data
- Logs missing functions for future dev

**Limitations**:
- More complex architecture
- Multiple API calls (higher cost)
- Slower execution
- Requires more robust error handling

### When to Use Which

**Use Static Approach** (`sales_intelligence_cerebras.py`):
- Quick batch processing needed
- Predictable output format required
- Cost optimization critical
- Simple research needs
- No web scraping available

**Use Intelligent Approach** (`cerebras_intelligent_research.py`):
- Deep research required
- Web scraping available
- Image collection needed
- Extensible system desired
- Research quality > speed
- Development of new capabilities planned

### Performance Comparison

| Metric | Static | Intelligent |
|--------|--------|-------------|
| API Calls | 1 per company | 3-10 per company |
| Time | 5-10 seconds | 30-120 seconds |
| Cost | $0.001-0.003 | $0.005-0.020 |
| Depth | Fixed | Adaptive |
| Images | No | Yes |
| Extensibility | Low | High |

## Development Roadmap

### Phase 1: Core Enhancement (Current)
- ✅ AI decision engine
- ✅ Function registry
- ✅ Image collection
- ✅ Data accumulation
- ⏳ Web scraping integration

### Phase 2: External Sources
- ⏳ LinkedIn integration
- ⏳ News API integration
- ⏳ Glassdoor reviews
- ⏳ Social media analysis

### Phase 3: Intelligence Enhancement
- ⏳ Competitor analysis
- ⏳ Market research
- ⏳ Financial data
- ⏳ Technology stack detection

### Phase 4: Output Enhancement
- ⏳ Multi-format reports (PDF, DOCX)
- ⏳ CRM integration
- ⏳ Email templates
- ⏳ Call scripts

## Contributing

To add new functions:

1. Implement core function logic
2. Add wrapper method to orchestrator
3. Register in `_register_functions()`
4. Update AI system prompt with function description
5. Test with test suite
6. Update documentation

Example:
```python
# 1. Core logic
def analyze_social_media(company_name: str, platforms: List[str]) -> Dict:
    """Analyze company social media presence."""
    results = {}
    for platform in platforms:
        # Your logic here
        results[platform] = analysis
    return results

# 2. Wrapper
def _analyze_social_media(self, company: str, platforms: List[str]):
    """Wrapper for social media analysis."""
    results = analyze_social_media(company, platforms)
    for platform, data in results.items():
        self.current_accumulator.add_source(f"{platform}: {company}", "social")
    print(f"    ✓ Analyzed {len(platforms)} social platforms")

# 3. Register
self.registry.register("analyze_social_media", self._analyze_social_media)

# 4. Update AI prompt (in AIDecisionEngine system_prompt)
# - analyze_social_media: {"company": "...", "platforms": ["linkedin", "twitter"]}
```

## License

This system is part of the Lead-Generation project.

## Support

For issues or questions:
1. Check troubleshooting guide above
2. Review test output in `test_output/test_report.json`
3. Enable verbose mode for detailed logs
4. Check missing functions log for capability gaps
