# Gemini CLI + Cerebras API Setup Guide

## Overview

This setup allows you to use the powerful **Gemini CLI** interface with **Cerebras API's ultra-fast inference**, combining the best of both worlds:

- **Gemini CLI**: Feature-rich command-line interface with chat mode, file processing, and streaming
- **Cerebras API**: Lightning-fast inference with Llama 3.3 70B at competitive pricing

## Architecture

```
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────┐
│   Gemini CLI    │─────▶│  Wrapper Script  │─────▶│  Cerebras API   │
│   (Interface)   │      │  (gemini-cerebras)│      │  (llama-3.3-70b)│
└─────────────────┘      └──────────────────┘      └─────────────────┘
                                   │
                                   ▼
                         ┌──────────────────┐
                         │    .geminirc     │
                         │  Configuration   │
                         └──────────────────┘
```

## Prerequisites

1. **Cerebras API Key**: Get your free API key from [https://cloud.cerebras.ai/](https://cloud.cerebras.ai/)
2. **Gemini CLI**: Install the Gemini CLI tool
3. **Environment Setup**: Configure your `.env` file

## Installation

### 1. Install Gemini CLI

```bash
npm install -g @google/generative-ai-cli
```

Or with yarn:
```bash
yarn global add @google/generative-ai-cli
```

Verify installation:
```bash
gemini --version
```

### 2. Configure Environment

Copy `.env.example` to `.env` and add your Cerebras API key:

```bash
cp .env.example .env
```

Edit `.env`:
```bash
CEREBRAS_API_KEY=your-actual-cerebras-api-key-here
```

### 3. Configuration Files

The setup includes three configuration files:

#### `.geminirc` - Gemini CLI Configuration
Configures the Gemini CLI to use Cerebras API endpoint:
- API Base: `https://api.cerebras.ai/v1`
- Model: `llama-3.3-70b`
- Default parameters (temperature, max tokens, etc.)

#### `gemini-cerebras.sh` - Wrapper Script
Smart wrapper that:
- Loads your Cerebras API key from `.env`
- Exports it as `GEMINI_API_KEY` for Gemini CLI
- Configures Gemini CLI to use Cerebras endpoint
- Provides error handling and helpful messages

## Usage

### Single Prompt Mode

Send a one-off prompt:

```bash
./gemini-cerebras.sh "Explain the benefits of Llama 3.3 70B"
```

Multi-line prompts:
```bash
./gemini-cerebras.sh "Generate a Python function that:
- Accepts a list of numbers
- Returns the median value
- Includes error handling"
```

### Interactive Chat Mode

Start a continuous conversation:

```bash
./gemini-cerebras.sh --chat
```

Features in chat mode:
- Multi-turn conversations with context
- Type your prompts interactively
- Exit with `Ctrl+C` or `exit`

### File Input Mode

Process a file as input:

```bash
./gemini-cerebras.sh --file prompt.txt
```

Great for:
- Long prompts stored in files
- Batch processing
- Templated prompts

### Help

Display usage information:

```bash
./gemini-cerebras.sh --help
```

## Example Use Cases

### 1. Code Generation

```bash
./gemini-cerebras.sh "Generate a FastAPI endpoint for user authentication with JWT tokens"
```

### 2. Data Analysis

```bash
./gemini-cerebras.sh --file sales_data_prompt.txt
```

Where `sales_data_prompt.txt` contains:
```
Analyze the following sales data and provide insights:
- Total revenue
- Top performing products
- Regional trends

[Your data here]
```

### 3. Interactive Debugging

```bash
./gemini-cerebras.sh --chat
```

Then paste code snippets and ask questions interactively.

### 4. Lead Generation Research

```bash
./gemini-cerebras.sh "Research the top 10 fintech companies in Singapore and provide:
- Company name
- Website
- Key products
- Target market
- Recent funding rounds"
```

## Benefits of This Approach

### 🚀 Performance
- **Ultra-fast inference**: Cerebras delivers tokens at 1800+ tokens/second
- **Low latency**: Sub-second response times for most queries
- **Scalable**: Handles complex 70B parameter model effortlessly

### 💰 Cost-Effective
- **Competitive pricing**: $0.60 per million input tokens, $0.60 per million output tokens
- **No rate limits**: Free tier generous for testing and development
- **Better value**: Llama 3.3 70B quality at fraction of GPT-4 cost

### 🛠️ Developer Experience
- **CLI flexibility**: Full Gemini CLI feature set
- **Easy integration**: Drop-in replacement for existing workflows
- **Familiar interface**: Standard CLI patterns and flags
- **Rich features**: Chat mode, file processing, streaming

### 🔧 Flexibility
- **Model choice**: Easy to switch models in `.geminirc`
- **Parameter tuning**: Adjust temperature, max tokens, etc.
- **Environment isolation**: Project-specific configurations
- **Script customization**: Modify `gemini-cerebras.sh` for your needs

## Configuration Options

### `.geminirc` Parameters

```bash
# Model Configuration
GEMINI_MODEL=llama-3.3-70b              # Model to use

# Generation Parameters
GEMINI_TEMPERATURE=0.7                  # Creativity (0.0-2.0)
GEMINI_MAX_TOKENS=4096                  # Maximum response length

# API Configuration
GEMINI_API_BASE=https://api.cerebras.ai/v1
GEMINI_TIMEOUT=30                       # Request timeout (seconds)
GEMINI_RETRY_COUNT=3                    # Number of retries on failure
```

### Environment Variables

The wrapper script supports:
- `CEREBRAS_API_KEY`: Your Cerebras API key (required)
- `GEMINI_TEMPERATURE`: Override default temperature
- `GEMINI_MAX_TOKENS`: Override default max tokens

## Troubleshooting

### "CEREBRAS_API_KEY not found"

**Solution**: Ensure `.env` file exists and contains your API key:
```bash
echo "CEREBRAS_API_KEY=your-key-here" > .env
```

### "Gemini CLI not found"

**Solution**: Install Gemini CLI:
```bash
npm install -g @google/generative-ai-cli
```

### API Connection Errors

**Solution**: Verify your API key is valid:
```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
     https://api.cerebras.ai/v1/models
```

### Permission Denied

**Solution**: Make script executable:
```bash
chmod +x gemini-cerebras.sh
```

## Comparison: Direct API vs Gemini CLI

| Feature | Direct API (Python) | Gemini CLI Wrapper |
|---------|-------------------|-------------------|
| Setup | Multiple dependencies | Single CLI install |
| Interactive Chat | Custom implementation | Built-in |
| Streaming | Manual handling | Automatic |
| File Processing | Custom code | Built-in flag |
| Error Handling | Manual implementation | Automatic |
| Learning Curve | Python + API docs | Standard CLI patterns |
| Flexibility | Full control | CLI feature set |

## Integration with Existing Tools

### Use with Lead Generation Scripts

```bash
# Generate company research
./gemini-cerebras.sh "Research $(cat companies.txt)" > research_output.txt

# Analyze results
python analyze_research.py research_output.txt
```

### Pipe with Other Commands

```bash
# Process CSV data
cat leads.csv | ./gemini-cerebras.sh "Analyze this lead data and prioritize by potential value"

# Chain with grep
./gemini-cerebras.sh --file prompt.txt | grep -i "email"
```

### Integration in Scripts

```python
import subprocess

def query_cerebras(prompt):
    result = subprocess.run(
        ['./gemini-cerebras.sh', prompt],
        capture_output=True,
        text=True
    )
    return result.stdout
```

## Advanced Usage

### Custom Parameters

Modify `gemini-cerebras.sh` to add custom parameters:

```bash
# Add before exec gemini call
EXTRA_ARGS=""
if [[ -n "${GEMINI_TEMPERATURE:-}" ]]; then
    EXTRA_ARGS="$EXTRA_ARGS --temperature $GEMINI_TEMPERATURE"
fi

exec gemini \
    --api-base "https://api.cerebras.ai/v1" \
    --model "llama-3.3-70b" \
    $EXTRA_ARGS \
    generate "$@"
```

### Multiple Model Support

Create model-specific scripts:

```bash
# gemini-cerebras-fast.sh - Uses smaller model
exec gemini --api-base "https://api.cerebras.ai/v1" --model "llama3.1-8b" generate "$@"

# gemini-cerebras-quality.sh - Uses larger model
exec gemini --api-base "https://api.cerebras.ai/v1" --model "llama-3.3-70b" generate "$@"
```

## Security Best Practices

1. **Never commit `.env`**: Already in `.gitignore`
2. **Use environment-specific keys**: Different keys for dev/staging/prod
3. **Rotate keys regularly**: Generate new keys periodically
4. **Monitor usage**: Check Cerebras dashboard for unexpected activity
5. **Restrict access**: Limit who has access to `.env` file

## Performance Tips

1. **Adjust temperature**: Lower (0.3-0.5) for factual tasks, higher (0.7-1.0) for creative
2. **Optimize max_tokens**: Set appropriate limits to avoid unnecessary costs
3. **Batch requests**: Use file input mode for multiple prompts
4. **Cache responses**: Store frequently used outputs
5. **Monitor metrics**: Track response times and costs

## Next Steps

1. ✅ Install Gemini CLI
2. ✅ Configure `.env` with your Cerebras API key
3. ✅ Test with: `./gemini-cerebras.sh "Hello, Cerebras!"`
4. ✅ Try chat mode: `./gemini-cerebras.sh --chat`
5. ✅ Integrate into your workflows

## Resources

- **Cerebras Documentation**: [https://docs.cerebras.ai/](https://docs.cerebras.ai/)
- **Gemini CLI GitHub**: [https://github.com/google/generative-ai-cli](https://github.com/google/generative-ai-cli)
- **Llama 3.3 Model Card**: [https://huggingface.co/meta-llama/Llama-3.3-70B](https://huggingface.co/meta-llama/Llama-3.3-70B)
- **Support**: Open an issue or contact support@cerebras.ai

## Contributing

Found a bug or have a suggestion? Please:
1. Open an issue describing the problem
2. Submit a pull request with improvements
3. Share your use cases and workflows

---

**Happy prompting with Gemini CLI + Cerebras! 🚀**
