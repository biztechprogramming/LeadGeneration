#!/usr/bin/env python3
"""
Website Scraper - Save to File

A companion script that handles the scraped content after Claude Code
retrieves it using Firecrawl MCP.

Usage:
    # Step 1: Ask Claude Code to scrape
    # Step 2: Claude will call this script with the content
    echo "markdown content" | python scrape_and_save.py output.md

    # Or save scraped content directly:
    python scrape_and_save.py output.md --url https://example.com

This demonstrates the complete workflow:
1. User requests URL scraping
2. Claude Code calls mcp__firecrawl__firecrawl_scrape
3. Content is saved using this script
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime
from typing import Optional


def save_content(content: str, output_file: Path, url: Optional[str] = None) -> None:
    """
    Save scraped content to file with metadata.

    Args:
        content: Markdown content to save
        output_file: Path to output file
        url: Source URL (optional, for metadata)
    """
    # Create parent directory if needed
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Add metadata header if URL provided
    if url:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        header = f"""---
Source URL: {url}
Scraped: {timestamp}
Tool: Firecrawl MCP
---

"""
        content = header + content

    # Write content
    output_file.write_text(content, encoding='utf-8')

    # Report success
    file_size = output_file.stat().st_size
    print(f"✓ Content saved to: {output_file}")
    print(f"✓ File size: {file_size:,} bytes")
    if url:
        print(f"✓ Source URL: {url}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Save scraped website content to file",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Save content from stdin
    echo "# Content" | python scrape_and_save.py output.md

    # Save with URL metadata
    python scrape_and_save.py output.md --url https://example.com < content.md

    # Specify custom output directory
    python scrape_and_save.py scraped_content/example.md --url https://example.com

This script is typically called by Claude Code after scraping with Firecrawl MCP.
        """
    )

    parser.add_argument(
        'output',
        type=Path,
        help='Output file path (e.g., output.md)'
    )

    parser.add_argument(
        '--url',
        type=str,
        help='Source URL (for metadata header)'
    )

    parser.add_argument(
        '--stdin',
        action='store_true',
        help='Read content from stdin (default if piped)'
    )

    args = parser.parse_args()

    # Check if content is piped or if stdin should be read
    if args.stdin or not sys.stdin.isatty():
        try:
            content = sys.stdin.read().strip()
            if not content:
                print("Error: No content provided via stdin", file=sys.stderr)
                sys.exit(1)
        except Exception as e:
            print(f"Error reading from stdin: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print("Error: No content provided. Please pipe content or use --stdin", file=sys.stderr)
        print("\nUsage examples:", file=sys.stderr)
        print("  echo 'content' | python scrape_and_save.py output.md", file=sys.stderr)
        print("  python scrape_and_save.py output.md --url URL < content.md", file=sys.stderr)
        sys.exit(1)

    # Save content
    try:
        save_content(content, args.output, args.url)
    except Exception as e:
        print(f"Error saving content: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
