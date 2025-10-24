# Citation System Implementation

## Overview

The intelligent research system now includes **comprehensive citation tracking** with clickable links for every fact captured during research.

## Key Features

### 1. **Automatic Citation Tracking**
- Every data point (contacts, pain points, technologies) includes a `source_url` parameter
- Citation numbers are automatically generated and reused for duplicate URLs
- Footnote references use standard markdown syntax: `[^1]`, `[^2]`, etc.

### 2. **Inline Citations**
Every fact in the report includes inline citation markers:
- **Contact names**: John Smith[^1]
- **Titles**: CEO[^1]
- **Emails**: john@example.com[^1]
- **Pain points**: "Scaling infrastructure challenges"[^2]
- **Technologies**: React[^1], Node.js[^1]

### 3. **Clickable Footnotes**
At the end of each report, a **Citations** section lists all sources:
```markdown
## 📚 Citations

[^1]: https://example.com/about
[^2]: https://example.com/blog/scaling-challenges
```

When viewed in markdown renderers (GitHub, VS Code, etc.), clicking `[^1]` jumps to the citation URL.

## Technical Implementation

### Modified Components

#### 1. **DataAccumulator** (`intelligent_research/data_accumulator.py`)
- Added `citation_map: Dict[str, int]` to track URL → citation number mapping
- Added `_get_citation_number(url)` method to generate/reuse citation numbers
- Updated all `add_*` methods to require `source_url` parameter
- Added `get_citations()` method to retrieve citation mappings for report generation

**Key methods:**
```python
def _get_citation_number(self, url: str) -> int:
    """Get or create citation number for a URL (reuses existing)"""

def add_contact(self, name, title, email, phone, source, source_url):
    """Stores contact with citation tracking"""

def get_citations(self) -> Dict[int, str]:
    """Returns mapping of citation number → URL"""
```

#### 2. **WebsiteExplorer** (`intelligent_research/website_explorer.py`)
- Modified `explore_page()` to return tuple: `(success, content, url)`
- URL is now returned for citation tracking

**Change:**
```python
# Before:
def explore_page(url) -> Tuple[bool, Optional[str]]

# After:
def explore_page(url) -> Tuple[bool, Optional[str], str]
```

#### 3. **ResearchOrchestrator** (`intelligent_research/research_orchestrator.py`)
- Added `current_source_url` tracking variable
- Updated `_explore_page()` to set `current_source_url` when scraping succeeds
- Modified all save functions to include `source_url` parameter
- Functions automatically use `current_source_url` if `source_url` not explicitly provided

**Key additions:**
```python
self.current_source_url: str = ""  # Tracks current page being analyzed

def _explore_page(self, url, reason):
    success, content, explored_url = self.explorer.explore_page(url, reason)
    if success:
        self.current_source_url = explored_url  # Set citation context
```

#### 4. **AIDecisionEngine** (`intelligent_research/ai_decision_engine.py`)
- Updated AI prompts to REQUIRE `source_url` in all function calls
- Added comprehensive examples and validation rules
- Explained citation importance and usage to the AI

**Prompt enhancements:**
```python
Available functions you can suggest:
- save_contact: {... "source_url": "REQUIRED"}
- save_pain_point: {... "source_url": "REQUIRED"}
- extract_tech_stack: {... "source_url": "REQUIRED"}

=== CRITICAL: SOURCE URL REQUIREMENT ===
EVERY save_* call MUST include source_url parameter.
```

#### 5. **Report Generator** (in `research_orchestrator.py`)
- Enhanced `generate_final_report()` to include inline citations
- Added `## 📚 Citations` section with footnote definitions
- Citations appear after every fact in tables and sections

**Report format:**
```markdown
| Name | Title | Email |
|------|-------|-------|
| John Smith[^1] | CEO[^1] | john@example.com[^1] |

## 📚 Citations
[^1]: https://example.com/about
```

## How It Works

### Data Flow

1. **Page Exploration**
   ```
   User → explore_page(url) → WebsiteExplorer
         → Returns (success, content, url)
         → Sets current_source_url
   ```

2. **Data Extraction**
   ```
   AI analyzes content
   → Identifies facts (name, title, email, etc.)
   → Calls save_contact(name="John", ..., source_url=current_source_url)
   → DataAccumulator assigns citation number
   ```

3. **Citation Tracking**
   ```
   DataAccumulator:
   - Checks if URL already cited → Reuse number
   - New URL → Increment counter, assign new number
   - Stores: citation_map[url] = citation_number
   ```

4. **Report Generation**
   ```
   For each contact/pain_point:
   - Lookup citation number
   - Add inline marker [^{citation_num}]

   At end of report:
   - List all citations: [^1]: URL, [^2]: URL, ...
   ```

### Citation Reuse Example

If the same page contains multiple facts:
- Contact: John Smith[^1] (from https://example.com/team)
- Contact: Jane Doe[^1] (from https://example.com/team)
- Pain Point: Scaling[^2] (from https://example.com/blog)
- Tech: React[^1] (from https://example.com/team)

All facts from the same URL share the same citation number!

## Markdown Compatibility

### Standard Markdown Footnotes
The system uses standard markdown footnote syntax, compatible with:
- ✅ GitHub (clickable footnotes)
- ✅ VS Code Markdown Preview
- ✅ Obsidian
- ✅ Notion
- ✅ Most markdown renderers

### Rendering Behavior
When viewing the markdown:
- **Inline markers** `[^1]` appear as superscript links
- **Clicking** jumps to the citation definition
- **Citations section** shows all URLs with reverse links back to references

## Benefits

### For Users
1. **Verifiable Facts**: Every fact has a source you can click
2. **Trust Building**: Transparent sourcing builds confidence
3. **Deep Dive**: Click through to explore sources in detail
4. **Audit Trail**: Complete record of where information came from

### For Sales Teams
1. **Fact-Checking**: Verify information before calls
2. **Context**: Read full source material for better understanding
3. **Updates**: Check if information is still current
4. **Credibility**: Show prospects you've done your homework

## Testing

Run the system with citation tracking:
```bash
python cerebras_intelligent_research.py --csv google_maps_leads.csv --limit 1 --max-iterations 3
```

Check the output report for:
- ✅ Citation markers after each fact
- ✅ Citations section at the end
- ✅ Correct URL mapping
- ✅ Reused citation numbers for duplicate URLs

## Example Output

### Contacts Section
```markdown
## 👥 Contacts Identified (2)

| Name | Title | Email | Phone | Source |
|------|-------|-------|-------|--------|
| John Smith[^1] | CEO[^1] | john@example.com[^1] | 555-1234[^1] | About Us page |
| Jane Doe[^2] | CTO[^2] | jane@example.com[^2] | 555-5678[^2] | Team page |
```

### Pain Points Section
```markdown
## 💡 Pain Points Identified (1)

### 1. Infrastructure scaling challenges[^3]

**Evidence:** Blog post discusses migration to microservices[^3]

**Source:** Company blog
```

### Citations Section
```markdown
## 📚 Citations

*All facts in this report are cited with clickable sources below:*

[^1]: https://example.com/about
[^2]: https://example.com/team
[^3]: https://example.com/blog/scaling-infrastructure
```

## Future Enhancements

Potential improvements:
1. **Date tracking**: Record when each source was accessed
2. **Content snippets**: Include relevant excerpt from source
3. **Confidence scores**: Rate reliability of each source
4. **Archive links**: Save archived versions of sources
5. **Citation export**: Export citations in BibTeX, APA, etc.

## Troubleshooting

### Citations Not Appearing
- Check if `source_url` is being passed to save functions
- Verify `current_source_url` is set during page exploration
- Ensure AI is including `source_url` in function calls

### Wrong URLs
- Verify WebsiteExplorer returns correct URL from scraping
- Check URL normalization and validation

### Missing Citations
- Add warnings when `source_url` is empty
- Update AI prompts to emphasize source_url requirement

## Summary

The citation system provides **complete transparency and traceability** for all research facts. Every name, title, email, pain point, and technology mention is now backed by a clickable source URL, making the research reports fully verifiable and trustworthy.

**Key Achievement**: From "we found this information" → "we found this information at [exact URL] and you can verify it yourself with one click"
