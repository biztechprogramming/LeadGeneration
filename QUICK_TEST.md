# Quick Test Guide - Intelligent Research System

Get the intelligent research system running in 3 simple steps!

## Prerequisites

- Python 3.8+
- Cerebras API key (free tier available)

## 3-Step Setup

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

Required packages:
- `requests` - API communication
- `beautifulsoup4` - HTML parsing
- `csv` (built-in)
- `json` (built-in)

### Step 2: Configure API Key

**Option A: Using .env file** (recommended)
```bash
# Copy example file
cp .env.example .env

# Edit .env and add your key
# CEREBRAS_API_KEY=your-key-here
```

**Option B: Export directly**
```bash
export CEREBRAS_API_KEY="your-key-here"
```

**Get your free API key**: https://cloud.cerebras.ai/

### Step 3: Run Test

```bash
python test_intelligent_research.py
```

Or with verbose output:
```bash
python test_intelligent_research.py --verbose
```

That's it! The test will run automatically.

---

## What to Expect

### Test Suite Overview

The test script runs **6 comprehensive tests**:

1. **API Connection** - Verifies Cerebras API is responding
2. **Function Registry** - Tests function execution and missing function logging
3. **Data Accumulator** - Verifies data storage and progression
4. **AI Decision Engine** - Tests real AI analysis with Cerebras
5. **Image Collector** - Validates image detection heuristics
6. **Live Company Research** - Runs full iterative research on first company

### Expected Timeline

```
Total time: ~60-90 seconds

[0s]    Starting test suite...
[2s]    ✓ API Connection
[5s]    ✓ Function Registry
[8s]    ✓ Data Accumulator
[15s]   ✓ AI Decision Engine
[18s]   ✓ Image Collector
[20s]   Starting live research...
[30s]   → Iteration 1/3: AI analyzing...
[45s]   → Iteration 2/3: AI analyzing...
[60s]   → Iteration 3/3: AI analyzing...
[65s]   ✓ Live Company Research
[70s]   Saving test report...
[72s]   ✓ All tests complete!
```

### Expected Output

```
============================================================
INTELLIGENT RESEARCH SYSTEM - TEST SUITE
============================================================
CSV: google_maps_leads.csv
Output: test_output
Verbose: False
Max Iterations: 3
============================================================

✓ Environment configured

→ Initializing orchestrator...
✓ Orchestrator initialized

→ Running test suite...

============================================================
TEST 1: Cerebras API Connection
============================================================
✓ Cerebras API is responding correctly

============================================================
TEST 2: Function Registry & Missing Function Logging
============================================================

→ Testing registered function (save_contact)...
  ✓ Registered function executed successfully

→ Testing missing function (nonexistent_function)...
  ✓ Missing function correctly logged

→ Verifying missing functions log file...
  ✓ Missing functions log exists
  → Contains 1 entries

✓ Function registry test PASSED

============================================================
TEST 3: Data Accumulator & Progression
============================================================

→ Testing data accumulation...
  ✓ contacts: True
  ✓ pain_points: True
  ✓ tech_stack: True
  ✓ news: True
  ✓ sources: True
  ✓ iterations: True

✓ Data accumulator test PASSED

============================================================
TEST 4: AI Decision Engine
============================================================

→ Sending data to AI for analysis...
  Company: Triangle Manufacturing Co., Inc.
  Current sources: 1

→ AI Decision received:
  Status: continue
  Actions: 2
  Next steps: 3
  Relevant data: 4

✓ AI decision engine test PASSED

============================================================
TEST 5: Image Detection & Collection
============================================================

→ Testing image detection heuristics...
  ✓ 'team/john.jpg' + 'Team member': True (expected True)
  ✓ 'logo.png' + 'Company Logo': False (expected False)
  ✓ 'headshot-ceo.jpg' + 'CEO Portrait': True (expected True)
  ✓ 'product.jpg' + 'Product Image': False (expected False)
  ✓ 'staff-photo.jpg' + 'Staff member': True (expected True)

  → Passed 5/5 detection tests

✓ Image collector test PASSED

============================================================
TEST 6: Live Company Research (First Company from CSV)
============================================================

→ Company: Triangle Manufacturing Co., Inc.
→ Website: trianglemfg.com
→ Max iterations: 3

→ Starting iterative research...

============================================================
Researching: Triangle Manufacturing Co., Inc.
============================================================

--- Iteration 1/3 ---
  → Consulting AI for analysis...
  📊 Relevant data identified: 3 items
    - Manufacturing company in New Jersey
    - Likely B2B operations
    - Contact information available
  ⚙️  Executing 1 action(s)...
    ✓ Saved: industry = Manufacturing
  🔍 Exploring 2 new source(s)...
    → Exploring: /about
      Reason: Find company background and team
    ⚠ Missing function: explore_page (logged)

=== Data Summary ===
Contacts: 0
Pain Points: 0
Technologies: 0
News Items: 0
Images: 0
Sources Explored: 1
Iterations: 1

--- Iteration 2/3 ---
  → Consulting AI for analysis...
  📊 Relevant data identified: 2 items
    - Address indicates suburban location
    - Phone area code 201 (North Jersey)
  ⚙️  Executing 2 action(s)...
    ✓ Saved pain point: Limited online presence...
    ✓ Saved: target_persona = Manufacturing Operations Manager
  🔍 Exploring 1 new source(s)...
    ⚠ Missing function: search_linkedin (logged)

=== Data Summary ===
Contacts: 0
Pain Points: 1
Technologies: 0
News Items: 0
Images: 0
Sources Explored: 1
Iterations: 2

--- Iteration 3/3 ---
  → Consulting AI for analysis...
  📊 Relevant data identified: 1 items
    - Basic research complete

  ✓ AI determined research is complete

============================================================
Research Complete: Triangle Manufacturing Co., Inc.
=== Data Summary ===
Contacts: 0
Pain Points: 1
Technologies: 0
News Items: 0
Images: 0
Sources Explored: 1
Iterations: 3
============================================================

→ Research completed! Analyzing results...

→ Results Summary:
  • Iterations Completed: 3
  • Contacts Found: 0
  • Pain Points Found: 1
  • Technologies Found: 0
  • News Found: 0
  • Images Collected: 0
  • Sources Explored: 1

📄 Report saved: test_output/Triangle_Manufacturing_Co_Inc_INTELLIGENT_RESEARCH.md

✓ Live company research test PASSED

📄 Full test report saved: test_output/test_report.json

============================================================
TEST SUMMARY
============================================================

Total Tests: 6
Passed: 6 ✓
Failed: 0 ✗

✓ Passed Tests:
  • api_connection
  • function_registry
  • data_accumulator
  • ai_decision_engine
  • image_collector
  • live_company_research

============================================================

AI Decisions Made: 3
Functions Executed: 4
Missing Functions Logged: 2
Images Detected: 5

============================================================
```

---

## Verify It's Working

### 1. Check Test Report

```bash
cat test_output/test_report.json
```

Should show:
```json
{
  "start_time": "2025-01-24T10:30:00",
  "tests_passed": [
    "api_connection",
    "function_registry",
    "data_accumulator",
    "ai_decision_engine",
    "image_collector",
    "live_company_research"
  ],
  "tests_failed": [],
  "summary": {
    "total_tests": 6,
    "passed": 6,
    "failed": 0
  }
}
```

### 2. Check Generated Report

```bash
cat test_output/Triangle_Manufacturing_Co_Inc_INTELLIGENT_RESEARCH.md
```

Should contain:
- Company overview
- Contacts table (may be empty if no website scraping)
- Pain points identified
- Technology stack
- Sources explored
- Research metadata

### 3. Check Missing Functions Log

```bash
cat test_output/missing_functions.json
```

Should show functions AI suggested but aren't implemented yet:
```json
{
  "explore_page": 2,
  "search_linkedin": 1
}
```

This is **normal and expected** - it shows the system is working!

---

## Success Indicators

✅ **All 6 tests passed**
- Each test reports "PASSED"
- No fatal errors

✅ **AI is making decisions**
- See "AI Decision received" messages
- Actions and next_steps populated
- Relevant data identified

✅ **Functions are executing**
- See "✓ Saved..." messages
- Data accumulator showing counts

✅ **Missing functions logged**
- See "⚠ Missing function: ..." warnings
- Check `missing_functions.json` created

✅ **Reports generated**
- Markdown report created
- JSON test report saved
- Both files readable

---

## Troubleshooting

### "CEREBRAS_API_KEY not found"

**Fix**:
```bash
# Create .env file
echo "CEREBRAS_API_KEY=your-key-here" > .env

# Or export
export CEREBRAS_API_KEY="your-key-here"
```

### "No companies found in CSV"

**Fix**:
```bash
# Verify CSV exists
ls -l google_maps_leads.csv

# Check contents
head -3 google_maps_leads.csv
```

Expected format:
```
Title,Address,PhoneNumber,WebsiteURL
Triangle Manufacturing Co., Inc.,"25 Park Way, Upper Saddle River, NJ 07458",2018251212,trianglemfg.com
```

### "API timed out"

**Fix**:
- Check internet connection
- Retry (temporary API issue)
- Reduce iterations: `--max-iterations 2`

### Tests fail but "Missing function" warnings appear

**This is normal!** Missing function warnings are expected. The system logs functions AI suggests but aren't implemented yet. This doesn't cause test failures.

Only worry if you see:
- "✗ Test FAILED"
- "FATAL ERROR"
- Exit code 1

---

## Next Steps

### Run Full Batch Research

Once tests pass, run full research:

```bash
# Research all companies in CSV
python cerebras_intelligent_research.py --csv google_maps_leads.csv

# Or limit to first 5
python cerebras_intelligent_research.py --limit 5
```

### Customize Test Parameters

```bash
# More iterations for deeper research
python test_intelligent_research.py --max-iterations 10

# Different CSV file
python test_intelligent_research.py --csv my_leads.csv

# Different output directory
python test_intelligent_research.py --output my_test_results

# All together
python test_intelligent_research.py \
    --verbose \
    --max-iterations 5 \
    --csv my_leads.csv \
    --output my_tests
```

### Review Documentation

For deeper understanding:
- **Architecture**: See INTELLIGENT_RESEARCH_README.md
- **Comparison**: Check "Comparison with Original System" section
- **Development**: See "Contributing" and "Development Roadmap"

---

## What Makes This Intelligent?

Unlike traditional static prompting, this system:

1. **Iterates**: Doesn't stop after one analysis
2. **Adapts**: AI decides what to explore based on findings
3. **Accumulates**: Builds context across iterations
4. **Extends**: Logs missing functions for future development
5. **Collects**: Gathers images with metadata
6. **Audits**: Tracks sources and evidence

**Key Innovation**: The AI isn't just answering questions - it's **deciding what questions to ask**.

---

## Expected Costs

Using Cerebras API (llama-3.3-70b):

**Per Company**:
- 3 iterations: ~$0.005-0.010
- 10 iterations: ~$0.015-0.030

**Batch of 100 companies** (3 iterations each):
- Total: ~$0.50-1.00

**Much cheaper than OpenAI GPT-4!**

---

## Getting Help

1. **Check test report**: `test_output/test_report.json`
2. **Enable verbose**: `--verbose` flag
3. **Review docs**: INTELLIGENT_RESEARCH_README.md
4. **Check missing functions**: Normal to see these logged!

---

**Ready to research?** Run `python test_intelligent_research.py` now! 🚀
