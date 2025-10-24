"""
Data accumulator for storing collected research information.

This module manages the storage and retrieval of all collected data
during the research process, including comprehensive citation tracking.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional


class DataAccumulator:
    """
    Stores all collected data chunks and builds growing context.
    Provides methods to add different types of research data.

    Citation System:
    - Every data point MUST have a source_url
    - Citation numbers are auto-generated and reused for duplicate URLs
    - Footnote references are tracked centrally for markdown generation
    """

    def __init__(self, company_info: Dict[str, str]):
        """
        Initialize data accumulator for a company.

        Args:
            company_info: Basic company information from source
        """
        self.company_info = company_info
        self.data: Dict[str, Any] = {
            "company": company_info,
            "contacts": [],
            "pain_points": [],
            "tech_stack": [],
            "news": [],
            "images": [],
            "sources_explored": [],
            "metadata": {
                "started_at": datetime.now().isoformat(),
                "iterations": 0
            }
        }

        # Citation tracking system
        # Maps URL -> citation number (starting from 1)
        self.citation_map: Dict[str, int] = {}
        self.citation_counter: int = 0

    def _get_citation_number(self, url: str) -> int:
        """
        Get or create citation number for a URL.

        Args:
            url: Source URL

        Returns:
            Citation number (reuses existing number if URL already cited)
        """
        if url in self.citation_map:
            return self.citation_map[url]

        self.citation_counter += 1
        self.citation_map[url] = self.citation_counter
        return self.citation_counter

    def add_contact(
        self,
        name: str,
        title: str = "",
        email: str = "",
        phone: str = "",
        source: str = "",
        source_url: str = ""
    ) -> None:
        """
        Add a contact to the dataset with citation.

        Args:
            name: Contact name
            title: Job title
            email: Email address
            phone: Phone number
            source: Where contact was found (description)
            source_url: URL where contact was found (REQUIRED for citations)
        """
        citation_num = self._get_citation_number(source_url) if source_url else None

        self.data["contacts"].append({
            "name": name,
            "title": title,
            "email": email,
            "phone": phone,
            "source": source,
            "source_url": source_url,
            "citation": citation_num,
            "added_at": datetime.now().isoformat()
        })

    def add_pain_point(
        self,
        description: str,
        evidence: str = "",
        source: str = "",
        source_url: str = ""
    ) -> None:
        """
        Add a pain point observation with citation.

        Args:
            description: Pain point description
            evidence: Supporting evidence
            source: Where pain point was identified (description)
            source_url: URL where pain point was identified (REQUIRED for citations)
        """
        citation_num = self._get_citation_number(source_url) if source_url else None

        self.data["pain_points"].append({
            "description": description,
            "evidence": evidence,
            "source": source,
            "source_url": source_url,
            "citation": citation_num,
            "added_at": datetime.now().isoformat()
        })

    def add_technology(
        self,
        tech: str,
        category: str = "",
        source: str = "",
        source_url: str = ""
    ) -> None:
        """
        Add a technology to the stack with citation.

        Args:
            tech: Technology name
            category: Technology category (e.g., "frontend", "database")
            source: Where technology was identified (description)
            source_url: URL where technology was identified (REQUIRED for citations)
        """
        citation_num = self._get_citation_number(source_url) if source_url else None

        self.data["tech_stack"].append({
            "technology": tech,
            "category": category,
            "source": source,
            "source_url": source_url,
            "citation": citation_num,
            "added_at": datetime.now().isoformat()
        })

    def add_news(
        self,
        title: str,
        summary: str = "",
        url: str = "",
        date: str = ""
    ) -> None:
        """
        Add a news item.

        Args:
            title: News title
            summary: News summary
            url: News article URL
            date: Publication date
        """
        self.data["news"].append({
            "title": title,
            "summary": summary,
            "url": url,
            "date": date,
            "added_at": datetime.now().isoformat()
        })

    def add_images(self, images: List[Dict[str, Any]]) -> None:
        """
        Add image metadata.

        Args:
            images: List of image metadata dictionaries
        """
        self.data["images"].extend(images)

    def add_source(self, source: str, source_type: str = "webpage") -> None:
        """
        Track an explored source.

        Args:
            source: Source identifier (URL, name, etc.)
            source_type: Type of source (webpage, social, news, etc.)
        """
        self.data["sources_explored"].append({
            "source": source,
            "type": source_type,
            "explored_at": datetime.now().isoformat()
        })

    def increment_iteration(self) -> None:
        """Increment the iteration counter."""
        self.data["metadata"]["iterations"] += 1

    def get_context(self) -> Dict[str, Any]:
        """
        Get all accumulated data.

        Returns:
            Complete data dictionary
        """
        return self.data

    def get_citations(self) -> Dict[int, str]:
        """
        Get all citations for footnote generation.

        Returns:
            Dictionary mapping citation number -> URL
        """
        # Invert the citation_map to get number -> URL mapping
        return {num: url for url, num in self.citation_map.items()}

    def get_summary(self) -> str:
        """
        Get human-readable summary of collected data.

        Returns:
            Formatted summary string
        """
        return f"""
=== Data Summary ===
Contacts: {len(self.data['contacts'])}
Pain Points: {len(self.data['pain_points'])}
Technologies: {len(self.data['tech_stack'])}
News Items: {len(self.data['news'])}
Images: {len(self.data['images'])}
Sources Explored: {len(self.data['sources_explored'])}
Citations Tracked: {len(self.citation_map)}
Iterations: {self.data['metadata']['iterations']}
"""
