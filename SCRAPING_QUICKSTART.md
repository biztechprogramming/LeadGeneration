# Firecrawl Web Scraping - Quick Start Guide

## TL;DR - The Easiest Way

Just ask Claude Code directly:

```
"Please scrape https://example.com and save to output.md"
```

Done! Claude Code handles everything automatically.

---

## Three Scripts, One Purpose

### 1. scrape_url.py
**Purpose**: Educational - explains the workflow
**Use When**: Learning how Firecrawl MCP works

```bash
python scrape_url.py https://example.com
```

### 2. scrape_url_mcp.py
**Purpose**: Generate MCP request configs
**Use When**: Need programmatic access or JSON output

```bash
# Human-readable instructions
python scrape_url_mcp.py https://example.com

# JSON for automation
python scrape_url_mcp.py https://example.com --json
```

### 3. scrape_and_save.py
**Purpose**: Save scraped content to files
**Use When**: Post-processing scraped data

```bash
echo "content" | python scrape_and_save.py output.md --url https://example.com
```

---

## Real Examples

### Example 1: Simple Scrape
```
Ask Claude Code: "Scrape https://news.ycombinator.com"
```

### Example 2: Scrape and Save
```
Ask Claude Code: "Scrape https://example.com and save to scraped/example.md"
```

### Example 3: Multiple URLs
```
Ask Claude Code: "Scrape these URLs and save each to separate files:
- https://site1.com
- https://site2.com
- https://site3.com"
```

### Example 4: Extract Main Content Only
```
Ask Claude Code: "Scrape https://blog.com/article but only the main content,
no navigation or ads"
```

---

## How It Actually Works

```
You Request → Claude Code → Firecrawl MCP → Website
                     ↓
              Markdown Content
                     ↓
              Save to File (optional)
```

**Behind the scenes:**
1. Claude Code calls `mcp__firecrawl__firecrawl_scrape`
2. Firecrawl fetches and converts to markdown
3. Content returned to Claude Code
4. Claude Code displays or saves the content

---

## Key Features

- **Fast**: 48-hour cache = 500% speedup on repeated scrapes
- **Clean**: Removes navigation, ads, sidebars automatically
- **Smart**: Handles JavaScript-heavy sites
- **Reliable**: Retries on failures, respects rate limits

---

## Common Patterns

### For Lead Generation
```
"Scrape this company website and extract:
- Company description
- Products/services
- Contact information"
```

### For Research
```
"Scrape these 10 competitor websites and
summarize their pricing pages"
```

### For Monitoring
```
"Scrape this page and compare with the version
I scraped yesterday"
```

---

## Troubleshooting

**Problem**: "This script requires Firecrawl MCP access"
**Solution**: Don't run scripts directly - ask Claude Code to scrape

**Problem**: URL not scraping
**Solution**: Ensure URL starts with http:// or https://

**Problem**: Missing content
**Solution**: Try disabling "main content only" or increase wait time

---

## Pro Tips

1. **Use caching**: Default 48-hour cache is enabled automatically
2. **Main content only**: Enabled by default, cleaner output
3. **Batch scraping**: Ask Claude Code to scrape multiple URLs at once
4. **Save important scrapes**: Use `scrape_and_save.py` for persistence

---

## Remember

These scripts are **wrappers** for Claude Code + Firecrawl MCP.
**Don't run them directly expecting scraping to work.**
Instead: **Ask Claude Code to do the scraping.**

---

## Need More Details?

See full documentation: `SCRAPING_README.md`

---

## Examples You Can Try Right Now

```
1. "Scrape https://example.com"
2. "Scrape https://news.ycombinator.com and show me the top stories"
3. "Scrape https://python.org and save to python_homepage.md"
4. "Generate a scraping request for https://github.com using scrape_url_mcp.py"
```

**That's it! Start scraping! 🚀**
