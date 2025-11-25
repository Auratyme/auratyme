"""
User profile data extraction utilities for scheduler.

This module provides functions to extract user profile data from
various sources with fallback mechanisms. Demonstrates defensive
programming patterns for handling missing or incomplete data while
maintaining schedule generation reliability.

Educational Note:
    Fallback mechanisms ensure scheduler can operate with partial
    data while still attempting personalization when full profile
    data is available, following graceful degradation principle.
"""

from typing import Dict, Any, Optional


def extract_profile_data_with_fallback(
    user_profile_data: Optional[Dict[str, Any]],
    preferences: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Extracts user profile data with preferences fallback.
    
    Attempts to retrieve user profile data from primary source,
    falling back to preferences dictionary if primary is empty.
    Demonstrates defensive data access patterns for robust
    operation with incomplete input data.
    
    Args:
        user_profile_data: Primary source for profile data
        preferences: Fallback source containing profile fields
        
    Returns:
        Dictionary containing available profile data
        
    Educational Note:
        Fallback pattern allows scheduler to function with data
        embedded in different payload locations, improving
        flexibility and backward compatibility.
    """
    primary_data = user_profile_data or {}
    return get_profile_or_fallback(primary_data, preferences)


def get_profile_or_fallback(
    primary_data: Dict[str, Any],
    preferences: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Returns primary data if present, otherwise falls back.
    
    Evaluates primary data availability and returns appropriate
    source based on data presence. Demonstrates conditional
    data source selection for flexible data handling.
    """
    if has_profile_data(primary_data):
        return primary_data
    return extract_from_preferences(preferences)


def has_profile_data(data: Dict[str, Any]) -> bool:
    """
    Checks if dictionary contains meaningful profile data.
    
    Determines whether a dictionary has actual content beyond
    being an empty container. Demonstrates data validation
    for informed fallback decisions.
    """
    return bool(data)


def extract_from_preferences(preferences: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extracts profile fields from preferences structure.
    
    Retrieves user profile data that may be embedded in
    preferences dictionary under chronotype key. Handles
    nested data access with safe fallback to empty dict.
    
    Educational Note:
        Accessing nested data requires defensive programming
        to handle missing keys gracefully, preventing runtime
        errors from incomplete input structures.
    """
    chronotype_data = preferences.get("chronotype", {})
    return merge_preferences_data(preferences, chronotype_data)


def merge_preferences_data(
    preferences: Dict[str, Any],
    chronotype_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Merges chronotype data with other preference fields.
    
    Combines chronotype-specific data with general preferences
    to create complete profile data dictionary. Demonstrates
    data composition from multiple sources.
    """
    return {**chronotype_data, **extract_additional_fields(preferences)}


def extract_additional_fields(preferences: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extracts additional profile fields from preferences.
    
    Retrieves non-chronotype profile fields that may exist
    at top level of preferences. Currently returns empty dict
    as placeholder for future field extraction logic.
    
    Educational Note:
        Placeholder function maintains extension point for
        adding more field extraction logic without modifying
        existing code, following open-closed principle.
    """
    return {}
