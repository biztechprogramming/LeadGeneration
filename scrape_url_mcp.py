#!/usr/bin/env python3
"""
Website Scraper using Firecrawl MCP - MCP Integration Wrapper

This is the actual working implementation that demonstrates how to request
web scraping from Claude Code using the Firecrawl MCP tool.

Usage:
    python scrape_url_mcp.py <url>
    python scrape_url_mcp.py https://example.com

Note: This script generates instructions for Claude Code to execute the actual
scraping using the mcp__firecrawl__firecrawl_scrape tool.
"""

import sys
import argparse
import json
from typing import Dict, Any
from urllib.parse import urlparse


def validate_url(url: str) -> bool:
    """Validate URL format."""
    try:
        result = urlparse(url)
        return all([result.scheme in ('http', 'https'), result.netloc])
    except Exception:
        return False


def generate_mcp_request(url: str, main_content: bool = True) -> Dict[str, Any]:
    """
    Generate Firecrawl MCP request configuration.

    Args:
        url: Website URL to scrape
        main_content: Whether to extract only main content

    Returns:
        Dictionary with MCP request parameters
    """
    return {
        "tool": "mcp__firecrawl__firecrawl_scrape",
        "parameters": {
            "url": url,
            "formats": ["markdown"],
            "onlyMainContent": main_content,
            "maxAge": 172800000  # 2-day cache for performance
        }
    }


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate Firecrawl MCP scraping request",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python scrape_url_mcp.py https://example.com
    python scrape_url_mcp.py https://example.com --no-main-content
    python scrape_url_mcp.py https://example.com --json

This script generates a request for Claude Code to execute.
        """
    )

    parser.add_argument(
        'url',
        type=str,
        help='Website URL to scrape'
    )

    parser.add_argument(
        '--no-main-content',
        action='store_true',
        help='Include all content (navigation, sidebars, etc.)'
    )

    parser.add_argument(
        '--json',
        action='store_true',
        help='Output request as JSON'
    )

    args = parser.parse_args()

    # Validate URL
    if not validate_url(args.url):
        print(f"Error: Invalid URL format: {args.url}", file=sys.stderr)
        print("URL must include http:// or https://", file=sys.stderr)
        sys.exit(1)

    # Generate MCP request
    mcp_request = generate_mcp_request(
        args.url,
        main_content=not args.no_main_content
    )

    if args.json:
        # Output as JSON for programmatic use
        print(json.dumps(mcp_request, indent=2))
    else:
        # Output human-readable instructions
        print("=" * 80)
        print("FIRECRAWL MCP SCRAPING REQUEST")
        print("=" * 80)
        print(f"\nTarget URL: {args.url}")
        print(f"Main content only: {not args.no_main_content}")
        print(f"Cache enabled: 48 hours")
        print("\n" + "=" * 80)
        print("MCP REQUEST DETAILS:")
        print("=" * 80)
        print(f"\nTool: {mcp_request['tool']}")
        print(f"\nParameters:")
        for key, value in mcp_request['parameters'].items():
            print(f"  {key}: {value}")
        print("\n" + "=" * 80)
        print("INSTRUCTIONS FOR CLAUDE CODE:")
        print("=" * 80)
        print("\nPlease execute the following MCP tool call:\n")
        print(f"Tool: {mcp_request['tool']}")
        print(f"URL: {args.url}")
        print(f"Formats: markdown")
        print(f"Only Main Content: {not args.no_main_content}")
        print("\nThe scraped content will be displayed as markdown.")
        print("=" * 80)

    sys.exit(0)


if __name__ == "__main__":
    main()
