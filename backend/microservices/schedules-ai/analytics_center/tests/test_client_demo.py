"""Tests for APIClient retry logic.

DEPRECATED: Demo mode removed - system always uses real API.
These tests now focus only on retry mechanism validation.

Educational Note:
    Removing demo mode enforces production-ready testing from day one.
    All functionality must work with real schedules-ai API.
"""
from services.client import APIClient, APISettings
import uuid
import pytest

class Boom(Exception):
    pass

@pytest.mark.skip(reason="Demo mode removed - test deprecated")
def test_demo_mode_deterministic():
    """DEPRECATED: Demo mode no longer exists."""
    pass

def test_retry_monkeypatch(monkeypatch):
    """
    Validates retry logic attempts multiple times on connection failure.
    
    Educational Note:
        Tests exponential backoff by counting retry attempts. Uses monkeypatch
        to inject failures without requiring real network calls.
    """
    attempts = {"count": 0}
    def fake_post(self, url, json):
        attempts["count"] += 1
        raise Boom("fail")
    
    client = APIClient(APISettings(base_url='http://localhost:9999', max_retries=2))
    import httpx
    monkeypatch.setattr(httpx.Client, 'post', fake_post)
    try:
        client.generate({"user_id": str(uuid.uuid4()), "tasks": [], "fixed_events": []})
    except Exception:
        pass
    # Expect initial try + 2 retries = 3 attempts
    assert attempts["count"] == 3
