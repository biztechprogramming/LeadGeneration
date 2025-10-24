"""
AI decision engine for intelligent research.

This module handles AI analysis of accumulated data and generates
structured decisions about next research steps.
"""

import json
from typing import Dict, Any, List

from .cerebras_client import GeminiCerebrasClient


class AIDecisionEngine:
    """
    Sends data to AI and gets structured decisions about what to do next.
    Builds prompts for AI analysis and parses structured responses.
    """

    def __init__(self, client: GeminiCerebrasClient):
        """
        Initialize decision engine.

        Args:
            client: GeminiCerebrasClient instance for API communication
        """
        self.client = client

    def analyze_data(
        self,
        accumulated_data: Dict[str, Any],
        company_info: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Ask AI to analyze current data and suggest next steps.

        Args:
            accumulated_data: All data collected so far
            company_info: Basic company information

        Returns:
            Structured decision with relevant_data, actions, next_steps, status

        Raises:
            RuntimeError: If AI analysis fails
        """
        system_prompt = self._build_analysis_system_prompt()
        user_prompt = self._build_analysis_user_prompt(accumulated_data, company_info)

        response = self.client.send_prompt(user_prompt, system_prompt=system_prompt)
        return self.client.parse_json_response(response)

    def ask_what_to_explore(
        self,
        company_info: Dict[str, str],
        explored_sources: List[str]
    ) -> Dict[str, Any]:
        """
        Ask AI what sources to explore next.

        Args:
            company_info: Basic company information
            explored_sources: List of sources already explored

        Returns:
            Structured decision with next exploration steps

        Raises:
            RuntimeError: If AI request fails
        """
        system_prompt = self._build_exploration_system_prompt()
        user_prompt = self._build_exploration_user_prompt(company_info, explored_sources)

        response = self.client.send_prompt(user_prompt, system_prompt=system_prompt)
        return self.client.parse_json_response(response)

    def _build_analysis_system_prompt(self) -> str:
        """Build system prompt for data analysis."""
        return """You are an intelligent research assistant that analyzes company data and suggests next steps.

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

=== CRITICAL RULES FOR save_contact ===

**VALIDATION REQUIREMENTS (STRICTLY ENFORCED):**
- MUST provide at least ONE of: name OR email
- Phone-only contacts will be REJECTED
- Empty/blank contacts will be REJECTED
- If you see generic text like "Contact Us" without actual person details, DO NOT save

**GOOD EXAMPLES - These WILL be accepted:**
✓ {"name": "John Smith", "title": "CEO", "email": "john@company.com", "phone": "555-1234"}
✓ {"name": "Sales Team", "title": "Sales", "email": "sales@company.com", "phone": "555-1234"}
✓ {"name": "Jane Doe", "title": "VP Engineering", "email": "jane@company.com"}
✓ {"email": "hello@company.com", "phone": "555-1234"}  // Generic contact with email

**BAD EXAMPLES - These WILL be rejected:**
✗ {"phone": "555-1234"}  // Phone only - REJECTED
✗ {"name": "", "email": "", "phone": "555-1234"}  // Empty fields - REJECTED
✗ {"name": " ", "title": " ", "email": " "}  // Whitespace only - REJECTED
✗ {}  // Empty object - REJECTED

**CONTACT EXTRACTION STRATEGY:**
1. Look for ACTUAL person names (e.g., "John Smith", "Jane Doe", "CEO Bob Johnson")
2. Accept department/role contacts IF they have email (e.g., "Sales Team" + sales@company.com)
3. Extract email addresses even if name is not available
4. If you find "Contact: 555-1234" or "Call us: 555-1234" but NO name/email, DO NOT save
5. For forms that say "Email *" or "Phone *", these are INPUT FIELDS not actual contacts - DO NOT save

**QUALITY STANDARDS:**
- Prefer specific people over generic departments
- Prioritize contacts with both name AND email
- Always include the "source" parameter to track where contact was found
- If unsure whether data is valid, err on side of NOT saving (we can always find it again)
"""

    def _build_analysis_user_prompt(
        self,
        accumulated_data: Dict[str, Any],
        company_info: Dict[str, str]
    ) -> str:
        """Build user prompt for data analysis."""
        return f"""Company: {company_info.get('Title', 'Unknown')}
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

    def _build_exploration_system_prompt(self) -> str:
        """Build system prompt for exploration strategy."""
        return """You are a research strategist deciding what sources to explore for company intelligence.

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

    def _build_exploration_user_prompt(
        self,
        company_info: Dict[str, str],
        explored_sources: List[str]
    ) -> str:
        """Build user prompt for exploration strategy."""
        return f"""Company: {company_info.get('Title', 'Unknown')}
Website: {company_info.get('WebsiteURL', 'N/A')}

Already explored:
{json.dumps(explored_sources, indent=2)}

What should we explore next to build comprehensive sales intelligence?
Respond with JSON only.
"""
