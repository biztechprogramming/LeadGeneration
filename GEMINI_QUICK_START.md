# Gemini + Cerebras Quick Start

## 🚀 Quick Setup (30 seconds)

```bash
# 1. Install Gemini CLI
npm install -g @google/generative-ai-cli

# 2. Add your Cerebras API key to .env
echo "CEREBRAS_API_KEY=your-key-here" >> .env

# 3. Test it!
./gemini-cerebras.sh "Hello, Cerebras!"
```

## 📝 Common Commands

```bash
# Single prompt
./gemini-cerebras.sh "Your question here"

# Interactive chat
./gemini-cerebras.sh --chat

# Process a file
./gemini-cerebras.sh --file input.txt

# Get help
./gemini-cerebras.sh --help
```

## 💡 Quick Examples

### Code Generation
```bash
./gemini-cerebras.sh "Write a Python function to calculate Fibonacci numbers"
```

### Company Research
```bash
./gemini-cerebras.sh "Find contact information for tech startups in Austin, Texas"
```

### Data Analysis
```bash
./gemini-cerebras.sh "Analyze this CSV data and find trends: $(cat data.csv)"
```

### Email Drafting
```bash
./gemini-cerebras.sh "Write a professional cold email for B2B SaaS outreach"
```

## 🔧 Configuration

Edit `.geminirc` to customize:
- Model selection
- Temperature (creativity)
- Max tokens (response length)
- Timeout and retry settings

## 📚 Full Documentation

See `GEMINI_CEREBRAS_SETUP.md` for complete guide.

## ⚡ Why Use This?

- **Speed**: 1800+ tokens/second
- **Cost**: $0.60 per million tokens (in/out)
- **Quality**: Llama 3.3 70B performance
- **Easy**: Standard CLI interface

---

**Happy prompting! 🎉**
