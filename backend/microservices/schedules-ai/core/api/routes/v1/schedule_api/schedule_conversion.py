"""
Utility for converting generated schedule items to API response format.

This module provides transformation functions to convert internal
scheduler output into API-compatible response structures. Demonstrates
data adaptation patterns essential for maintaining clean boundaries
between business logic and presentation layers.

Educational Note:
    Separating conversion logic into dedicated utilities promotes
    reusability and testability while keeping response formatting
    functions focused on a single responsibility.
"""

from typing import List, Dict, Any


def _normalize_time_format(time_str: str) -> str:
    """
    Normalizes time string to HH:MM format.
    
    Converts various time formats (HH:MM:SS, HH:MM) to consistent
    HH:MM format required by frontend. Handles Fixed Events that
    may return times with seconds from datetime.time objects.
    
    Args:
        time_str: Time string in HH:MM or HH:MM:SS format
        
    Returns:
        Time string in HH:MM format
        
    Educational Note:
        Frontend validation expects HH:MM format exclusively.
        Backend may return HH:MM:SS from datetime serialization,
        requiring normalization at API boundary for compatibility.
    """
    if not time_str:
        return ""
    
    if len(time_str) == 8 and time_str.count(":") == 2:
        return time_str[:5]
    
    return time_str


def convert_scheduled_items_to_tasks(scheduled_items: List[Dict[str, Any]]) -> List[dict]:
    """
    Converts scheduler output items to API task format.
    
    Transforms internal schedule item structure to API response
    format by extracting required fields and applying field
    name mappings. Demonstrates adapter pattern for maintaining
    compatibility between internal and external data formats.
    
    Args:
        scheduled_items: List of schedule items from internal generator
        
    Returns:
        List of task dictionaries formatted for API response
        
    Educational Note:
        Field mapping (name→task) handles semantic differences
        between internal implementation and API contract while
        maintaining backward compatibility with existing clients.
    """
    return [_transform_single_item(item) for item in scheduled_items]


def _transform_single_item(item: Dict[str, Any]) -> dict:
    """
    Transforms a single schedule item to API format.
    
    Extracts and maps fields from internal representation to
    API response structure with proper field naming and type
    handling. Demonstrates single-responsibility transformation
    logic for maintainable data conversion operations.
    """
    return _build_task_dict(item)


def _build_task_dict(item: Dict[str, Any]) -> dict:
    """
    Builds task dictionary with mapped field names.
    
    Creates API-compatible task dictionary by extracting fields
    and applying semantic name mappings. Handles missing fields
    gracefully with sensible defaults.
    """
    task_name = _extract_task_name(item)
    return _create_response_dict(item, task_name)


def _extract_task_name(item: Dict[str, Any]) -> str:
    """
    Extracts task name from schedule item.
    
    Retrieves task name field handling both internal naming
    conventions (name) and API conventions (task). Provides
    fallback for missing values to ensure robust operation.
    """
    return item.get("name") or item.get("task", "Unknown Task")


def _create_response_dict(item: Dict[str, Any], task_name: str) -> dict:
    """
    Creates final response dictionary structure.
    
    Assembles complete response dictionary with all required
    fields using extracted and transformed values. Maintains
    consistent structure for API client consumption. Normalizes
    time formats to HH:MM for frontend compatibility.
    
    Educational Note:
        Time normalization ensures consistent data format across
        different schedule item sources (solver tasks use HH:MM,
        fixed events may use HH:MM:SS from datetime serialization).
    """
    result = {
        "start_time": _normalize_time_format(item.get("start_time", "")),
        "end_time": _normalize_time_format(item.get("end_time", "")),
        "task": task_name,
        "type": item.get("type", "task")
    }
    
    if item.get("next_day"):
        result["next_day"] = True
    
    if item.get("start_time_previous_day"):
        result["start_time_previous_day"] = True
    
    if item.get("end_time_next_day"):
        result["end_time_next_day"] = True
    
    return result
