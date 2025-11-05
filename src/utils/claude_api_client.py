"""
Centralized Claude API client for all API interactions.
"""

import json
import urllib.request
from typing import Optional


class ClaudeAPIClient:
    """
    Centralized client for Claude API calls.

    Handles:
    - Configuration from settings
    - HTTP request construction
    - Error handling
    - Timeout management
    """

    API_URL = "https://api.anthropic.com/v1/messages"
    API_VERSION = "2023-06-01"

    def __init__(self, settings):
        """
        Initialize API client.

        Args:
            settings: Settings object with get_claude_config() method
        """
        self.settings = settings

    def call(self, context: str, system_prompt: Optional[str] = None,
             timeout: int = 60) -> str:
        """
        Call Claude API with configured settings.

        Args:
            context: User message/context to send
            system_prompt: Optional system prompt for guidance
            timeout: Request timeout in seconds (default 60)

        Returns:
            Claude's response text

        Raises:
            Exception: If API key not configured or request fails
        """
        # Get configuration
        config = self.settings.get_claude_config()

        if not config.get('api_key'):
            raise Exception("Claude API key not configured. Go to Settings > Claude Settings.")

        api_key = config['api_key']
        model = config['model']
        max_tokens = config['max_tokens']

        # Build request
        headers = {
            "x-api-key": api_key,
            "anthropic-version": self.API_VERSION,
            "content-type": "application/json"
        }

        data = {
            "model": model,
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": context}]
        }

        # Add system prompt if provided
        if system_prompt:
            data["system"] = system_prompt

        # Make request
        req = urllib.request.Request(
            self.API_URL,
            data=json.dumps(data).encode('utf-8'),
            headers=headers,
            method='POST'
        )

        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                result = json.loads(response.read().decode('utf-8'))
                return result['content'][0]['text']
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            raise Exception(f"API Error ({e.code}): {error_body}")
        except urllib.error.URLError as e:
            raise Exception(f"Network Error: {e.reason}")
        except Exception as e:
            raise Exception(f"API call failed: {e}")

    def is_configured(self) -> bool:
        """
        Check if API is configured (has API key).

        Returns:
            True if API key is set
        """
        api_key = self.settings.get_claude_api_key()
        return bool(api_key)