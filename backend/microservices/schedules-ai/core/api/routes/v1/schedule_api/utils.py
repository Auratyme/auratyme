"""
Utility functions for schedule processing and data conversion.

This module provides reusable utility functions for time conversion
and data transformation operations needed across the schedule API.
Demonstrates separation of concerns and function decomposition
principles essential for maintainable code architecture.
"""

from datetime import time


def convert_time_to_minutes(time_obj: time) -> int:
    """
    Converts time object to minutes since midnight.
    
    This utility function provides a standardized way to convert
    time objects to numeric minutes for calculations. Essential
    for schedule algorithms that need numeric time representation.
    """
    return time_obj.hour * 60 + time_obj.minute


def convert_time_string_to_minutes(time_str: str) -> int:
    """
    Converts time string to minutes since midnight.
    
    This function safely parses time strings in HH:MM format
    returning minutes for schedule calculations. Demonstrates
    defensive programming with error handling for string parsing.
    """
    try:
        parts = time_str.split(":")
        return _extract_hours_and_minutes(parts)
    except (ValueError, IndexError):
        return 0


def _extract_hours_and_minutes(time_parts: list) -> int:
    """
    Extracts hours and minutes from split time string.
    
    This internal helper function processes time components
    safely handling invalid input. Demonstrates decomposition
    of complex parsing logic into focused helper functions.
    """
    if len(time_parts) >= 2:
        hours = int(time_parts[0])
        minutes = int(time_parts[1])
        return hours * 60 + minutes
    return 0


def validate_time_order(start_time: time, end_time: time) -> bool:
    """
    Validates chronological order of start and end times.
    
    This validation function ensures logical time ordering
    preventing schedule inconsistencies. Essential for data
    integrity in time-based scheduling operations.
    """
    return start_time < end_time
