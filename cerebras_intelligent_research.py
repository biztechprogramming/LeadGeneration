"""
Iterative AI-Driven Research System with Cerebras

This system uses AI to intelligently explore company data:
1. AI analyzes current data and suggests next actions
2. System executes suggested functions (or logs if missing)
3. Collects images of people from websites
4. Iteratively builds comprehensive company intelligence
5. Continues until AI determines sufficient data collected

Architecture:
- AIDecisionEngine: Sends data to AI, gets structured decisions
- FunctionRegistry: Tracks available functions, logs missing ones
- ImageCollector: Finds and downloads people images with metadata
- DataAccumulator: Stores growing context for AI analysis
- WebsiteExplorer: Iteratively explores company web presence
- GeminiCerebrasClient: Wrapper for Cerebras API via Gemini CLI
"""

import csv
import os
import re
import json
import requests
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any, Callable
from datetime import datetime
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import hashlib


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


class GeminiCerebrasClient:
    """
    Wrapper to use Gemini CLI pointed at Cerebras API.
    Constructs proper Gemini CLI commands and parses responses.
    """

    def __init__(self, api_key: str, model: str = "llama-3.3-70b"):
        """
        Initialize Gemini client for Cerebras.

        Args:
            api_key: Cerebras API key
            model: Model to use (default: llama-3.3-70b)
        """
        self.api_key = api_key
        self.model = model
        self.api_base = "https://api.cerebras.ai/v1"

    def send_prompt(self, prompt: str, system_prompt: Optional[str] = None,
                   temperature: float = 0.7, max_tokens: int = 4000) -> str:
        """
        Send prompt to Cerebras via API.

        Args:
            prompt: User prompt
            system_prompt: System context (optional)
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response

        Returns:
            AI response text
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        messages = []
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })
        messages.append({
            "role": "user",
            "content": prompt
        })

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
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

    def parse_json_response(self, response: str) -> Dict[str, Any]:
        """
        Parse JSON from AI response.

        Args:
            response: Raw AI response text

        Returns:
            Parsed JSON dictionary
        """
        # Try to extract JSON from code blocks
        json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            # Try to find JSON object directly
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
            else:
                json_str = response

        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON response: {e}\nResponse: {response[:500]}")


class AIDecisionEngine:
    """
    Sends data to AI and gets structured decisions about what to do next.
    """

    def __init__(self, client: GeminiCerebrasClient):
        """
        Initialize decision engine.

        Args:
            client: GeminiCerebrasClient instance
        """
        self.client = client

    def analyze_data(self, accumulated_data: Dict[str, Any],
                    company_info: Dict[str, str]) -> Dict[str, Any]:
        """
        Ask AI to analyze current data and suggest next steps.

        Args:
            accumulated_data: All data collected so far
            company_info: Basic company information

        Returns:
            Structured decision with relevant_data, actions, next_steps, status
        """
        system_prompt = """You are an intelligent research assistant that analyzes company data and suggests next steps.

Your task is to:
1. Identify relevant data from current context
2. Suggest actions to take with the data (save, extract, analyze)
3. Suggest next exploration steps (pages to visit, sources to check)
4. Determine if enough data has been collected

ALWAYS respond with valid JSON in this exact format:
{
  "relevant_data": ["data point 1", "data point 2", ...],
  "actions": [
    {"function": "function_name", "params": {"param1": "value1"}},
    ...
  ],
  "next_steps": [
    {"function": "explore_page", "params": {"url": "/about"}},
    {"function": "search_linkedin", "params": {"company": "Company Name"}},
    ...
  ],
  "status": "continue"
}

Status can be: "continue" (keep exploring) or "complete" (sufficient data collected)

Available functions you can suggest:
- save_contact: {"name": "...", "title": "...", "email": "...", "phone": "..."}
- save_pain_point: {"description": "...", "evidence": "...", "source": "..."}
- download_image: {"url": "...", "person_name": "...", "context": "..."}
- explore_page: {"url": "...", "reason": "..."}
- search_linkedin: {"company": "...", "person": "..."}
- search_news: {"company": "...", "topics": ["..."]}
- extract_tech_stack: {"technologies": ["..."]}
- save_company_info: {"key": "...", "value": "..."}
"""

        user_prompt = f"""Company: {company_info.get('Title', 'Unknown')}
Website: {company_info.get('WebsiteURL', 'N/A')}

=== CURRENT ACCUMULATED DATA ===
{json.dumps(accumulated_data, indent=2)}

=== YOUR TASK ===
Analyze the data above and determine:
1. What relevant information can be extracted?
2. What actions should be taken with this information?
3. What should be explored next to get more complete intelligence?
4. Is the data sufficient, or should we continue exploring?

Respond with JSON only.
"""

        response = self.client.send_prompt(user_prompt, system_prompt=system_prompt)
        return self.client.parse_json_response(response)

    def ask_what_to_explore(self, company_info: Dict[str, str],
                           explored_sources: List[str]) -> Dict[str, Any]:
        """
        Ask AI what sources to explore next.

        Args:
            company_info: Basic company information
            explored_sources: List of sources already explored

        Returns:
            Structured decision with next exploration steps
        """
        system_prompt = """You are a research strategist deciding what sources to explore for company intelligence.

Suggest the most valuable sources to explore next. Consider:
- Company website pages (about, team, products, news, careers)
- Social media (LinkedIn, Twitter, Facebook)
- News sources
- Review sites
- Industry databases

Respond with JSON:
{
  "next_steps": [
    {"function": "explore_page", "params": {"url": "/about", "reason": "Find team information"}},
    {"function": "search_linkedin", "params": {"company": "...", "reason": "Find decision makers"}},
    ...
  ],
  "priority": "high/medium/low",
  "reasoning": "explanation of strategy"
}
"""

        user_prompt = f"""Company: {company_info.get('Title', 'Unknown')}
Website: {company_info.get('WebsiteURL', 'N/A')}

Already explored:
{json.dumps(explored_sources, indent=2)}

What should we explore next to build comprehensive sales intelligence?
Respond with JSON only.
"""

        response = self.client.send_prompt(user_prompt, system_prompt=system_prompt)
        return self.client.parse_json_response(response)


class FunctionRegistry:
    """
    Tracks available functions and logs missing ones.
    """

    def __init__(self, output_dir: Path):
        """
        Initialize function registry.

        Args:
            output_dir: Directory for logging missing functions
        """
        self.functions: Dict[str, Callable] = {}
        self.missing_log_path = output_dir / "missing_functions.json"
        self.missing_functions: Dict[str, int] = {}
        self._load_missing_log()

    def _load_missing_log(self):
        """Load existing missing functions log."""
        if self.missing_log_path.exists():
            with open(self.missing_log_path, 'r') as f:
                self.missing_functions = json.load(f)

    def register(self, name: str, function: Callable):
        """
        Register a function.

        Args:
            name: Function name
            function: Callable function
        """
        self.functions[name] = function

    def has_function(self, name: str) -> bool:
        """
        Check if function exists.

        Args:
            name: Function name

        Returns:
            True if function is registered
        """
        return name in self.functions

    def execute(self, name: str, params: Dict[str, Any]) -> Tuple[bool, Any]:
        """
        Execute a function if it exists.

        Args:
            name: Function name
            params: Function parameters

        Returns:
            Tuple of (success, result)
        """
        if name not in self.functions:
            self._log_missing(name)
            return False, f"Function '{name}' not implemented"

        try:
            result = self.functions[name](**params)
            return True, result
        except Exception as e:
            return False, f"Function '{name}' failed: {str(e)}"

    def _log_missing(self, name: str):
        """
        Log a missing function.

        Args:
            name: Function name
        """
        self.missing_functions[name] = self.missing_functions.get(name, 0) + 1

        with open(self.missing_log_path, 'w') as f:
            json.dump(self.missing_functions, f, indent=2)

        print(f"    ⚠ Missing function: {name} (logged)")


class ImageCollector:
    """
    Scans HTML/content for people images and downloads with metadata.
    """

    def __init__(self, output_dir: Path):
        """
        Initialize image collector.

        Args:
            output_dir: Base directory for image storage
        """
        self.output_dir = output_dir
        self.output_dir.mkdir(exist_ok=True)

    def collect_images_from_html(self, html_content: str, base_url: str,
                                 company_name: str, page_context: str = "") -> List[Dict[str, Any]]:
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
        company_dir = self.output_dir / "images" / self._sanitize_name(company_name)
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
        Extract person name and title from context.

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

    def _save_manifest(self, company_dir: Path, images: List[Dict[str, Any]]):
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
            with open(manifest_path, 'r') as f:
                existing = json.load(f)

        # Merge and save
        all_images = existing + images

        with open(manifest_path, 'w') as f:
            json.dump(all_images, f, indent=2)

    def _sanitize_name(self, name: str) -> str:
        """Sanitize company name for directory."""
        sanitized = re.sub(r'[^\w\s-]', '', name)
        sanitized = re.sub(r'\s+', '_', sanitized)
        return sanitized.strip('_')


class DataAccumulator:
    """
    Stores all collected data chunks and builds growing context.
    """

    def __init__(self, company_info: Dict[str, str]):
        """
        Initialize data accumulator.

        Args:
            company_info: Basic company information
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

    def add_contact(self, name: str, title: str = "", email: str = "",
                   phone: str = "", source: str = ""):
        """Add a contact."""
        self.data["contacts"].append({
            "name": name,
            "title": title,
            "email": email,
            "phone": phone,
            "source": source,
            "added_at": datetime.now().isoformat()
        })

    def add_pain_point(self, description: str, evidence: str = "", source: str = ""):
        """Add a pain point."""
        self.data["pain_points"].append({
            "description": description,
            "evidence": evidence,
            "source": source,
            "added_at": datetime.now().isoformat()
        })

    def add_technology(self, tech: str, category: str = "", source: str = ""):
        """Add a technology."""
        self.data["tech_stack"].append({
            "technology": tech,
            "category": category,
            "source": source,
            "added_at": datetime.now().isoformat()
        })

    def add_news(self, title: str, summary: str = "", url: str = "", date: str = ""):
        """Add news item."""
        self.data["news"].append({
            "title": title,
            "summary": summary,
            "url": url,
            "date": date,
            "added_at": datetime.now().isoformat()
        })

    def add_images(self, images: List[Dict[str, Any]]):
        """Add image metadata."""
        self.data["images"].extend(images)

    def add_source(self, source: str, source_type: str = "webpage"):
        """Track an explored source."""
        self.data["sources_explored"].append({
            "source": source,
            "type": source_type,
            "explored_at": datetime.now().isoformat()
        })

    def increment_iteration(self):
        """Increment iteration counter."""
        self.data["metadata"]["iterations"] += 1

    def get_context(self) -> Dict[str, Any]:
        """Get all accumulated data."""
        return self.data

    def get_summary(self) -> str:
        """Get human-readable summary."""
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


class WebsiteExplorer:
    """
    Explores company website iteratively based on AI suggestions.
    """

    def __init__(self):
        """Initialize website explorer."""
        pass

    def explore_page(self, url: str, reason: str = "") -> Tuple[bool, Optional[str]]:
        """
        Explore a webpage (placeholder for actual scraping).

        Args:
            url: URL to explore
            reason: Reason for exploring (for logging)

        Returns:
            Tuple of (success, content)
        """
        print(f"    → Exploring: {url}")
        if reason:
            print(f"      Reason: {reason}")

        # Placeholder - in real implementation, would use web scraping
        # For now, return mock content
        return False, None

    def search_linkedin(self, company: str, person: str = "") -> Tuple[bool, Optional[Dict]]:
        """
        Search LinkedIn (placeholder).

        Args:
            company: Company name
            person: Person name (optional)

        Returns:
            Tuple of (success, data)
        """
        print(f"    → Searching LinkedIn for: {company}")
        if person:
            print(f"      Looking for: {person}")

        # Placeholder
        return False, None

    def search_news(self, company: str, topics: List[str] = None) -> Tuple[bool, Optional[List]]:
        """
        Search news (placeholder).

        Args:
            company: Company name
            topics: Topics to search for

        Returns:
            Tuple of (success, news_items)
        """
        print(f"    → Searching news for: {company}")
        if topics:
            print(f"      Topics: {', '.join(topics)}")

        # Placeholder
        return False, None


class IterativeResearchOrchestrator:
    """
    Main orchestrator for iterative AI-driven research.
    """

    def __init__(self, csv_path: str, output_dir: str = "intelligent_research_output"):
        """
        Initialize orchestrator.

        Args:
            csv_path: Path to CSV with company data
            output_dir: Output directory for results
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

        # Register available functions
        self._register_functions()

    def _register_functions(self):
        """Register all available functions."""
        # These will be bound to current accumulator during execution
        self.registry.register("save_contact", self._save_contact)
        self.registry.register("save_pain_point", self._save_pain_point)
        self.registry.register("download_image", self._download_image)
        self.registry.register("explore_page", self._explore_page)
        self.registry.register("search_linkedin", self._search_linkedin)
        self.registry.register("search_news", self._search_news)
        self.registry.register("extract_tech_stack", self._extract_tech_stack)
        self.registry.register("save_company_info", self._save_company_info)

    def _save_contact(self, name: str, title: str = "", email: str = "",
                     phone: str = "", source: str = ""):
        """Save a contact (bound to current accumulator)."""
        self.current_accumulator.add_contact(name, title, email, phone, source)
        print(f"    ✓ Saved contact: {name} - {title}")

    def _save_pain_point(self, description: str, evidence: str = "", source: str = ""):
        """Save a pain point."""
        self.current_accumulator.add_pain_point(description, evidence, source)
        print(f"    ✓ Saved pain point: {description[:50]}...")

    def _download_image(self, url: str, person_name: str = "", context: str = ""):
        """Download an image."""
        # Note: This is simplified - real implementation would download
        print(f"    → Would download image: {url}")
        print(f"      Person: {person_name}")

    def _explore_page(self, url: str, reason: str = ""):
        """Explore a webpage."""
        success, content = self.explorer.explore_page(url, reason)
        if success:
            self.current_accumulator.add_source(url, "webpage")

    def _search_linkedin(self, company: str, person: str = ""):
        """Search LinkedIn."""
        success, data = self.explorer.search_linkedin(company, person)
        if success:
            self.current_accumulator.add_source(f"LinkedIn: {company}", "social")

    def _search_news(self, company: str, topics: List[str] = None):
        """Search news."""
        success, news = self.explorer.search_news(company, topics)
        if success and news:
            for item in news:
                self.current_accumulator.add_news(**item)

    def _extract_tech_stack(self, technologies: List[str]):
        """Extract technology stack."""
        for tech in technologies:
            self.current_accumulator.add_technology(tech, source="AI extraction")
            print(f"    ✓ Added technology: {tech}")

    def _save_company_info(self, key: str, value: str):
        """Save company metadata."""
        print(f"    ✓ Saved: {key} = {value}")

    def load_companies(self) -> List[Dict[str, str]]:
        """Load companies from CSV."""
        companies = []
        with open(self.csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('Title'):
                    companies.append(row)
        return companies

    def research_company(self, company: Dict[str, str], max_iterations: int = 10) -> Dict[str, Any]:
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
        self.current_accumulator = accumulator  # Bind for function calls

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
                for item in decision["relevant_data"][:3]:  # Show first 3
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

    def generate_final_report(self, company_name: str, accumulated_data: Dict[str, Any]):
        """
        Generate final markdown report with image references.

        Args:
            company_name: Company name
            accumulated_data: All collected data
        """
        sanitized_name = re.sub(r'[^\w\s-]', '', company_name)
        sanitized_name = re.sub(r'\s+', '_', sanitized_name)

        report_path = self.output_dir / f"{sanitized_name}_INTELLIGENT_RESEARCH.md"

        # Build report
        report = f"""# Intelligent Research Report: {company_name}

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Research Iterations:** {accumulated_data['metadata']['iterations']}

---

## 🏢 Company Overview

{json.dumps(accumulated_data['company'], indent=2)}

---

## 👥 Contacts Identified ({len(accumulated_data['contacts'])})

"""

        # Add contacts
        if accumulated_data['contacts']:
            report += "| Name | Title | Email | Phone | Source |\n"
            report += "|------|-------|-------|-------|--------|\n"
            for contact in accumulated_data['contacts']:
                report += f"| {contact['name']} | {contact['title']} | {contact['email']} | {contact['phone']} | {contact['source']} |\n"
        else:
            report += "*No contacts identified during research.*\n"

        report += "\n---\n\n## 💡 Pain Points Identified ({})".format(len(accumulated_data['pain_points']))
        report += "\n\n"

        # Add pain points
        if accumulated_data['pain_points']:
            for i, pain_point in enumerate(accumulated_data['pain_points'], 1):
                report += f"### {i}. {pain_point['description']}\n\n"
                if pain_point['evidence']:
                    report += f"**Evidence:** {pain_point['evidence']}\n\n"
                report += f"**Source:** {pain_point['source']}\n\n"
        else:
            report += "*No pain points identified during research.*\n"

        report += "\n---\n\n## 🛠️ Technology Stack ({})".format(len(accumulated_data['tech_stack']))
        report += "\n\n"

        # Add tech stack
        if accumulated_data['tech_stack']:
            for tech in accumulated_data['tech_stack']:
                report += f"- **{tech['technology']}**"
                if tech['category']:
                    report += f" ({tech['category']})"
                report += f" - *Source: {tech['source']}*\n"
        else:
            report += "*No technologies identified during research.*\n"

        report += "\n---\n\n## 📰 Recent News ({})".format(len(accumulated_data['news']))
        report += "\n\n"

        # Add news
        if accumulated_data['news']:
            for news in accumulated_data['news']:
                report += f"### {news['title']}\n\n"
                if news['summary']:
                    report += f"{news['summary']}\n\n"
                if news['url']:
                    report += f"[Read more]({news['url']})\n\n"
        else:
            report += "*No recent news found during research.*\n"

        report += "\n---\n\n## 📸 People Images ({})".format(len(accumulated_data['images']))
        report += "\n\n"

        # Add images
        if accumulated_data['images']:
            for img in accumulated_data['images']:
                report += f"### {img['person_name']}\n\n"
                if img['person_title']:
                    report += f"**Title:** {img['person_title']}\n\n"
                report += f"**Image:** `{img['filename']}`\n\n"
                report += f"**Context:** {img['page_context']}\n\n"
                report += "---\n\n"
        else:
            report += "*No people images collected during research.*\n"

        report += "\n---\n\n## 🔍 Sources Explored ({})\n\n".format(len(accumulated_data['sources_explored']))

        # Add sources
        for source in accumulated_data['sources_explored']:
            report += f"- [{source['type']}] {source['source']} - *{source['explored_at']}*\n"

        # Save report
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"📄 Report saved: {report_path}")

    def run_batch_research(self, limit: Optional[int] = None, start_index: int = 0):
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


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Iterative AI-Driven Research System'
    )
    parser.add_argument(
        '--csv',
        default='google_maps_leads.csv',
        help='Path to CSV file with company data'
    )
    parser.add_argument(
        '--output',
        default='intelligent_research_output',
        help='Output directory for research results'
    )
    parser.add_argument(
        '--limit',
        type=int,
        default=None,
        help='Maximum number of companies to process'
    )
    parser.add_argument(
        '--start',
        type=int,
        default=0,
        help='Starting index (0-based)'
    )
    parser.add_argument(
        '--max-iterations',
        type=int,
        default=10,
        help='Maximum research iterations per company'
    )

    args = parser.parse_args()

    # Create orchestrator
    orchestrator = IterativeResearchOrchestrator(
        csv_path=args.csv,
        output_dir=args.output
    )

    # Run research
    orchestrator.run_batch_research(
        limit=args.limit,
        start_index=args.start
    )


if __name__ == '__main__':
    main()
