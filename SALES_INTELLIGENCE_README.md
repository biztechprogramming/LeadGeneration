# Sales Intelligence Research System

Automated AI-powered sales intelligence research that generates comprehensive company briefings from your Google Maps lead list.

## 🎯 What It Does

For each company in your `google_maps_leads.csv`, this system automatically generates **3 detailed markdown files**:

1. **`[Company]_CONTACTS.md`** - Contact & Org Chart Intelligence
   - Key decision-makers and influencers
   - Inferred email formats
   - Organizational structure insights
   - Growth signals from hiring patterns

2. **`[Company]_PAIN_POINTS.md`** - Pain Points & Strategic Analysis
   - 3-5 specific, evidence-based pain points
   - Strategic sales thesis
   - Competitive intelligence clues
   - Technology stack insights

3. **`[Company]_CALL_PREP.md`** - Call Prep & Conversation Starters
   - Recent company news and developments
   - High-value discovery questions
   - Proven conversation starters
   - Objection handling frameworks

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Install required packages
pip install -r requirements.txt
```

**Note**: No API key needed! The system uses Claude Code's built-in OAuth token automatically.

### 2. Test on Sample Companies (RECOMMENDED)

```bash
# Process first 3 companies as a test
python test_sales_intelligence.py
```

This will:
- Process the first 3 companies
- Create files in `test_reports/` directory
- Allow you to verify output quality before full run

### 3. Run Full Batch Processing

```bash
# Process ALL 122 companies
python sales_intelligence_research.py

# Or process in batches (recommended for large lists)
python sales_intelligence_research.py --limit 20 --start 0
python sales_intelligence_research.py --limit 20 --start 20
python sales_intelligence_research.py --limit 20 --start 40
# ... etc
```

## 📊 Command Line Options

```bash
python sales_intelligence_research.py [OPTIONS]

Options:
  --csv PATH          Path to CSV file (default: google_maps_leads.csv)
  --output DIR        Output directory (default: sales_intelligence_reports)
  --limit N           Process only N companies (useful for testing)
  --start N           Start from company N (0-based index)
```

### Usage Examples

```bash
# Test with first 5 companies
python sales_intelligence_research.py --limit 5

# Process companies 10-19
python sales_intelligence_research.py --limit 10 --start 10

# Use different input/output paths
python sales_intelligence_research.py --csv my_leads.csv --output my_reports

# Full batch (all 122 companies)
python sales_intelligence_research.py
```

## 📁 Output Structure

```
sales_intelligence_reports/
├── Triangle_Manufacturing_Co_Inc_CONTACTS.md
├── Triangle_Manufacturing_Co_Inc_PAIN_POINTS.md
├── Triangle_Manufacturing_Co_Inc_CALL_PREP.md
├── Rockleigh_Industries_Inc_CONTACTS.md
├── Rockleigh_Industries_Inc_PAIN_POINTS.md
├── Rockleigh_Industries_Inc_CALL_PREP.md
├── ...
└── _batch_summary.json    # Processing summary and statistics
```

## 🔍 How It Works

### 1. **Data Loading**
- Reads companies from `google_maps_leads.csv`
- Extracts: Company Name, Website, Address, Phone

### 2. **AI Analysis**
- Sends comprehensive research prompt to Claude AI
- Analyzes company website, industry, location
- Generates evidence-based intelligence

### 3. **Report Generation**
- Parses AI output using delimiter tags
- Creates 3 separate markdown files per company
- Saves batch summary as JSON

### 4. **Rate Limiting**
- 2-second delay between companies
- Prevents API rate limit issues
- Can pause/resume with `--start` flag

## 🎯 Best Practices

### Before Full Run

1. **Test First**: Always run `test_sales_intelligence.py` to verify output quality
2. **Review Samples**: Check the first few reports manually
3. **Adjust Prompt**: Edit prompt in `sales_intelligence_research.py` if needed

### During Batch Processing

1. **Process in Batches**: Use `--limit 20` for manageable chunks
2. **Monitor Progress**: Watch console output for errors
3. **Check Summary**: Review `_batch_summary.json` after each batch

### After Processing

1. **Review Quality**: Spot-check reports for accuracy
2. **Customize**: Edit reports as needed for your sales process
3. **CRM Import**: Use markdown files or convert to your CRM format

## 💡 Pro Tips

### Handling Missing Websites

For companies without websites, the AI will:
- Make inferences from company name and industry
- Use address/location context
- Provide general manufacturing industry insights
- Mark all data as "inferred" for transparency

### Improving Output Quality

To customize the analysis, edit the prompt in `sales_intelligence_research.py`:

```python
def build_research_prompt(self, company: Dict[str, str]) -> str:
    # Edit this method to customize the AI prompt
    # Add your product/service details
    # Adjust industry-specific pain points
    # Customize conversation starters
```

### Processing Large Lists

For 122 companies:
- **Recommended**: Process in batches of 20-30
- **Estimated Time**: ~3-5 minutes per company
- **Total Time**: 6-10 hours for full list
- **Cost**: ~$0.50-$1.00 per company (Claude Sonnet 4.5 rates)

### Resume After Interruption

```bash
# If processing stops at company 50
python sales_intelligence_research.py --start 50

# Check _batch_summary.json to see last processed company
```

## 🐛 Troubleshooting

### Rate Limit Errors

- Increase delay in `process_company()` method
- Process smaller batches (`--limit 10`)
- Wait 1 minute between batches

### Missing Files for Some Companies

Check `_batch_summary.json`:
```json
{
  "results": [
    {
      "company": "Example Co",
      "success": false,
      "error": "Error message here"
    }
  ]
}
```

Re-run failed companies:
```bash
# Get failed company indices from summary.json
python sales_intelligence_research.py --limit 1 --start 42
```

### Poor Quality Output

1. **Check website availability**: Some companies may have no website
2. **Adjust AI prompt**: Add more specific industry context
3. **Increase max_tokens**: Edit `max_tokens=8000` to `max_tokens=12000`

## 📈 Next Steps

1. **Run the test** to verify everything works
2. **Review and customize** the AI prompt if needed (edit `build_research_prompt()` method)
3. **Process in batches** to manage the 122 companies efficiently

### Optional Enhancements

- **CRM Integration**: Convert markdown to Salesforce/HubSpot CSV format
- **Email Finder**: Integrate Hunter.io to verify email addresses
- **LinkedIn Data**: Add company page scraping for employee insights
- **Firecrawl Integration**: Enhanced website scraping for better data quality

## 📝 Sample Output

### Example: Triangle Manufacturing Co., Inc.

**CONTACTS.md**:
```markdown
| Name | Title | Buying Role | Email Format | Source |
|------|-------|-------------|--------------|--------|
| John Smith | CEO | Decision Maker | jsmith@trianglemfg.com | About Page |
| Sarah Johnson | VP Operations | Influencer | sjohnson@trianglemfg.com | Team Page |
```

**PAIN_POINTS.md**:
```markdown
1. **Outdated Production Systems**: Career page mentions "modernizing legacy equipment"
2. **Supply Chain Visibility**: Blog posts discuss inventory tracking challenges
3. **Quality Control Automation**: Multiple QA engineer job postings
```

**CALL_PREP.md**:
```markdown
**High-Value Question**: "I noticed the recent VP of Operations hire. What's the biggest operational bottleneck driving that change?"

**Bold Statement**: "Companies in precision manufacturing typically see 40% reduction in defects when automating quality control."
```

## 🤝 Support

For issues or questions:
1. Check `_batch_summary.json` for error details
2. Review console output for specific errors
3. Test with `--limit 1` to isolate issues

---

**Happy Selling!** 🚀

The system uses Claude Code's OAuth token automatically - no API key setup required!
