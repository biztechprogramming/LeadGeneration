#!/bin/bash

# gemini-cerebras.sh
# Wrapper script to use Gemini CLI with Cerebras API
# Usage: ./gemini-cerebras.sh "your prompt here"

set -euo pipefail

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Error handling function
error_exit() {
    echo -e "${RED}Error: $1${NC}" >&2
    exit 1
}

# Success message function
success_msg() {
    echo -e "${GREEN}$1${NC}"
}

# Warning message function
warning_msg() {
    echo -e "${YELLOW}$1${NC}"
}

# Check if .env file exists
if [[ ! -f "${SCRIPT_DIR}/.env" ]]; then
    error_exit ".env file not found in ${SCRIPT_DIR}. Please create it from .env.example"
fi

# Load environment variables from .env
set -a
source "${SCRIPT_DIR}/.env"
set +a

# Check if CEREBRAS_API_KEY is set
if [[ -z "${CEREBRAS_API_KEY:-}" ]]; then
    error_exit "CEREBRAS_API_KEY not found in .env file"
fi

# Export as GEMINI_API_KEY for Gemini CLI
export GEMINI_API_KEY="${CEREBRAS_API_KEY}"

# Check if gemini CLI is installed
if ! command -v gemini &> /dev/null; then
    error_exit "Gemini CLI not found. Install it with: npm install -g @google/generative-ai-cli"
fi

# Check if .geminirc exists
if [[ ! -f "${SCRIPT_DIR}/.geminirc" ]]; then
    warning_msg ".geminirc not found. Using default configuration."
fi

# Check if prompt is provided
if [[ $# -eq 0 ]]; then
    error_exit "Usage: $0 \"your prompt here\"\n       Or: $0 --chat    (for interactive mode)\n       Or: $0 --file input.txt    (for file input)"
fi

# Parse command line arguments
case "$1" in
    --chat|-c)
        success_msg "Starting interactive chat mode with Cerebras API..."
        exec gemini \
            --api-base "https://api.cerebras.ai/v1" \
            --model "llama-3.3-70b" \
            chat
        ;;
    --file|-f)
        if [[ $# -lt 2 ]]; then
            error_exit "File path required. Usage: $0 --file input.txt"
        fi
        if [[ ! -f "$2" ]]; then
            error_exit "File not found: $2"
        fi
        success_msg "Processing file: $2"
        exec gemini \
            --api-base "https://api.cerebras.ai/v1" \
            --model "llama-3.3-70b" \
            generate < "$2"
        ;;
    --help|-h)
        echo "Gemini CLI with Cerebras API - Usage Guide"
        echo ""
        echo "Usage:"
        echo "  $0 \"your prompt here\"           Send a single prompt"
        echo "  $0 --chat                        Start interactive chat mode"
        echo "  $0 --file input.txt              Process file as input"
        echo "  $0 --help                        Show this help message"
        echo ""
        echo "Environment:"
        echo "  Reads CEREBRAS_API_KEY from .env file"
        echo "  Uses configuration from .geminirc if available"
        echo ""
        echo "Examples:"
        echo "  $0 \"Explain quantum computing\""
        echo "  $0 --chat"
        echo "  $0 --file prompt.txt"
        exit 0
        ;;
    *)
        # Single prompt mode
        success_msg "Sending prompt to Cerebras API..."
        exec gemini \
            --api-base "https://api.cerebras.ai/v1" \
            --model "llama-3.3-70b" \
            generate "$@"
        ;;
esac
