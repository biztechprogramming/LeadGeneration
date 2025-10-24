"""
Sales Intelligence Research Automation System

This script reads companies from google_maps_leads.csv and generates
comprehensive sales intelligence reports using AI-powered web scraping.

For each company, generates 3 markdown files:
1. [Company]_CONTACTS.md - Contact & Org Chart
2. [Company]_PAIN_POINTS.md - Pain Points & Strategic Analysis
3. [Company]_CALL_PREP.md - Call Prep & Conversation Starters
"""

import csv
import os
import re
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime


class SalesIntelligenceResearcher:
    """
    Automated sales intelligence research system using Claude Code CLI.
    """

    def __init__(self, csv_path: str, output_dir: str = "sales_intelligence_reports", log_dir: str = "ai_logs"):
        """
        Initialize the researcher.

        Args:
            csv_path: Path to CSV file with company data
            output_dir: Directory to store generated markdown reports
            log_dir: Directory to store AI interaction logs
        """
        self.csv_path = csv_path
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        # Setup AI logging directory
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self.request_count = 0

        # Check if claude CLI is available
        if not self._check_claude_cli():
            raise RuntimeError(
                "Claude CLI not found. Please ensure Claude Code is installed and 'claude' command is available."
            )

        # Delimiters for parsing AI output
        self.delimiters = {
            'contacts': '<FILE_1_CONTACT_ORG_CHART>',
            'pain_points': '<FILE_2_PAIN_POINTS_STRATEGY>',
            'call_prep': '<FILE_3_CALL_PREP_STARTERS>'
        }

    def _check_claude_cli(self) -> bool:
        """Check if claude CLI command is available."""
        try:
            subprocess.run(['claude', '--help'], capture_output=True, check=True, timeout=5)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            return False

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
        # Remove special characters, keep alphanumeric and spaces
        sanitized = re.sub(r'[^\w\s-]', '', company_name)
        # Replace spaces with underscores
        sanitized = re.sub(r'\s+', '_', sanitized)
        # Remove multiple underscores
        sanitized = re.sub(r'_+', '_', sanitized)
        return sanitized.strip('_')

    def build_research_prompt(self, company: Dict[str, str]) -> str:
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

        # Add https:// if not present
        if website and not website.startswith('http'):
            website = f'https://{website}'

        prompt = f"""**CONTEXT & ROLE:**
You are a highly skilled Sales Intelligence Analyst and Competitive Researcher. Your task is to perform an exhaustive deep-dive on the company at the provided URL. You must analyze the company's website structure, public information, and implicit signals (e.g., career pages, leadership language) to generate an actionable sales briefing.

**INPUT DATA:**
* **Company Name:** {company_name}
* **Website URL:** {website or "No website available"}
* **Address:** {address}
* **Phone Number:** {phone}

**CRITICAL INSTRUCTIONS:**
You MUST use the exact delimiter tags to separate the three sections. Each section should be complete and comprehensive.

**OUTPUT INSTRUCTIONS (STRICTLY FOLLOW THIS FORMAT):**
Generate a single, continuous text output segmented into three sections, each beginning with a unique delimiter tag.

---

{self.delimiters['contacts']}

Generate content for file: {company_name}_CONTACTS.md

**Objective:** List all key individuals, their potential buying role, and inferred contact information.

**CRITICAL CONTACT QUALITY RULES:**
❌ **DO NOT include contacts where you only have:**
   - Generic phone numbers without names/emails
   - Form field labels (like "Email *" or "Phone *")
   - Contact form submit buttons without actual contact info
   - Placeholder text or instructions

✅ **ONLY include contacts where you have:**
   - ACTUAL person names (e.g., "John Smith", "Jane Doe", "Bob Johnson")
   - Department/role contacts WITH real email addresses (e.g., "Sales Team" + sales@company.com)
   - Real email addresses even if person name is unknown
   - Verifiable information from About Us, Team, or Leadership pages

**Quality Standards:**
- Prefer specific people over generic departments
- Prioritize contacts with both name AND email
- Include LinkedIn URLs if found for executives
- If you find "Contact: 555-1234" but NO name/email, DO NOT add it to the table
- If unsure whether data is valid, DO NOT include it

**Format:** Markdown table for key contacts and brief org structure summary.

| Name | Title (Actual/Inferred) | Buying Role (DM, Influencer, User) | Estimated Email Format | Source of Info |
| :--- | :--- | :--- | :--- | :--- |
| **CEO/Founder** | [Current Title] | Decision Maker | [Example: jdoe@company.com] | [Source URL/Page] |
| **Primary Target Persona** | [VP of Sales, Head of IT, CMO, etc.] | [DM/Influencer] | [Example: first.last@company.com] | [Source URL/Page] |
| **Secondary Target** | [e.g., IT Director] | Influencer | [Example: initials@company.com] | [Source URL/Page] |

**If NO valid contacts found:** State "No specific contacts identified on public website. Recommend LinkedIn prospecting or direct phone inquiry."

**Org Structure Notes:**
* **Key Departments:** Briefly describe major divisions mentioned
* **Growth Signals:** Mention departments or roles with high hiring volume

---

{self.delimiters['pain_points']}

Generate content for file: {company_name}_PAIN_POINTS.md

**Objective:** Analyze the company's public presence to infer operational, technical, or financial challenges.

**Format:** List of 3-5 specific, well-substantiated pain points and strategic sales thesis.

**Top 3-5 Inferred Pain Points:**
1. **[Specific Problem]:** [1-2 sentences explaining why they likely have this problem, citing evidence]
2. **[Specific Problem]:** [Analysis and Evidence]
3. **[Specific Problem]:** [Analysis and Evidence]
4. **[Specific Problem]:** [Analysis and Evidence]

**Strategic Sales Thesis:**
* **Primary Sales Angle:** State the single most effective way your product/service can address their most critical pain point
* **Competition Clues:** Mention any partners, competitors, or technologies they work with

---

{self.delimiters['call_prep']}

Generate content for file: {company_name}_CALL_PREP.md

**Objective:** Create a concise, actionable cheat sheet for sales representatives.

**Format:** Short, impactful bullet points and questions.

**Pre-Call Checklist:**
* **Current News:** [1-2 sentences on most recent public announcement (funding, new product, major hire, etc.)]
* **Call Goal:** Secure follow-up/discovery on their need to address Pain Point 1

**Conversation Starters (Use these!):**
* **High-Value Question (Needs Analysis):** "I noticed [specific observation]. What's the biggest bottleneck your team is hitting right now?"
* **Bold Statement (Value Proposition):** "Based on our work with companies in your space, I anticipate a significant pain point is [Pain Point 1]. We typically see a **[X%] improvement in Y metric** when that's fixed."
* **Closing Question:** "If we could demonstrate a clear path to solving [Pain Point 1] in the next 90 days, would that be a priority for you?"

---

**CRITICAL CITATION REQUIREMENTS:**
🔗 **EVERY SINGLE FACT MUST HAVE A CITATION WITH CLICKABLE URL!**

**MANDATORY CITATION RULES:**
1. **USE MARKDOWN FOOTNOTE SYNTAX:** [^1], [^2], [^3], etc.
2. **CITE EVERY INDIVIDUAL FACT:** Each name, title, email, phone number, statement gets its own citation marker
3. **REUSE CITATION NUMBERS:** If multiple facts come from the EXACT SAME URL, use the same citation number
4. **NEW URL = NEW NUMBER:** Different URL/page = different citation number
5. **END EACH SECTION:** Add "## Citations" at the bottom of EACH file section with all URL definitions

**WHAT REQUIRES CITATIONS (Everything!):**
- ✅ **Names:** John Smith[^1]
- ✅ **Titles:** CEO[^1], VP of Sales[^2]
- ✅ **Emails:** john@example.com[^1]
- ✅ **Phone Numbers:** 555-1234[^1]
- ✅ **Pain Points:** "Scaling infrastructure challenges"[^3]
- ✅ **Evidence:** "Blog post mentions migration to cloud"[^3]
- ✅ **Technologies:** React[^4], Node.js[^4]
- ✅ **Company Info:** Founded in 2010[^5], 50 employees[^5]
- ✅ **News Items:** "Raised $10M Series A"[^6]
- ✅ **Departments:** Engineering team[^2], Sales department[^7]

**GRANULAR CITATION RULES:**
1. **Same URL, Same Facts → Same Citation:**
   - If "John Smith" and "CEO" both come from https://example.com/about
   - Use: John Smith[^1], CEO[^1]
   - Citation: [^1]: https://example.com/about

2. **Different URLs → Different Citations:**
   - If "John Smith" from https://example.com/about
   - And "jane@example.com" from https://example.com/contact
   - Use: John Smith[^1], jane@example.com[^2]
   - Citations: [^1]: https://example.com/about, [^2]: https://example.com/contact

3. **Paragraph Rule:**
   - If entire paragraph comes from ONE source, cite once at end of paragraph
   - If paragraph combines info from multiple sources, cite each fact individually

**CITATION FORMAT IN TABLES:**
```markdown
| Name | Title | Email | Phone | Source |
|------|-------|-------|-------|--------|
| John Smith[^1] | CEO[^1] | john@example.com[^1] | 555-1234[^1] | About Us page |
| Jane Doe[^2] | CTO[^2] | jane@example.com[^2] | 555-5678[^2] | Team page |

## Citations
[^1]: https://example.com/about
[^2]: https://example.com/team
```

**CITATION FORMAT IN LISTS:**
```markdown
1. **Infrastructure Scaling Challenges[^3]:** The company blog discusses migration challenges and cloud adoption[^3]
2. **Legacy System Debt[^4]:** Careers page mentions "modernizing legacy systems"[^4]

## Citations
[^3]: https://example.com/blog/scaling
[^4]: https://example.com/careers
```

**COMPLETE EXAMPLE - CONTACTS TABLE:**
```markdown
| Name | Title | Email | Phone | Source |
|------|-------|-------|-------|--------|
| John Smith[^1] | CEO[^1] | john@company.com[^1] | 555-0001[^1] | About page |
| Jane Doe[^2] | VP Engineering[^2] | jane@company.com[^3] | 555-0002[^3] | Team page |
| Bob Johnson[^4] | Sales Director[^4] | bob@company.com[^4] | - | LinkedIn profile |

**Explanation:**
- John's name, title, email, phone all from same URL → [^1]
- Jane's name and title from team page → [^2]
- Jane's email and phone from contact page → [^3]
- Bob's info all from LinkedIn → [^4]

## Citations
[^1]: https://company.com/about
[^2]: https://company.com/team
[^3]: https://company.com/contact
[^4]: https://linkedin.com/in/bobjohnson
```

**IMPORTANT REMINDERS:**
1. Use the EXACT delimiter tags shown above to separate sections
2. Be specific and evidence-based in your analysis
3. **ADD CITATIONS WITH URLS TO EVERY FACT - THIS IS MANDATORY**
4. Focus on actionable intelligence for sales teams
5. If website is unavailable, make reasonable inferences from company name, address, and industry context
"""
        return prompt

    async def scrape_website(self, url: str) -> Optional[str]:
        """
        Scrape website content using available tools.

        Note: This is a placeholder. In actual implementation, you would use
        the Firecrawl MCP server or similar web scraping tool.

        Args:
            url: Website URL to scrape

        Returns:
            Scraped content as markdown text, or None if scraping fails
        """
        # TODO: Implement Firecrawl integration
        # For now, return None to indicate scraping should be done via MCP
        return None

    def analyze_with_ai(self, prompt: str, website_content: Optional[str] = None) -> str:
        """
        Send prompt to Claude AI via Claude Code CLI with comprehensive logging.

        Args:
            prompt: Research prompt
            website_content: Optional scraped website content

        Returns:
            AI-generated analysis
        """
        self.request_count += 1
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = self.log_dir / f"claude_request_{self.request_count:03d}_{timestamp}.log"

        # Build full prompt
        full_prompt = prompt
        if website_content:
            full_prompt = f"**WEBSITE CONTENT:**\n\n{website_content}\n\n---\n\n{prompt}"

        # Log request
        log_content = [
            "=" * 80,
            f"CLAUDE AI REQUEST #{self.request_count}",
            f"Timestamp: {datetime.now().isoformat()}",
            f"Method: Claude Code CLI",
            "=" * 80,
            "",
            "--- PROMPT ---",
            full_prompt,
            "",
            "--- EXECUTION START ---",
            f"Command: claude --print <prompt>",
            f"Timeout: 300 seconds",
            ""
        ]

        # Call claude CLI with --print flag for non-interactive output
        try:
            result = subprocess.run(
                ['claude', '--print', full_prompt],
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
                check=True
            )

            ai_response = result.stdout.strip()

            # Log successful response
            log_content.extend([
                "--- AI RESPONSE ---",
                ai_response,
                "",
                "--- RESPONSE METADATA ---",
                f"Status: SUCCESS",
                f"Response Length: {len(ai_response)} characters",
                f"STDERR (if any): {result.stderr if result.stderr else '(none)'}",
                "",
                "=" * 80
            ])

            # Write log file
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(log_content))

            print(f"    📝 AI interaction logged: {log_file.name}")

            return ai_response

        except subprocess.TimeoutExpired:
            log_content.extend([
                "--- ERROR ---",
                "Claude CLI timed out after 5 minutes",
                "",
                "=" * 80
            ])
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(log_content))
            raise RuntimeError("Claude CLI timed out after 5 minutes")

        except subprocess.CalledProcessError as e:
            log_content.extend([
                "--- ERROR ---",
                f"Claude CLI failed with exit code: {e.returncode}",
                f"STDERR: {e.stderr}",
                f"STDOUT: {e.stdout}",
                "",
                "=" * 80
            ])
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(log_content))
            raise RuntimeError(f"Claude CLI failed: {e.stderr}")

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
        """
        Extract section between delimiters.

        Args:
            text: Full text
            start_delimiter: Starting delimiter
            end_delimiter: Ending delimiter (None for last section)

        Returns:
            Extracted section text
        """
        # Find start position
        start_idx = text.find(start_delimiter)
        if start_idx == -1:
            return ""

        # Move past the delimiter
        start_idx += len(start_delimiter)

        # Find end position
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
            # Step 1: Build research prompt
            prompt = self.build_research_prompt(company)

            # Step 2: Scrape website (if available)
            website_content = None
            if website:
                print(f"  → Scraping website...")
                # TODO: Implement Firecrawl scraping
                # website_content = await self.scrape_website(website)

            # Step 3: Analyze with AI
            print(f"  → Analyzing with AI...")
            ai_output = self.analyze_with_ai(prompt, website_content)

            # Step 4: Parse and save reports
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
        print(f"Sales Intelligence Research System")
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
                print(f"  → Waiting 2 seconds before next company...")
                import time
                time.sleep(2)

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
        summary_path = self.output_dir / '_batch_summary.json'

        summary = {
            'timestamp': datetime.now().isoformat(),
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
        description='Sales Intelligence Research Automation System'
    )
    parser.add_argument(
        '--csv',
        default='google_maps_leads.csv',
        help='Path to CSV file with company data'
    )
    parser.add_argument(
        '--output',
        default='sales_intelligence_reports',
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
    researcher = SalesIntelligenceResearcher(
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
