# Sales Intelligence Research - Quick Start

## ⚡ 2 Steps to Sales Intelligence Reports

**No API key needed!** Automatically uses your Claude Code OAuth token.

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Test on 3 Companies
```bash
python test_sales_intelligence.py
```

This creates 9 files in `test_reports/`:
- 3 companies × 3 files each (CONTACTS, PAIN_POINTS, CALL_PREP)

### 3. Process All 122 Companies (Optional)
```bash
# Option A: All at once (6-10 hours)
python sales_intelligence_research.py

# Option B: In batches (RECOMMENDED)
python sales_intelligence_research.py --limit 20 --start 0
python sales_intelligence_research.py --limit 20 --start 20
python sales_intelligence_research.py --limit 20 --start 40
# ... continue until all 122 are done
```

## 📁 Output

Files are created in `sales_intelligence_reports/`:
```
Triangle_Manufacturing_Co_Inc_CONTACTS.md
Triangle_Manufacturing_Co_Inc_PAIN_POINTS.md
Triangle_Manufacturing_Co_Inc_CALL_PREP.md
Rockleigh_Industries_Inc_CONTACTS.md
Rockleigh_Industries_Inc_PAIN_POINTS.md
...
```

## 💡 Pro Tips

- **No API Key Needed**: Uses Claude Code OAuth automatically
- **Batch Processing**: Process 20-30 at a time for best results
- **Resume Anytime**: Use `--start N` to resume from company N
- **Check Progress**: Review `_batch_summary.json` for status

## 📖 Full Documentation

See `SALES_INTELLIGENCE_README.md` for complete guide.

---

**That's it!** You're ready to generate sales intelligence reports. 🚀
