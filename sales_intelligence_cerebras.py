"""
Sales Intelligence Research Automation System - Cerebras Edition

This script uses the Cerebras API (ultra-fast inference) instead of Claude.
Cerebras is much cheaper and faster for batch processing tasks.

For each company, generates 3 markdown files:
1. [Company]_CONTACTS.md - Contact & Org Chart
2. [Company]_PAIN_POINTS.md - Pain Points & Strategic Analysis
3. [Company]_CALL_PREP.md - Call Prep & Conversation Starters
"""

import csv
import os
import re
import json
import requests
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime


def load_env_file():
    """Load environment variables from .env file if it exists."""
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    # Only set if not already in environment
                    if key not in os.environ:
                        os.environ[key] = value.strip()


class CerebrasSalesIntelligenceResearcher:
    """
    Automated sales intelligence research system using Cerebras API.
    """

    def __init__(self, csv_path: str, output_dir: str = "sales_intelligence_reports"):
        """
        Initialize the researcher.

        Args:
            csv_path: Path to CSV file with company data
            output_dir: Directory to store generated markdown reports
        """
        # Load .env file if it exists
        load_env_file()

        self.csv_path = csv_path
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        # Get Cerebras API key
        self.api_key = os.environ.get('CEREBRAS_API_KEY')
        if not self.api_key:
            raise ValueError(
                "CEREBRAS_API_KEY not set.\n\n"
                "Setup options:\n"
                "1. Create .env file: cp .env.example .env (then edit with your key)\n"
                "2. Or export: export CEREBRAS_API_KEY='your-key-here'\n\n"
                "Get your API key from: https://cloud.cerebras.ai/\n"
            )

        self.api_base = "https://api.cerebras.ai/v1"

        # Delimiters for parsing AI output
        self.delimiters = {
            'contacts': '<FILE_1_CONTACT_ORG_CHART>',
            'pain_points': '<FILE_2_PAIN_POINTS_STRATEGY>',
            'call_prep': '<FILE_3_CALL_PREP_STARTERS>'
        }

    def load_companies(self) -> List[Dict[str, str]]:
        """Load companies from CSV file."""
        companies = []
        with open(self.csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('Title'):  # Skip empty rows
                    companies.append(row)
        return companies

    def sanitize_filename(self, company_name: str) -> str:
        """Convert company name to valid filename."""
        sanitized = re.sub(r'[^\w\s-]', '', company_name)
        sanitized = re.sub(r'\s+', '_', sanitized)
        sanitized = re.sub(r'_+', '_', sanitized)
        return sanitized.strip('_')

    def scrape_website(self, url: str) -> Optional[str]:
        """
        Scrape website content using Firecrawl.

        Args:
            url: Website URL to scrape

        Returns:
            Scraped content as markdown, or None if scraping fails
        """
        if not url or url == 'N/A':
            return None

        try:
            # Note: This requires Firecrawl MCP to be available
            # For now, return None and let AI know website wasn't accessible
            # TODO: Implement actual Firecrawl integration
            return None
        except Exception as e:
            print(f"    Warning: Could not scrape {url}: {e}")
            return None

    def build_research_prompt(self, company: Dict[str, str], website_content: Optional[str] = None) -> str:
        """
        Build the comprehensive research prompt for AI analysis.

        Args:
            company: Dictionary with company data from CSV

        Returns:
            Formatted prompt string
        """
        company_name = company.get('Title', 'Unknown')
        website = company.get('WebsiteURL', '')
        address = company.get('Address', 'N/A')
        phone = company.get('PhoneNumber', 'N/A')

        if website and not website.startswith('http'):
            website = f'https://{website}'

        # Build website content section
        website_section = ""
        if website_content:
            website_section = f"""
**WEBSITE CONTENT (SCRAPED DATA):**
{website_content}

---
"""
        else:
            website_section = """
**IMPORTANT: NO WEBSITE DATA AVAILABLE**
The website could not be accessed. You MUST NOT make up or invent any specific details about:
- Employee names
- Specific job titles
- Contact email addresses
- Specific pain points
- Recent news or announcements

Only provide GENERAL industry-based insights clearly marked as assumptions.

---
"""

        prompt = f"""**CONTEXT & ROLE:**
You are a highly skilled Sales Intelligence Analyst.

**CRITICAL RULE: NEVER INVENT DATA**
- If you don't have actual data from a website, clearly state "NO DATA AVAILABLE - GENERAL INDUSTRY ASSUMPTIONS"
- NEVER make up employee names, titles, or contact information
- NEVER fabricate specific company pain points or news
- Only provide general manufacturing industry insights when no data is available

**INPUT DATA:**
* **Company Name:** {company_name}
* **Website URL:** {website or "No website available"}
* **Address:** {address}
* **Phone Number:** {phone}

{website_section}

**CRITICAL INSTRUCTIONS:**
You MUST use the exact delimiter tags to separate the three sections.

**OUTPUT INSTRUCTIONS (STRICTLY FOLLOW THIS FORMAT):**
Generate a single, continuous text output segmented into three sections, each beginning with a unique delimiter tag.

---

{self.delimiters['contacts']}

Generate content for file: {company_name}_CONTACTS.md

**Objective:** List all key individuals from ACTUAL WEBSITE DATA ONLY.

**IF NO WEBSITE DATA:**
State: "NO CONTACT DATA AVAILABLE - Website not accessible. Research required."

**IF WEBSITE DATA AVAILABLE:**
Create markdown table with ONLY real contacts found on website:

| Name | Title | Buying Role | Email Format | Source |
| :--- | :--- | :--- | :--- | :--- |
| [REAL NAME] | [ACTUAL TITLE] | [Role] | [Format from website] | [Specific page URL] |

**Org Structure Notes:**
* ONLY include if actual data found on website
* If no data: "NO ORG DATA AVAILABLE"

---

{self.delimiters['pain_points']}

Generate content for file: {company_name}_PAIN_POINTS.md

**Objective:** Identify pain points ONLY from actual website content.

**IF NO WEBSITE DATA:**
State: "NO WEBSITE DATA - GENERAL MANUFACTURING ASSUMPTIONS ONLY"
Then list 2-3 COMMON manufacturing industry challenges (clearly marked as general assumptions, NOT specific to this company)

**IF WEBSITE DATA AVAILABLE:**
List 3-5 pain points with SPECIFIC EVIDENCE from the website:
1. **[Problem]:** [Quote or reference from website showing this issue]
2. **[Problem]:** [Specific evidence]

**Strategic Sales Thesis:**
* ONLY if website data available
* If no data: "REQUIRES RESEARCH - Cannot determine without website access"

---

{self.delimiters['call_prep']}

Generate content for file: {company_name}_CALL_PREP.md

**Objective:** Provide call prep ONLY based on real data.

**IF NO WEBSITE DATA:**
State: "NO WEBSITE DATA - MANUAL RESEARCH REQUIRED BEFORE CALLING"
List: "Action Items: 1) Research company website manually 2) Find decision-makers on LinkedIn 3) Check recent news"

**IF WEBSITE DATA AVAILABLE:**
* **Current News:** [ONLY if found on website - otherwise say "No recent news found"]
* **Call Goal:** [Based on actual pain points found]
* **Conversation Starters:** [ONLY using real observations from website - NO generic scripts if no data]

---

**IMPORTANT REMINDERS:**
1. Use the EXACT delimiter tags shown above to separate sections
2. Be specific and evidence-based in your analysis
3. Focus on actionable intelligence for sales teams
4. If website is unavailable, make reasonable inferences from company name, address, and industry context
"""
        return prompt

    def analyze_with_cerebras(self, prompt: str) -> str:
        """
        Send prompt to Cerebras API for analysis.

        Args:
            prompt: Research prompt

        Returns:
            AI-generated analysis
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        # Cerebras uses OpenAI-compatible API
        payload = {
            "model": "llama-3.3-70b",  # Fast and capable model
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert sales intelligence analyst. Provide detailed, evidence-based research."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 8000
        }

        try:
            response = requests.post(
                f"{self.api_base}/chat/completions",
                headers=headers,
                json=payload,
                timeout=120
            )
            response.raise_for_status()

            result = response.json()
            return result['choices'][0]['message']['content']

        except requests.exceptions.Timeout:
            raise RuntimeError("Cerebras API timed out after 120 seconds")
        except requests.exceptions.HTTPError as e:
            raise RuntimeError(f"Cerebras API error: {e.response.text}")
        except Exception as e:
            raise RuntimeError(f"Cerebras API failed: {str(e)}")

    def parse_and_save_reports(self, company_name: str, ai_output: str) -> Tuple[bool, List[str]]:
        """
        Parse AI output using delimiters and save to separate markdown files.

        Args:
            company_name: Name of the company
            ai_output: Raw AI output with delimiter tags

        Returns:
            Tuple of (success, list of created file paths)
        """
        created_files = []
        sanitized_name = self.sanitize_filename(company_name)

        try:
            # Split content by delimiters
            sections = {
                'contacts': self._extract_section(ai_output, self.delimiters['contacts'], self.delimiters['pain_points']),
                'pain_points': self._extract_section(ai_output, self.delimiters['pain_points'], self.delimiters['call_prep']),
                'call_prep': self._extract_section(ai_output, self.delimiters['call_prep'], None)
            }

            # Define file mappings
            file_mappings = {
                'contacts': f'{sanitized_name}_CONTACTS.md',
                'pain_points': f'{sanitized_name}_PAIN_POINTS.md',
                'call_prep': f'{sanitized_name}_CALL_PREP.md'
            }

            # Save each section
            for section_key, content in sections.items():
                if content:
                    filename = file_mappings[section_key]
                    filepath = self.output_dir / filename

                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content.strip())

                    created_files.append(str(filepath))

            return True, created_files

        except Exception as e:
            print(f"Error parsing output for {company_name}: {e}")
            return False, []

    def _extract_section(self, text: str, start_delimiter: str, end_delimiter: Optional[str]) -> str:
        """Extract section between delimiters."""
        start_idx = text.find(start_delimiter)
        if start_idx == -1:
            return ""

        start_idx += len(start_delimiter)

        if end_delimiter:
            end_idx = text.find(end_delimiter, start_idx)
            if end_idx == -1:
                end_idx = len(text)
        else:
            end_idx = len(text)

        return text[start_idx:end_idx]

    def process_company(self, company: Dict[str, str], index: int, total: int) -> Dict[str, any]:
        """
        Process a single company and generate reports.

        Args:
            company: Company data dictionary
            index: Current company index (1-based)
            total: Total number of companies

        Returns:
            Result dictionary with status and details
        """
        company_name = company.get('Title', 'Unknown')
        website = company.get('WebsiteURL', '')

        print(f"\n[{index}/{total}] Processing: {company_name}")
        print(f"Website: {website or 'N/A'}")

        result = {
            'company': company_name,
            'website': website,
            'success': False,
            'files_created': [],
            'error': None
        }

        try:
            # Build research prompt
            prompt = self.build_research_prompt(company)

            # Analyze with Cerebras
            print(f"  → Analyzing with Cerebras AI...")
            ai_output = self.analyze_with_cerebras(prompt)

            # Parse and save reports
            print(f"  → Generating markdown files...")
            success, created_files = self.parse_and_save_reports(company_name, ai_output)

            result['success'] = success
            result['files_created'] = created_files

            if success:
                print(f"  ✓ Created {len(created_files)} files")
                for filepath in created_files:
                    print(f"    - {filepath}")
            else:
                print(f"  ✗ Failed to create files")

        except Exception as e:
            result['error'] = str(e)
            print(f"  ✗ Error: {e}")

        return result

    def run_batch_analysis(self, limit: Optional[int] = None, start_index: int = 0):
        """
        Run batch analysis on all companies in CSV.

        Args:
            limit: Maximum number of companies to process (None for all)
            start_index: Starting index (0-based)
        """
        # Load companies
        companies = self.load_companies()
        total = len(companies)

        print(f"\n{'='*60}")
        print(f"Sales Intelligence Research System (Cerebras Edition)")
        print(f"{'='*60}")
        print(f"Total companies loaded: {total}")
        print(f"Output directory: {self.output_dir}")
        print(f"{'='*60}\n")

        # Apply limit and offset
        if limit:
            companies = companies[start_index:start_index + limit]
        else:
            companies = companies[start_index:]

        print(f"Processing {len(companies)} companies (starting from index {start_index})\n")

        # Track results
        results = []
        successful = 0
        failed = 0

        # Process each company
        for idx, company in enumerate(companies, start=start_index + 1):
            result = self.process_company(company, idx, total)
            results.append(result)

            if result['success']:
                successful += 1
            else:
                failed += 1

            # Small delay to avoid rate limiting
            if idx < len(companies):
                print(f"  → Waiting 1 second before next company...")
                import time
                time.sleep(1)

        # Print summary
        print(f"\n{'='*60}")
        print(f"Batch Processing Complete")
        print(f"{'='*60}")
        print(f"Total Processed: {len(results)}")
        print(f"Successful: {successful}")
        print(f"Failed: {failed}")
        print(f"{'='*60}\n")

        # Save summary report
        self._save_summary_report(results)

    def _save_summary_report(self, results: List[Dict]):
        """Save summary report as JSON."""
        summary_path = self.output_dir / '_batch_summary_cerebras.json'

        summary = {
            'timestamp': datetime.now().isoformat(),
            'provider': 'cerebras',
            'model': 'llama-3.3-70b',
            'total_processed': len(results),
            'successful': sum(1 for r in results if r['success']),
            'failed': sum(1 for r in results if not r['success']),
            'results': results
        }

        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)

        print(f"Summary report saved to: {summary_path}")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Sales Intelligence Research System (Cerebras Edition)'
    )
    parser.add_argument(
        '--csv',
        default='google_maps_leads.csv',
        help='Path to CSV file with company data'
    )
    parser.add_argument(
        '--output',
        default='sales_intelligence_reports_cerebras',
        help='Output directory for markdown reports'
    )
    parser.add_argument(
        '--limit',
        type=int,
        default=None,
        help='Maximum number of companies to process (for testing)'
    )
    parser.add_argument(
        '--start',
        type=int,
        default=0,
        help='Starting index (0-based)'
    )

    args = parser.parse_args()

    # Create researcher instance
    researcher = CerebrasSalesIntelligenceResearcher(
        csv_path=args.csv,
        output_dir=args.output
    )

    # Run batch analysis
    researcher.run_batch_analysis(
        limit=args.limit,
        start_index=args.start
    )


if __name__ == '__main__':
    main()
