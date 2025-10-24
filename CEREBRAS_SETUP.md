# Cerebras API Setup Guide

## Quick Setup (2 minutes)

### Step 1: Get API Key
1. Go to https://cloud.cerebras.ai/
2. Sign up (free tier available)
3. Navigate to **API Keys** section
4. Click **Create API Key**
5. Copy the key (starts with `csk-...`)

### Step 2: Configure Locally (Choose One)

#### Option A: .env File (Recommended - No exports needed!)
```bash
# 1. Copy the example file
cp .env.example .env

# 2. Edit the file and add your key
nano .env
# or
code .env

# Change this line:
CEREBRAS_API_KEY=your-cerebras-api-key-here

# To your actual key:
CEREBRAS_API_KEY=csk-xxxxxxxxxxxxxxxxxxxxxx
```

**That's it!** The key is stored permanently in the project.

#### Option B: Environment Variable (Traditional)
```bash
# For current session only
export CEREBRAS_API_KEY='csk-xxxxxxxxxxxxxxxxxxxxxx'

# Or add to ~/.bashrc for persistence
echo 'export CEREBRAS_API_KEY="csk-xxxxxxxxxxxxxxxxxxxxxx"' >> ~/.bashrc
source ~/.bashrc
```

### Step 3: Verify Setup
```bash
# This should work without errors
python test_cerebras.py
```

## ✅ Done!

The `.env` file is automatically loaded by the script, so you never have to remember to export the key again.

## Security Notes

- ✅ `.env` is in `.gitignore` - your key won't be committed to git
- ✅ `.env.example` is tracked - others can see the template
- ✅ Keep your API key private - never share it

## Troubleshooting

### "CEREBRAS_API_KEY not set" Error
```bash
# Check if .env exists
ls -la .env

# Check if key is in the file
cat .env

# Make sure there are no extra spaces
CEREBRAS_API_KEY=csk-xxx  # ✅ Good
CEREBRAS_API_KEY = csk-xxx  # ❌ Bad (spaces around =)
```

### Still Not Working?
Try the export method as a fallback:
```bash
export CEREBRAS_API_KEY='csk-xxxxxxxxxxxxxxxxxxxxxx'
python test_cerebras.py
```

## Cost Information

Cerebras is **very affordable**:
- Free tier: Generous limits for testing
- Paid tier: ~$0.10 per million tokens
- **Your 122 companies**: ~$1-3 total cost

## Next Steps

Once setup is complete:
```bash
# Test on 3 companies
python test_cerebras.py

# Process all 122 companies
python sales_intelligence_cerebras.py
```

---

**Pro Tip**: Keep both `.env.example` (template) and `.env` (your actual key) in the project. This way you can easily recreate the setup on other machines.
