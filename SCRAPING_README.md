# Website Scraping with Firecrawl MCP

A collection of Python scripts for scraping websites using the Firecrawl MCP tool through Claude Code.

## Overview

This project includes three complementary scripts for web scraping:

1. **scrape_url.py** - Educational script showing the Firecrawl MCP workflow
2. **scrape_url_mcp.py** - MCP request generator for programmatic use
3. **scrape_and_save.py** - Content saver for post-scraping file operations

## Prerequisites

- Python 3.7+
- Claude Code with Firecrawl MCP server configured
- Internet connection for web scraping

## Quick Start

### Method 1: Direct Request to Claude Code

The simplest way to scrape a website:

```bash
# Just ask Claude Code directly:
"Please scrape https://example.com using Firecrawl and show me the markdown"
```

Claude Code will automatically call the `mcp__firecrawl__firecrawl_scrape` tool and display results.

### Method 2: Using the Helper Scripts

```bash
# Generate scraping instructions
python scrape_url_mcp.py https://example.com

# Then ask Claude Code to execute the displayed MCP request
```

### Method 3: Complete Workflow (Scrape + Save)

```bash
# Step 1: Ask Claude Code to scrape
# "Please scrape https://example.com and save to output.md"

# Claude Code will:
# 1. Call mcp__firecrawl__firecrawl_scrape
# 2. Save results using scrape_and_save.py
```

## Script Details

### scrape_url.py

Educational wrapper that explains the MCP workflow.

**Usage:**
```bash
python scrape_url.py https://example.com
python scrape_url.py https://example.com --format markdown --main-content
```

**Options:**
- `--format` - Output format: markdown, html, or text (default: markdown)
- `--main-content` - Extract only main content, excluding navigation

**Output:**
Displays instructions for Claude Code to execute the actual scraping.

### scrape_url_mcp.py

Generates MCP request configurations for programmatic use.

**Usage:**
```bash
# Human-readable output
python scrape_url_mcp.py https://example.com

# JSON output for automation
python scrape_url_mcp.py https://example.com --json
```

**Options:**
- `--no-main-content` - Include all content (navigation, sidebars, etc.)
- `--json` - Output request as JSON

**Example JSON Output:**
```json
{
  "tool": "mcp__firecrawl__firecrawl_scrape",
  "parameters": {
    "url": "https://example.com",
    "formats": ["markdown"],
    "onlyMainContent": true,
    "maxAge": 172800000
  }
}
```

### scrape_and_save.py

Saves scraped content to files with metadata headers.

**Usage:**
```bash
# Save content from stdin
echo "# Content" | python scrape_and_save.py output.md

# Save with URL metadata
echo "# Content" | python scrape_and_save.py output.md --url https://example.com

# Read from file
python scrape_and_save.py output.md --url https://example.com < content.md
```

**Options:**
- `--url` - Source URL (adds metadata header)
- `--stdin` - Explicitly read from stdin

**Output File Format:**
```markdown
---
Source URL: https://example.com
Scraped: 2025-10-24 14:30:00
Tool: Firecrawl MCP
---

[Scraped content here]
```

## Firecrawl MCP Features

The underlying `mcp__firecrawl__firecrawl_scrape` tool provides:

### Performance Optimization
- **Caching**: 48-hour cache (maxAge: 172800000ms) for 500% faster scrapes
- **Parallel Processing**: Can scrape multiple URLs simultaneously
- **Smart Timeouts**: Handles slow-loading pages gracefully

### Content Extraction
- **Main Content Only**: Removes navigation, ads, sidebars
- **Multiple Formats**: Markdown, HTML, raw HTML, links, summary
- **Clean Output**: Properly formatted markdown with preserved structure

### Advanced Options

```python
# Full parameter set for mcp__firecrawl__firecrawl_scrape
{
    "url": "https://example.com",
    "formats": ["markdown"],           # Output formats
    "onlyMainContent": true,           # Extract main content only
    "maxAge": 172800000,               # Cache duration (48h)
    "waitFor": 5000,                   # Wait for JS to load (ms)
    "actions": [],                     # Browser actions (click, scroll, etc.)
    "includeTags": [],                 # Include specific HTML tags
    "excludeTags": [],                 # Exclude specific HTML tags
    "removeBase64Images": false        # Strip base64 images
}
```

## Common Use Cases

### 1. Scrape News Article
```bash
# Ask Claude Code:
"Scrape this article: https://news.ycombinator.com/item?id=12345
and save to articles/hn_12345.md"
```

### 2. Scrape Multiple Pages
```bash
# Create a list of URLs
cat << EOF > urls.txt
https://example.com/page1
https://example.com/page2
https://example.com/page3
EOF

# Ask Claude Code:
"Please scrape all URLs from urls.txt and save each to a separate markdown file"
```

### 3. Extract Main Content Only
```bash
# Ask Claude Code:
"Scrape https://blog.example.com/post with only main content,
exclude navigation and ads"
```

### 4. Scrape with JavaScript Rendering
```bash
# Ask Claude Code:
"Scrape https://spa-app.com with 5 second wait for JavaScript to load"
```

## Integration Examples

### With Lead Generation System

```python
# In your lead generation code
import subprocess
import json

def scrape_company_website(url: str) -> str:
    """Scrape company website using Claude Code + Firecrawl."""
    # Generate MCP request
    result = subprocess.run(
        ['python', 'scrape_url_mcp.py', url, '--json'],
        capture_output=True,
        text=True
    )

    request = json.loads(result.stdout)

    # Note: Actual scraping requires Claude Code with MCP access
    # This demonstrates the request structure
    return request
```

### With Sales Intelligence

```python
# Add to sales_intelligence_research.py
def enrich_with_website_data(company_name: str, website: str) -> dict:
    """Enrich company data with scraped website content."""
    # Ask Claude Code to scrape and analyze
    # "Please scrape {website} and extract:
    #  - Company description
    #  - Key products/services
    #  - Contact information
    #  - Recent news/updates"
    pass
```

## Error Handling

The scripts include comprehensive error handling:

### URL Validation
```python
# Invalid URL formats are caught early
python scrape_url_mcp.py invalid-url
# Error: Invalid URL format: invalid-url
# URL must include http:// or https://
```

### Network Errors
- Connection timeouts: Handled by Firecrawl with retries
- DNS failures: Reported with clear error messages
- SSL errors: Can be bypassed with skipTlsVerification option

### Content Errors
- Empty pages: Detected and reported
- JavaScript errors: Logged for debugging
- Rate limiting: Respects robots.txt and rate limits

## Performance Tips

1. **Use Caching**: Default 48-hour cache provides 500% speedup
2. **Batch Requests**: Scrape multiple URLs in parallel
3. **Main Content Only**: Reduces processing time and output size
4. **Appropriate Timeouts**: Adjust waitFor based on site complexity

## Troubleshooting

### "This script requires Firecrawl MCP access"
- These scripts are designed to work through Claude Code
- Don't run them directly expecting scraping to work
- Ask Claude Code to execute the scraping operations

### "Invalid URL format"
- Ensure URL includes http:// or https://
- Check for typos in the URL
- Validate URL structure

### "Connection timeout"
- Check internet connection
- Try increasing waitFor parameter
- Verify the website is accessible

### Empty or incomplete content
- Try disabling "main content only" mode
- Increase waitFor for JavaScript-heavy sites
- Check if site requires authentication

## Best Practices

1. **Respect robots.txt**: Firecrawl honors robots.txt directives
2. **Rate Limiting**: Don't scrape too aggressively
3. **Cache Wisely**: Use maxAge for frequently accessed pages
4. **Error Recovery**: Handle failures gracefully in production code
5. **Content Validation**: Verify scraped content meets expectations

## Advanced Usage

### Custom Browser Actions

```python
# Ask Claude Code to scrape with actions:
"Please scrape https://example.com with these actions:
- Wait 2 seconds
- Click on 'Load More' button
- Scroll down to bottom
- Take screenshot"
```

### Extract Structured Data

```python
# Ask Claude Code to extract specific data:
"Scrape https://company.com and extract:
- Company name from title
- All product names from lists
- Contact email addresses
- Social media links"
```

### Monitor Page Changes

```python
# Set up monitoring workflow:
"Scrape https://competitor.com every 24 hours
and alert me when content changes"
```

## Support

For issues or questions:
1. Check script help: `python scrape_url_mcp.py --help`
2. Review Firecrawl MCP documentation
3. Test with Claude Code directly: "Please scrape [URL]"
4. Check network connectivity and URL accessibility

## License

Part of the Lead-Generation project.

## Changelog

### 2025-10-24
- Initial release
- Added scrape_url.py educational wrapper
- Added scrape_url_mcp.py request generator
- Added scrape_and_save.py content saver
- Comprehensive documentation and examples
