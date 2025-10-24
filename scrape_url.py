#!/usr/bin/env python3
"""
Website Scraper using Firecrawl MCP

A simple command-line tool to scrape website content and convert it to markdown.
Uses the Firecrawl MCP server for reliable web scraping.

Usage:
    python scrape_url.py <url>
    python scrape_url.py https://example.com

Author: Lead-Generation Project
"""

import sys
import argparse
from typing import Optional
from urllib.parse import urlparse


def validate_url(url: str) -> bool:
    """
    Validate URL format.

    Args:
        url: URL string to validate

    Returns:
        True if URL is valid, False otherwise
    """
    try:
        result = urlparse(url)
        return all([result.scheme in ('http', 'https'), result.netloc])
    except Exception:
        return False


def scrape_website(url: str) -> Optional[str]:
    """
    Scrape website content using Firecrawl MCP.

    Args:
        url: Website URL to scrape

    Returns:
        Scraped markdown content or None on failure
    """
    # NOTE: This script is designed to be called by Claude Code which has access
    # to the mcp__firecrawl__firecrawl_scrape tool. This script cannot directly
    # call MCP tools - it serves as a command-line wrapper for Claude Code to execute.

    print(f"Error: This script requires Firecrawl MCP access through Claude Code.", file=sys.stderr)
    print(f"Please run this script through Claude Code, not directly.", file=sys.stderr)
    return None


def main():
    """Main entry point for the scraper."""
    parser = argparse.ArgumentParser(
        description="Scrape website content and convert to markdown using Firecrawl MCP",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python scrape_url.py https://example.com
    python scrape_url.py https://news.ycombinator.com

Note: This script requires access to Firecrawl MCP server.
        """
    )

    parser.add_argument(
        'url',
        type=str,
        help='Website URL to scrape (must include http:// or https://)'
    )

    parser.add_argument(
        '--format',
        type=str,
        default='markdown',
        choices=['markdown', 'html', 'text'],
        help='Output format (default: markdown)'
    )

    parser.add_argument(
        '--main-content',
        action='store_true',
        help='Extract only main content, excluding navigation and sidebars'
    )

    args = parser.parse_args()

    # Validate URL
    if not validate_url(args.url):
        print(f"Error: Invalid URL format: {args.url}", file=sys.stderr)
        print("URL must include http:// or https://", file=sys.stderr)
        sys.exit(1)

    # Inform user about MCP requirement
    print("=" * 80)
    print("FIRECRAWL WEB SCRAPER")
    print("=" * 80)
    print(f"\nTarget URL: {args.url}")
    print(f"Format: {args.format}")
    print(f"Main content only: {args.main_content}")
    print("\nNote: This tool requires Firecrawl MCP access via Claude Code")
    print("=" * 80)
    print("\nTo use this script, please ask Claude Code to:")
    print(f"1. Call mcp__firecrawl__firecrawl_scrape with URL: {args.url}")
    print(f"2. Use formats: ['{args.format}']")
    if args.main_content:
        print("3. Set onlyMainContent: true")
    print("\nClaude Code will then display the scraped content.")
    print("=" * 80)

    sys.exit(0)


if __name__ == "__main__":
    main()
