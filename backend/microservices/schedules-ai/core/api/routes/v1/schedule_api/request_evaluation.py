"""
Request context evaluation utilities.

This module provides functions to determine request processing
strategy based on request characteristics. Demonstrates conditional
processing patterns for API endpoints while maintaining clean
separation between demonstration and production flows.

Educational Note:
    Conditional processing allows API to serve both demonstration
    and production use cases through same endpoint, improving
    testability while maintaining production reliability.
"""

from typing import Optional


def should_use_real_schedule_generation(
    request_data: Optional[object],
    request_path: str
) -> bool:
    """
    Determines if real schedule generation should be used.
    
    Evaluates request context to decide between demonstration
    and production processing paths. Returns True when request
    contains actual user data requiring real generation logic.
    
    Args:
        request_data: Incoming request data object
        request_path: Request URL path for context
        
    Returns:
        bool: True if real generation should be used, False for demo
        
    Educational Note:
        Using presence of request_data as primary signal ensures
        that any request with actual payload gets real processing,
        making demo mode explicit (None request_data).
    """
    return request_data is not None


def is_demonstration_request(
    request_data: Optional[object]
) -> bool:
    """
    Checks if request should use demonstration mode.
    
    Identifies requests intended for demonstration purposes
    based on absence of actual user data. Demonstrates
    explicit opt-in pattern for special processing modes.
    """
    return request_data is None
