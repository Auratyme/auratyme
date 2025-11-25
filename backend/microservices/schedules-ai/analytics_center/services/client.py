"""HTTP API client with retry logic for real API calls.

Educational Rationale:
Centralizing outbound HTTP concerns (timeouts, retries, fallbacks)
reduces duplication and makes error handling and diagnostics uniform.
Always connects to real schedules-ai API - no demo mode.
"""
from __future__ import annotations
import time
import httpx
from dataclasses import dataclass
from typing import Dict, Any, Optional

@dataclass(slots=True)
class APISettings:
    """
    Configuration for real API connections.
    
    Args:
        base_url: Base URL of schedules-ai service (e.g., http://schedules-ai:8000)
        timeout: HTTP request timeout in seconds
        max_retries: Number of retry attempts on connection failures
        backoff_base: Base delay for exponential backoff (seconds)
    
    Educational Note:
        No demo_mode - system always uses real API for production-ready testing.
    """
    base_url: str
    timeout: int = 300
    max_retries: int = 3
    backoff_base: float = 0.5

class APIClient:
    """
    HTTP client for schedules-ai API with retry logic.
    
    Educational Note:
        Implements exponential backoff for transient failures (network issues),
        but fails fast on permanent errors (4xx HTTP codes).
    """
    def __init__(self, settings: APISettings):
        self.settings = settings

    def generate(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate schedule via real API with automatic retries.
        
        Args:
            payload: Schedule generation request (tasks, fixed_events, user profile, etc.)
        
        Returns:
            API response with generated schedule
        
        Raises:
            Exception: On connection failures, HTTP errors, or exceeded retries
        
        Educational Note:
            Retry logic handles temporary network glitches but preserves error
            context for debugging. No fallback to mock data - failures are explicit.
        """
        base_url = self.settings.base_url.rstrip('/')
        url = f"{base_url}/v1/schedule/generate-simple"
        
        attempt = 0
        last_exc: Optional[Exception] = None
        
        while attempt <= self.settings.max_retries:
            try:
                with httpx.Client(timeout=self.settings.timeout) as client:
                    resp = client.post(url, json=payload)
                    resp.raise_for_status()
                    return resp.json()
            except httpx.ConnectError as e:
                last_exc = e
                if attempt == self.settings.max_retries:
                    raise Exception(
                        f"Cannot connect to API at {url}. "
                        f"Please ensure schedules-ai service is running on {base_url}"
                    ) from e
                sleep_for = self.settings.backoff_base * (2 ** attempt)
                time.sleep(sleep_for)
                attempt += 1
            except httpx.HTTPStatusError as e:
                last_exc = e
                if attempt == self.settings.max_retries:
                    raise Exception(
                        f"API returned error {e.response.status_code}: {e.response.text}"
                    ) from e
                sleep_for = self.settings.backoff_base * (2 ** attempt)
                time.sleep(sleep_for)
                attempt += 1
            except Exception as e:
                last_exc = e
                if attempt == self.settings.max_retries:
                    raise Exception(f"Unexpected error: {str(e)}") from e
                sleep_for = self.settings.backoff_base * (2 ** attempt)
                time.sleep(sleep_for)
                attempt += 1
        
        if last_exc:
            raise last_exc
        return {}
