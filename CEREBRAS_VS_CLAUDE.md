# Cerebras vs Claude Code - Comparison Guide

You now have **two versions** of the Sales Intelligence Research System:

## 🚀 Option 1: Claude Code CLI (sales_intelligence_research.py)

### Pros
- ✅ Uses your existing Claude Code subscription
- ✅ Best AI quality (Claude Sonnet 4.5)
- ✅ No additional API key needed
- ✅ Integrated with Claude Code ecosystem

### Cons
- ⏱️ Slower (~3-5 min per company)
- 💰 Uses your Claude Code quota

### Setup
```bash
# No setup needed - uses claude CLI automatically
python test_sales_intelligence.py
```

### When to Use
- When you want highest quality analysis
- When you're already using Claude Code
- For important/complex companies
- When speed isn't critical

---

## ⚡ Option 2: Cerebras API (sales_intelligence_cerebras.py)

### Pros
- ⚡ **Ultra-fast** (~10-30 seconds per company)
- 💵 **Very cheap** (~$0.10 per million tokens)
- 🔥 Can process all 122 companies in ~10-20 minutes
- 📊 Great for batch processing

### Cons
- 🔑 Requires separate API key
- 🤖 Different AI model (Llama 3.3 70B - still very good)
- 💳 Pay-per-use pricing

### Setup
```bash
# 1. Get API key from https://cloud.cerebras.ai/
# 2. Set environment variable
export CEREBRAS_API_KEY='your-key-here'

# 3. Test
python test_cerebras.py
```

### When to Use
- When you need to process all 122 companies quickly
- For initial research pass (then refine with Claude)
- When you want to save Claude Code quota
- For high-volume processing

---

## 📊 Performance Comparison

| Metric | Claude Code | Cerebras |
|--------|------------|----------|
| **Speed** | 3-5 min/company | 10-30 sec/company |
| **Quality** | Excellent (Sonnet 4.5) | Very Good (Llama 3.3 70B) |
| **Cost** | Claude subscription | ~$0.10 per 1M tokens |
| **Total Time (122 companies)** | ~6-10 hours | ~10-20 minutes |
| **Setup** | None (uses CLI) | API key required |

---

## 🎯 Recommended Workflow

### Two-Pass Approach (Best of Both Worlds)

**Pass 1: Cerebras (Fast Initial Research)**
```bash
# Process all 122 companies quickly
python sales_intelligence_cerebras.py
```
- Get initial intelligence on all companies
- Identify top prospects
- Takes ~20 minutes total

**Pass 2: Claude (Deep Dive on Top Prospects)**
```bash
# Re-analyze top 20 companies with Claude for highest quality
python sales_intelligence_research.py --limit 20
```
- Get premium analysis on best opportunities
- Refine messaging and positioning
- Takes ~1-2 hours

---

## 💰 Cost Breakdown

### Cerebras Pricing
- Model: `llama-3.3-70b`
- Input: ~$0.10 per 1M tokens
- Output: ~$0.10 per 1M tokens
- **Total for 122 companies**: ~$1-3

### Claude Code
- Included in subscription
- Usage counts against quota
- **Total for 122 companies**: Part of subscription

---

## 🚀 Quick Start Commands

### Test Both Systems
```bash
# Test Claude Code version
python test_sales_intelligence.py

# Test Cerebras version (after setting API key)
python test_cerebras.py
```

### Full Production Runs
```bash
# Cerebras: Fast batch processing
python sales_intelligence_cerebras.py

# Claude Code: High-quality analysis
python sales_intelligence_research.py --limit 20
```

### Batch Processing (Either System)
```bash
# Process in chunks of 20
python sales_intelligence_cerebras.py --limit 20 --start 0
python sales_intelligence_cerebras.py --limit 20 --start 20
python sales_intelligence_cerebras.py --limit 20 --start 40
# ... continue
```

---

## 📁 Output Differences

Both systems generate the **same file structure**:
```
sales_intelligence_reports/          # Claude Code output
sales_intelligence_reports_cerebras/  # Cerebras output

Each contains:
  - Company_CONTACTS.md
  - Company_PAIN_POINTS.md
  - Company_CALL_PREP.md
  - _batch_summary.json (or _batch_summary_cerebras.json)
```

---

## 🎓 Which Should You Use?

### Use Claude Code When:
- You want the absolute best quality
- Processing < 20 companies
- You have time (6-10 hours for all)
- You're already using Claude Code
- Premium clients/high-value deals

### Use Cerebras When:
- You need results fast (minutes vs hours)
- Processing all 122 companies
- You want to save Claude Code quota
- Initial research phase
- Volume processing

### Use Both When:
- **Cerebras first** for fast initial pass (20 min)
- **Claude second** for top prospects (2 hours)
- Best of both worlds: speed + quality

---

## 🛠️ Troubleshooting

### Claude Code Issues
```bash
# Check if claude CLI is available
claude --help

# Make sure you're logged in
claude --print "test"
```

### Cerebras Issues
```bash
# Verify API key is set
echo $CEREBRAS_API_KEY

# Test API connection
curl -X POST https://api.cerebras.ai/v1/chat/completions \
  -H "Authorization: Bearer $CEREBRAS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"llama-3.3-70b","messages":[{"role":"user","content":"test"}]}'
```

---

## 📈 Next Steps

1. **Test both systems** on 3 companies
2. **Compare output quality** - review generated files
3. **Choose your approach**:
   - Fast: Cerebras for all 122
   - Quality: Claude Code for all 122
   - Hybrid: Cerebras first pass, Claude refinement
4. **Run production batch**
5. **Import to CRM**

---

**Bottom Line**: Both systems work great. Choose based on your priorities:
- **Speed + Volume** → Cerebras
- **Quality + Integration** → Claude Code
- **Best Results** → Use both!
