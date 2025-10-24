"""
Website exploration module for research system.

This module handles web page exploration by requesting scraping
via Claude Code's Firecrawl MCP integration.
"""

from typing import Tuple, Optional, Dict, List
import json
import time
import os
from pathlib import Path


class WebsiteExplorer:
    """
    Explores company website iteratively based on AI suggestions.
    Uses Claude Code + Firecrawl MCP for web scraping via request files.
    """

    def __init__(self, scrape_cache_dir: str = "scrape_cache"):
        """
        Initialize website explorer.

        Args:
            scrape_cache_dir: Directory for scraping request/response files
        """
        self.scrape_cache_dir = Path(scrape_cache_dir)
        self.scrape_cache_dir.mkdir(exist_ok=True)
        print(f"✓ Website explorer initialized with cache: {self.scrape_cache_dir}")

    def explore_page(self, url: str, reason: str = "") -> Tuple[bool, Optional[str], str]:
        """
        Explore a webpage using Claude Code + Firecrawl MCP.

        Args:
            url: URL to explore
            reason: Reason for exploring (for logging)

        Returns:
            Tuple of (success: bool, content: Optional[str], url: str)
            The URL is returned for citation purposes
        """
        print(f"    → Exploring: {url}")
        if reason:
            print(f"      Reason: {reason}")

        try:
            # Check cache first
            cache_file = self.scrape_cache_dir / f"{hash(url)}.md"
            if cache_file.exists():
                content = cache_file.read_text(encoding='utf-8')
                print(f"      ✓ Using cached content ({len(content)} characters)")
                return True, content, url

            # Use qwen -y -p to scrape via Firecrawl MCP (Cerebras-powered, much faster!)
            import subprocess

            prompt = f"""Use the Firecrawl MCP tool (mcp__firecrawl__firecrawl_scrape) to scrape this URL: {url}

Parameters:
- url: {url}
- formats: ["markdown"]
- onlyMainContent: true

Return ONLY the markdown content, no explanations or formatting. Just the raw scraped content."""

            result = subprocess.run(
                ['qwen', '-y', '-p', prompt],
                capture_output=True,
                text=True,
                timeout=60,  # Cerebras is much faster, reduce timeout
                env={**os.environ, 'NODE_ENV': 'production'}  # Suppress debug output
            )

            if result.returncode == 0 and result.stdout:
                content = result.stdout.strip()

                # Filter out qwen debug output and other noise
                lines = content.split('\n')
                cleaned_lines = []
                skip_patterns = ['[QWEN]', 'Created workspace', 'Setting language', 'Global language', 'Loading translations', 'Translations loaded', 'Available translation keys']
                for line in lines:
                    if not any(pattern in line for pattern in skip_patterns):
                        cleaned_lines.append(line)
                content = '\n'.join(cleaned_lines).strip()

                # Basic validation - should have some content
                if len(content) > 100:
                    # Cache the result
                    cache_file.write_text(content, encoding='utf-8')
                    print(f"      ✓ Scraped {len(content)} characters (cached)")
                    return True, content, url
                else:
                    print(f"      ✗ Content too short ({len(content)} chars)")
                    return False, None, url
            else:
                print(f"      ✗ Scraping failed: {result.stderr[:200] if result.stderr else 'no output'}")
                return False, None, url

        except subprocess.TimeoutExpired:
            print(f"      ✗ Scraping timeout after 120s")
            return False, None, url
        except Exception as e:
            print(f"      ✗ Error scraping {url}: {e}")
            return False, None, url

    def search_linkedin(
        self,
        company: str,
        person: str = ""
    ) -> Tuple[bool, Optional[Dict]]:
        """
        Search LinkedIn (placeholder).

        Args:
            company: Company name
            person: Person name (optional)

        Returns:
            Tuple of (success: bool, data: Optional[Dict])
        """
        print(f"    → Searching LinkedIn for: {company}")
        if person:
            print(f"      Looking for: {person}")

        # Placeholder - real implementation would:
        # - Use LinkedIn API (requires authentication)
        # - Or use web scraping (respect rate limits and ToS)
        # - Return structured profile data
        return False, None

    def search_news(
        self,
        company: str,
        topics: List[str] = None
    ) -> Tuple[bool, Optional[List]]:
        """
        Search news (placeholder).

        Args:
            company: Company name
            topics: Topics to search for

        Returns:
            Tuple of (success: bool, news_items: Optional[List])
        """
        print(f"    → Searching news for: {company}")
        if topics:
            print(f"      Topics: {', '.join(topics)}")

        # Placeholder - real implementation could use:
        # - News APIs (Google News API, NewsAPI, etc.)
        # - RSS feeds
        # - Web scraping of news sites
        # Return list of dictionaries with:
        # - title, summary, url, date, source
        return False, None

    def validate_url(self, url: str) -> bool:
        """
        Validate URL format.

        Args:
            url: URL string to validate

        Returns:
            True if URL appears valid
        """
        if not url:
            return False

        # Basic validation
        return url.startswith(('http://', 'https://'))

    def extract_domain(self, url: str) -> Optional[str]:
        """
        Extract domain from URL.

        Args:
            url: Full URL

        Returns:
            Domain name or None
        """
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc
        except Exception:
            return None
