"""
Cerebras API client for AI research operations.

This module provides a wrapper around the Cerebras API for sending prompts
and parsing structured responses.
"""

import re
import json
import logging
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

# Configure logging
logger = logging.getLogger(__name__)


class GeminiCerebrasClient:
    """
    Wrapper to communicate with Cerebras API.
    Constructs API requests and parses JSON responses.
    """

    def __init__(self, api_key: str, model: str = "llama-3.3-70b", log_dir: str = "ai_logs"):
        """
        Initialize Cerebras API client.

        Args:
            api_key: Cerebras API key
            model: Model to use (default: llama-3.3-70b)
            log_dir: Directory for detailed AI interaction logs

        Raises:
            ValueError: If api_key is empty
        """
        if not api_key:
            raise ValueError("API key cannot be empty")

        self.api_key = api_key
        self.model = model
        self.api_base = "https://api.cerebras.ai/v1"

        # Setup logging directory
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)

        # Request counter for unique log files
        self.request_count = 0

    def send_prompt(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000
    ) -> str:
        """
        Send prompt to Cerebras via API with comprehensive logging.

        Args:
            prompt: User prompt text
            system_prompt: Optional system context
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens in response

        Returns:
            AI response text

        Raises:
            RuntimeError: If API request fails
        """
        self.request_count += 1
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = self.log_dir / f"request_{self.request_count:03d}_{timestamp}.log"

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

        # Log request details
        log_content = [
            "=" * 80,
            f"AI REQUEST #{self.request_count}",
            f"Timestamp: {datetime.now().isoformat()}",
            f"Model: {self.model}",
            "=" * 80,
            "",
            "--- SYSTEM PROMPT ---",
            system_prompt if system_prompt else "(none)",
            "",
            "--- USER PROMPT ---",
            prompt,
            "",
            "--- REQUEST PARAMETERS ---",
            f"Temperature: {temperature}",
            f"Max Tokens: {max_tokens}",
            "",
        ]

        try:
            response = requests.post(
                f"{self.api_base}/chat/completions",
                headers=headers,
                json=payload,
                timeout=120
            )
            response.raise_for_status()

            result = response.json()
            ai_response = result['choices'][0]['message']['content']

            # Log successful response
            log_content.extend([
                "--- AI RESPONSE ---",
                ai_response,
                "",
                "--- RESPONSE METADATA ---",
                f"Status: SUCCESS",
                f"Usage: {json.dumps(result.get('usage', {}), indent=2)}",
                "",
                "=" * 80
            ])

            # Write log file
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(log_content))

            logger.info(f"AI request #{self.request_count} logged to {log_file}")
            print(f"    📝 AI interaction logged: {log_file.name}")

            return ai_response

        except requests.exceptions.Timeout:
            log_content.extend([
                "--- ERROR ---",
                "Cerebras API timed out after 120 seconds",
                "",
                "=" * 80
            ])
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(log_content))
            raise RuntimeError("Cerebras API timed out after 120 seconds")

        except requests.exceptions.HTTPError as e:
            log_content.extend([
                "--- ERROR ---",
                f"HTTP Error: {e.response.status_code}",
                f"Response: {e.response.text}",
                "",
                "=" * 80
            ])
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(log_content))
            raise RuntimeError(f"Cerebras API error: {e.response.text}")

        except Exception as e:
            log_content.extend([
                "--- ERROR ---",
                f"Exception: {type(e).__name__}",
                f"Message: {str(e)}",
                "",
                "=" * 80
            ])
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(log_content))
            raise RuntimeError(f"Cerebras API failed: {str(e)}")

    def parse_json_response(self, response: str) -> Dict[str, Any]:
        """
        Parse JSON from AI response text.

        Handles responses with or without markdown code blocks.

        Args:
            response: Raw AI response text

        Returns:
            Parsed JSON dictionary

        Raises:
            ValueError: If JSON parsing fails
        """
        # Try to extract JSON from code blocks first
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
            raise ValueError(
                f"Failed to parse JSON response: {e}\n"
                f"Response: {response[:500]}"
            )
