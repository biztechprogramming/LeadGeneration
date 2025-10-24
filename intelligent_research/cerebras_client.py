"""
Cerebras API client for AI research operations.

This module provides a wrapper around the Cerebras API for sending prompts
and parsing structured responses.
"""

import re
import json
import requests
from typing import Dict, Any, Optional


class GeminiCerebrasClient:
    """
    Wrapper to communicate with Cerebras API.
    Constructs API requests and parses JSON responses.
    """

    def __init__(self, api_key: str, model: str = "llama-3.3-70b"):
        """
        Initialize Cerebras API client.

        Args:
            api_key: Cerebras API key
            model: Model to use (default: llama-3.3-70b)

        Raises:
            ValueError: If api_key is empty
        """
        if not api_key:
            raise ValueError("API key cannot be empty")

        self.api_key = api_key
        self.model = model
        self.api_base = "https://api.cerebras.ai/v1"

    def send_prompt(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000
    ) -> str:
        """
        Send prompt to Cerebras via API.

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
