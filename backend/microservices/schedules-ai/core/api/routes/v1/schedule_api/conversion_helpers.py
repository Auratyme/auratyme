"""
Helper utilities for schedule response conversion.

This module provides utility functions for converting generated
schedule objects into API response format. Demonstrates separation
of conversion logic from business logic for improved testability
and maintainability.
"""

from typing import List
from src.core.scheduler import GeneratedSchedule
from .schedule_conversion import convert_scheduled_items_to_tasks
from .sleep_corrector import correct_sleep_blocks


def convert_schedule_to_response_tasks(generated_schedule: GeneratedSchedule) -> List[dict]:
    """
    Converts GeneratedSchedule object to API response task list.
    
    Extracts scheduled items from the generated schedule and
    transforms them into API-compatible task dictionaries.
    Corrects sleep blocks to create TWO full blocks crossing midnight
    (previous night + tonight) and adds morning/evening routines
    with durations from user preferences.
    
    Args:
        generated_schedule: Internal schedule generation result
        
    Returns:
        List of task dictionaries ready for API response
        
    Educational Note:
        Daily schedule spans ~3 calendar days via sleep blocks:
        - Previous night sleep (ends today morning)
        - Today's activities with routines
        - Tonight's sleep (starts today evening)
        This represents realistic daily schedule boundaries.
    """
    raw_items = generated_schedule.scheduled_items
    sleep_rec = generated_schedule.sleep_recommendation
    
    if sleep_rec is None:
        return convert_scheduled_items_to_tasks(raw_items)
    
    routine_prefs = generated_schedule.routine_preferences
    if not routine_prefs:
        routine_prefs = {"morning_duration_minutes": 30, "evening_duration_minutes": 45}
    
    corrected_items = correct_sleep_blocks(raw_items, sleep_rec, routine_prefs)
    
    return convert_scheduled_items_to_tasks(corrected_items)
