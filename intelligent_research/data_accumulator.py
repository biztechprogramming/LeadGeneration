"""
Data accumulator for storing collected research information.

This module manages the storage and retrieval of all collected data
during the research process.
"""

from datetime import datetime
from typing import Dict, Any, List


class DataAccumulator:
    """
    Stores all collected data chunks and builds growing context.
    Provides methods to add different types of research data.
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

    def add_contact(
        self,
        name: str,
        title: str = "",
        email: str = "",
        phone: str = "",
        source: str = ""
    ) -> None:
        """
        Add a contact to the dataset.

        Args:
            name: Contact name
            title: Job title
            email: Email address
            phone: Phone number
            source: Where contact was found
        """
        self.data["contacts"].append({
            "name": name,
            "title": title,
            "email": email,
            "phone": phone,
            "source": source,
            "added_at": datetime.now().isoformat()
        })

    def add_pain_point(
        self,
        description: str,
        evidence: str = "",
        source: str = ""
    ) -> None:
        """
        Add a pain point observation.

        Args:
            description: Pain point description
            evidence: Supporting evidence
            source: Where pain point was identified
        """
        self.data["pain_points"].append({
            "description": description,
            "evidence": evidence,
            "source": source,
            "added_at": datetime.now().isoformat()
        })

    def add_technology(
        self,
        tech: str,
        category: str = "",
        source: str = ""
    ) -> None:
        """
        Add a technology to the stack.

        Args:
            tech: Technology name
            category: Technology category (e.g., "frontend", "database")
            source: Where technology was identified
        """
        self.data["tech_stack"].append({
            "technology": tech,
            "category": category,
            "source": source,
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
Iterations: {self.data['metadata']['iterations']}
"""
