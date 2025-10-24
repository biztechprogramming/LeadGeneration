"""
Image collection and processing for research system.

This module handles detection, download, and metadata management
for people images found during research.
"""

import json
import hashlib
import requests
from pathlib import Path
from datetime import datetime
from urllib.parse import urljoin, urlparse
from typing import Dict, Any, List, Optional
from bs4 import BeautifulSoup

from .utils import sanitize_filename


class ImageCollector:
    """
    Scans HTML content for people images and downloads with metadata.
    Uses heuristics to identify person photos vs other images.
    """

    def __init__(self, output_dir: Path):
        """
        Initialize image collector.

        Args:
            output_dir: Base directory for image storage
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def collect_images_from_html(
        self,
        html_content: str,
        base_url: str,
        company_name: str,
        page_context: str = ""
    ) -> List[Dict[str, Any]]:
        """
        Scan HTML for people images and download them.

        Args:
            html_content: HTML content to scan
            base_url: Base URL for resolving relative URLs
            company_name: Company name for organizing images
            page_context: Description of where images were found

        Returns:
            List of image metadata dictionaries
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        images_found = []

        # Create company directory
        company_dir = self.output_dir / "images" / sanitize_filename(company_name)
        company_dir.mkdir(parents=True, exist_ok=True)

        # Find all img tags
        img_tags = soup.find_all('img')

        for img in img_tags:
            src = img.get('src', '')
            alt = img.get('alt', '')

            # Skip obvious non-people images
            if self._is_likely_person_image(src, alt):
                # Resolve full URL
                full_url = urljoin(base_url, src)

                # Extract context
                person_info = self._extract_person_info(img, alt)

                # Download image
                image_path = self._download_image(full_url, company_dir)

                if image_path:
                    metadata = {
                        "filename": image_path.name,
                        "source_url": full_url,
                        "page_context": page_context,
                        "person_name": person_info.get("name", "Unknown"),
                        "person_title": person_info.get("title", ""),
                        "alt_text": alt,
                        "downloaded_at": datetime.now().isoformat()
                    }
                    images_found.append(metadata)

        # Save manifest
        if images_found:
            self._save_manifest(company_dir, images_found)

        return images_found

    def _is_likely_person_image(self, src: str, alt: str) -> bool:
        """
        Heuristic check if image is likely a person photo.

        Args:
            src: Image source URL
            alt: Alt text

        Returns:
            True if likely a person image
        """
        # Keywords suggesting people images
        person_keywords = [
            'team', 'staff', 'employee', 'founder', 'ceo', 'president',
            'director', 'manager', 'headshot', 'profile', 'people',
            'leadership', 'executive', 'member', 'portrait'
        ]

        # Keywords suggesting NOT people images
        exclude_keywords = [
            'logo', 'icon', 'banner', 'background', 'product',
            'chart', 'graph', 'diagram', 'screenshot'
        ]

        text_to_check = (src + " " + alt).lower()

        # Check exclusions first
        if any(keyword in text_to_check for keyword in exclude_keywords):
            return False

        # Check for person indicators
        return any(keyword in text_to_check for keyword in person_keywords)

    def _extract_person_info(self, img_tag, alt_text: str) -> Dict[str, str]:
        """
        Extract person name and title from image context.

        Args:
            img_tag: BeautifulSoup img tag
            alt_text: Image alt text

        Returns:
            Dictionary with name and title
        """
        info = {"name": "", "title": ""}

        # Try to extract from alt text
        if alt_text:
            info["name"] = alt_text

        # Look for nearby text (caption, figcaption, etc.)
        parent = img_tag.parent
        if parent:
            # Check for figcaption
            caption = parent.find('figcaption')
            if caption:
                caption_text = caption.get_text(strip=True)
                # Try to parse "Name - Title" format
                if ' - ' in caption_text:
                    parts = caption_text.split(' - ')
                    info["name"] = parts[0].strip()
                    info["title"] = parts[1].strip() if len(parts) > 1 else ""
                else:
                    info["name"] = caption_text

            # Check for nearby headings or paragraphs
            for sibling in parent.find_all(['h2', 'h3', 'h4', 'p'], limit=2):
                text = sibling.get_text(strip=True)
                if text and not info["name"]:
                    info["name"] = text
                    break

        return info

    def _download_image(self, url: str, output_dir: Path) -> Optional[Path]:
        """
        Download image from URL.

        Args:
            url: Image URL
            output_dir: Directory to save image

        Returns:
            Path to downloaded image, or None if failed
        """
        try:
            response = requests.get(url, timeout=10, stream=True)
            response.raise_for_status()

            # Generate filename from URL hash
            url_hash = hashlib.md5(url.encode()).hexdigest()[:12]
            extension = Path(urlparse(url).path).suffix or '.jpg'
            filename = f"person_{url_hash}{extension}"
            filepath = output_dir / filename

            # Save image
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            return filepath

        except Exception as e:
            print(f"    ⚠ Failed to download image {url}: {e}")
            return None

    def _save_manifest(self, company_dir: Path, images: List[Dict[str, Any]]) -> None:
        """
        Save image manifest JSON.

        Args:
            company_dir: Company images directory
            images: List of image metadata
        """
        manifest_path = company_dir / "image_manifest.json"

        # Load existing manifest if present
        existing = []
        if manifest_path.exists():
            try:
                with open(manifest_path, 'r') as f:
                    existing = json.load(f)
            except (json.JSONDecodeError, IOError):
                existing = []

        # Merge and save
        all_images = existing + images

        with open(manifest_path, 'w') as f:
            json.dump(all_images, f, indent=2)
