"""
Main research orchestrator coordinating all components.

This module provides the primary orchestration logic that coordinates
the AI decision engine, function registry, data accumulator, and other
components to perform iterative intelligent research.
"""

import os
import csv
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

from .utils import load_env_file, sanitize_filename
from .cerebras_client import GeminiCerebrasClient
from .ai_decision_engine import AIDecisionEngine
from .function_registry import FunctionRegistry
from .data_accumulator import DataAccumulator
from .image_collector import ImageCollector
from .website_explorer import WebsiteExplorer


class IterativeResearchOrchestrator:
    """
    Main orchestrator for iterative AI-driven research.
    Coordinates all system components and manages the research loop.
    """

    def __init__(self, csv_path: str, output_dir: str = "intelligent_research_output"):
        """
        Initialize research orchestrator.

        Args:
            csv_path: Path to CSV with company data
            output_dir: Output directory for results

        Raises:
            ValueError: If CEREBRAS_API_KEY not set
        """
        # Load environment
        load_env_file()

        self.csv_path = csv_path
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        # Get API key
        api_key = os.environ.get('CEREBRAS_API_KEY')
        if not api_key:
            raise ValueError(
                "CEREBRAS_API_KEY not set.\n\n"
                "Setup: Create .env file or export CEREBRAS_API_KEY='your-key'\n"
                "Get key from: https://cloud.cerebras.ai/"
            )

        # Initialize components
        self.client = GeminiCerebrasClient(api_key)
        self.ai_engine = AIDecisionEngine(self.client)
        self.registry = FunctionRegistry(self.output_dir)
        self.image_collector = ImageCollector(self.output_dir)
        self.explorer = WebsiteExplorer()

        # Current accumulator (set during company research)
        self.current_accumulator: Optional[DataAccumulator] = None

        # Current source URL (set during page exploration)
        # This tracks the URL context for all data extractions
        self.current_source_url: str = ""

        # Register available functions
        self._register_functions()

    def _register_functions(self) -> None:
        """Register all available research functions."""
        self.registry.register("save_contact", self._save_contact)
        self.registry.register("save_pain_point", self._save_pain_point)
        self.registry.register("download_image", self._download_image)
        self.registry.register("explore_page", self._explore_page)
        self.registry.register("search_linkedin", self._search_linkedin)
        self.registry.register("search_news", self._search_news)
        self.registry.register("extract_tech_stack", self._extract_tech_stack)
        self.registry.register("save_company_info", self._save_company_info)

    def _save_contact(
        self,
        name: str,
        title: str = "",
        email: str = "",
        phone: str = "",
        source: str = "",
        source_url: str = ""
    ) -> None:
        """
        Save a contact (bound to current accumulator).

        Validation: Rejects contacts where ALL required fields are empty.
        At minimum, we need either a name OR an email OR both.
        """
        # Strip whitespace from all fields
        name = name.strip()
        title = title.strip()
        email = email.strip()
        phone = phone.strip()
        source = source.strip()

        # Use provided source_url or fall back to current_source_url
        if not source_url:
            source_url = self.current_source_url

        # Validation: Must have at least name or email
        if not name and not email:
            print(f"    ⚠ Rejected empty contact (no name and no email)")
            print(f"      Debug: name='{name}', email='{email}', phone='{phone}'")
            return

        # Additional quality check: Warn about contacts with only phone
        if not name and not email and phone:
            print(f"    ⚠ Rejected phone-only contact: {phone}")
            print(f"      Reason: Need at least a name or email for valid contact")
            return

        # Warn if no source URL
        if not source_url:
            print(f"    ⚠ Warning: No source URL for contact {name}")

        if self.current_accumulator:
            self.current_accumulator.add_contact(name, title, email, phone, source, source_url)
            print(f"    ✓ Saved contact: {name} - {title} [Citation: {source_url[:50] if source_url else 'N/A'}...]")
            if email:
                print(f"      Email: {email}")
            if phone:
                print(f"      Phone: {phone}")

    def _save_pain_point(
        self,
        description: str,
        evidence: str = "",
        source: str = "",
        source_url: str = ""
    ) -> None:
        """Save a pain point with citation."""
        # Use provided source_url or fall back to current_source_url
        if not source_url:
            source_url = self.current_source_url

        # Warn if no source URL
        if not source_url:
            print(f"    ⚠ Warning: No source URL for pain point")

        if self.current_accumulator:
            self.current_accumulator.add_pain_point(description, evidence, source, source_url)
            print(f"    ✓ Saved pain point: {description[:50]}... [Citation: {source_url[:50] if source_url else 'N/A'}...]")

    def _download_image(
        self,
        url: str,
        person_name: str = "",
        context: str = ""
    ) -> None:
        """Download an image (placeholder)."""
        print(f"    → Would download image: {url}")
        print(f"      Person: {person_name}")

    def _explore_page(self, url: str, reason: str = "") -> None:
        """Explore a webpage and set it as current source context."""
        success, content, explored_url = self.explorer.explore_page(url, reason)

        # Update current source URL for citation tracking
        if success:
            self.current_source_url = explored_url
            print(f"    📍 Current citation source set to: {explored_url}")

        if success and self.current_accumulator:
            self.current_accumulator.add_source(explored_url, "webpage")

    def _search_linkedin(self, company: str, person: str = "") -> None:
        """Search LinkedIn."""
        success, data = self.explorer.search_linkedin(company, person)
        if success and self.current_accumulator:
            self.current_accumulator.add_source(f"LinkedIn: {company}", "social")

    def _search_news(self, company: str, topics: List[str] = None) -> None:
        """Search news."""
        success, news = self.explorer.search_news(company, topics)
        if success and news and self.current_accumulator:
            for item in news:
                self.current_accumulator.add_news(**item)

    def _extract_tech_stack(self, technologies: List[str], source_url: str = "") -> None:
        """Extract technology stack with citation."""
        # Use provided source_url or fall back to current_source_url
        if not source_url:
            source_url = self.current_source_url

        if self.current_accumulator:
            for tech in technologies:
                self.current_accumulator.add_technology(
                    tech,
                    source="AI extraction",
                    source_url=source_url
                )
                print(f"    ✓ Added technology: {tech} [Citation: {source_url[:50] if source_url else 'N/A'}...]")

    def _save_company_info(self, key: str, value: str) -> None:
        """Save company metadata."""
        print(f"    ✓ Saved: {key} = {value}")

    def load_companies(self) -> List[Dict[str, str]]:
        """
        Load companies from CSV file.

        Returns:
            List of company dictionaries
        """
        companies = []
        with open(self.csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('Title'):
                    companies.append(row)
        return companies

    def research_company(
        self,
        company: Dict[str, str],
        max_iterations: int = 10
    ) -> Dict[str, Any]:
        """
        Perform iterative research on a company.

        Args:
            company: Company data dictionary
            max_iterations: Maximum research iterations

        Returns:
            Final accumulated data
        """
        company_name = company.get('Title', 'Unknown')
        print(f"\n{'='*60}")
        print(f"Researching: {company_name}")
        print(f"{'='*60}")

        # Initialize accumulator for this company
        accumulator = DataAccumulator(company)
        self.current_accumulator = accumulator

        # Initial exploration (if website available)
        website = company.get('WebsiteURL', '')
        if website:
            accumulator.add_source(website, "homepage")

        # Iterative research loop
        for iteration in range(1, max_iterations + 1):
            print(f"\n--- Iteration {iteration}/{max_iterations} ---")
            accumulator.increment_iteration()

            # Get current context
            context = accumulator.get_context()

            # Ask AI for analysis and decisions
            print("  → Consulting AI for analysis...")
            try:
                decision = self.ai_engine.analyze_data(context, company)
            except Exception as e:
                print(f"  ✗ AI analysis failed: {e}")
                break

            # Show relevant data found
            if decision.get("relevant_data"):
                print(f"  📊 Relevant data identified: {len(decision['relevant_data'])} items")
                for item in decision["relevant_data"][:3]:
                    print(f"    - {item}")

            # Execute suggested actions
            actions = decision.get("actions", [])
            if actions:
                print(f"  ⚙️  Executing {len(actions)} action(s)...")
                for action in actions:
                    func_name = action.get("function", "")
                    params = action.get("params", {})

                    if func_name:
                        success, result = self.registry.execute(func_name, params)
                        if not success:
                            print(f"    ⚠ {result}")

            # Execute next steps
            next_steps = decision.get("next_steps", [])
            if next_steps:
                print(f"  🔍 Exploring {len(next_steps)} new source(s)...")
                for step in next_steps:
                    func_name = step.get("function", "")
                    params = step.get("params", {})

                    if func_name:
                        success, result = self.registry.execute(func_name, params)
                        if not success:
                            print(f"    ⚠ {result}")

            # Check if AI says we're done
            status = decision.get("status", "continue")
            if status == "complete":
                print(f"\n  ✓ AI determined research is complete")
                break

            # Show current progress
            print(accumulator.get_summary())

        # Final summary
        print(f"\n{'='*60}")
        print(f"Research Complete: {company_name}")
        print(accumulator.get_summary())
        print(f"{'='*60}\n")

        return accumulator.get_context()

    def generate_final_report(
        self,
        company_name: str,
        accumulated_data: Dict[str, Any]
    ) -> None:
        """
        Generate final markdown report with comprehensive inline citations.

        Args:
            company_name: Company name
            accumulated_data: All collected data with citation tracking
        """
        sanitized_name = sanitize_filename(company_name)
        report_path = self.output_dir / f"{sanitized_name}_INTELLIGENT_RESEARCH.md"

        # Get citation mappings
        citations = self.current_accumulator.get_citations() if self.current_accumulator else {}

        # Build report sections
        report_lines = [
            f"# Intelligent Research Report: {company_name}",
            "",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Research Iterations:** {accumulated_data['metadata']['iterations']}",
            f"**Citations Tracked:** {len(citations)}",
            "",
            "---",
            "",
            "## 🏢 Company Overview",
            "",
            f"```json\n{json.dumps(accumulated_data['company'], indent=2)}\n```",
            "",
            "---",
            "",
            f"## 👥 Contacts Identified ({len(accumulated_data['contacts'])})",
            ""
        ]

        # Add contacts table with inline citations
        if accumulated_data['contacts']:
            report_lines.extend([
                "| Name | Title | Email | Phone | Source |",
                "|------|-------|-------|-------|--------|"
            ])
            for contact in accumulated_data['contacts']:
                # Add citation marker if available
                citation_marker = f"[^{contact['citation']}]" if contact.get('citation') else ""

                # Build row with citations after each fact
                name_cell = f"{contact['name']}{citation_marker}" if contact['name'] else ""
                title_cell = f"{contact['title']}{citation_marker}" if contact['title'] else ""
                email_cell = f"{contact['email']}{citation_marker}" if contact['email'] else ""
                phone_cell = f"{contact['phone']}{citation_marker}" if contact['phone'] else ""
                source_cell = f"{contact['source']}"

                report_lines.append(
                    f"| {name_cell} | {title_cell} | "
                    f"{email_cell} | {phone_cell} | {source_cell} |"
                )
        else:
            report_lines.append("*No contacts identified during research.*")

        report_lines.extend([
            "",
            "---",
            "",
            f"## 💡 Pain Points Identified ({len(accumulated_data['pain_points'])})",
            ""
        ])

        # Add pain points with inline citations
        if accumulated_data['pain_points']:
            for i, pain_point in enumerate(accumulated_data['pain_points'], 1):
                citation_marker = f"[^{pain_point['citation']}]" if pain_point.get('citation') else ""

                report_lines.append(f"### {i}. {pain_point['description']}{citation_marker}")
                report_lines.append("")
                if pain_point['evidence']:
                    report_lines.append(f"**Evidence:** {pain_point['evidence']}{citation_marker}")
                    report_lines.append("")
                report_lines.append(f"**Source:** {pain_point['source']}")
                report_lines.append("")
        else:
            report_lines.append("*No pain points identified during research.*")

        # Add tech stack section if available
        if accumulated_data.get('tech_stack'):
            report_lines.extend([
                "",
                "---",
                "",
                f"## 🔧 Technology Stack ({len(accumulated_data['tech_stack'])})",
                ""
            ])

            # Group by category
            tech_by_category: Dict[str, List] = {}
            for tech_item in accumulated_data['tech_stack']:
                category = tech_item.get('category', 'Other')
                if category not in tech_by_category:
                    tech_by_category[category] = []
                tech_by_category[category].append(tech_item)

            for category, items in sorted(tech_by_category.items()):
                report_lines.append(f"### {category}")
                report_lines.append("")
                for tech_item in items:
                    citation_marker = f"[^{tech_item['citation']}]" if tech_item.get('citation') else ""
                    report_lines.append(f"- {tech_item['technology']}{citation_marker}")
                report_lines.append("")

        # Add citations/footnotes section at the end
        if citations:
            report_lines.extend([
                "",
                "---",
                "",
                "## 📚 Citations",
                "",
                "*All facts in this report are cited with clickable sources below:*",
                ""
            ])

            # Add footnote definitions (sorted by citation number)
            for citation_num in sorted(citations.keys()):
                url = citations[citation_num]
                report_lines.append(f"[^{citation_num}]: {url}")

        # Save report
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_lines))

        print(f"📄 Report saved: {report_path}")
        print(f"   📍 {len(citations)} unique sources cited")

    def run_batch_research(
        self,
        limit: Optional[int] = None,
        start_index: int = 0
    ) -> None:
        """
        Run batch research on companies.

        Args:
            limit: Maximum companies to process
            start_index: Starting index
        """
        companies = self.load_companies()

        print(f"\n{'='*60}")
        print(f"Iterative AI-Driven Research System")
        print(f"{'='*60}")
        print(f"Total companies: {len(companies)}")
        print(f"Output directory: {self.output_dir}")
        print(f"{'='*60}\n")

        # Apply limit
        if limit:
            companies = companies[start_index:start_index + limit]
        else:
            companies = companies[start_index:]

        print(f"Processing {len(companies)} companies\n")

        # Process each company
        results = []
        for idx, company in enumerate(companies, start=start_index + 1):
            try:
                print(f"\n[{idx}/{len(companies)}] Starting research...")

                # Research company
                accumulated_data = self.research_company(company)

                # Generate report
                company_name = company.get('Title', 'Unknown')
                self.generate_final_report(company_name, accumulated_data)

                results.append({
                    "company": company_name,
                    "success": True,
                    "iterations": accumulated_data['metadata']['iterations'],
                    "contacts_found": len(accumulated_data['contacts']),
                    "pain_points_found": len(accumulated_data['pain_points']),
                    "images_collected": len(accumulated_data['images'])
                })

            except Exception as e:
                print(f"\n✗ Error processing company: {e}")
                results.append({
                    "company": company.get('Title', 'Unknown'),
                    "success": False,
                    "error": str(e)
                })

        # Save summary
        summary_path = self.output_dir / "_batch_summary.json"
        with open(summary_path, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "total_processed": len(results),
                "successful": sum(1 for r in results if r.get('success')),
                "results": results
            }, f, indent=2)

        print(f"\n{'='*60}")
        print(f"Batch Research Complete")
        print(f"Summary saved: {summary_path}")
        print(f"{'='*60}\n")
