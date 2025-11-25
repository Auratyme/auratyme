"""
Response formatting utilities for schedule API endpoints.

This module handles the transformation of internal schedule data
into API response formats. Provides standardized response structure
and formatting for consistent client consumption while demonstrating
data presentation layer separation patterns.
"""

from typing import List

from .models import SimplifiedScheduleTask, ScheduleSuccessResponse


def create_success_response_with_tasks(tasks: List[dict]) -> ScheduleSuccessResponse:
    """
    Creates standardized success response with task data.
    
    This function wraps task data in a consistent response
    structure providing metadata and standardized messaging.
    Demonstrates response standardization patterns essential
    for API consistency and client predictability.
    """
    task_objects = _convert_tasks_to_response_objects(tasks)
    
    return ScheduleSuccessResponse(
        message="Schedule received successfully.",
        data={"tasks": task_objects}
    )


def _convert_tasks_to_response_objects(tasks: List[dict]) -> List[SimplifiedScheduleTask]:
    """
    Converts task dictionaries to response model objects.
    
    This helper function transforms internal task representations
    into structured response objects with proper validation.
    Demonstrates data transformation patterns for maintaining
    type safety in API responses while ensuring data integrity.
    """
    return [SimplifiedScheduleTask(**task) for task in tasks]


def get_demonstration_schedule_tasks() -> List[dict]:
    """
    Provides demonstration schedule for API testing.
    
    This function returns a comprehensive example schedule
    demonstrating the expected output format and structure.
    Serves as both documentation and testing data while
    showing realistic schedule generation capabilities.
    """
    return [
        {"start_time": "00:00", "end_time": "06:00", "task": "Sleep"},
        {"start_time": "06:00", "end_time": "07:00", "task": "Morning Routine"},
        {"start_time": "07:00", "end_time": "07:30", "task": "Quick Emails Check"},
        {"start_time": "07:30", "end_time": "08:00", "task": "Commute To Office"},
        {"start_time": "08:00", "end_time": "09:00", "task": "Focus Work Session"},
        {"start_time": "09:00", "end_time": "10:00", "task": "Plan Team Meeting Agenda"},
        {"start_time": "10:00", "end_time": "10:45", "task": "Weekly Team Meeting"},
        {"start_time": "10:45", "end_time": "12:00", "task": "Prepare Monthly Report"},
        {"start_time": "12:00", "end_time": "12:45", "task": "Lunch"},
        {"start_time": "12:45", "end_time": "14:00", "task": "Review Budget Proposal"},
        {"start_time": "14:00", "end_time": "15:00", "task": "Client Presentation"},
        {"start_time": "15:00", "end_time": "15:45", "task": "Check Project Status"},
        {"start_time": "15:45", "end_time": "16:00", "task": "Answer Emails"},
        {"start_time": "16:00", "end_time": "16:30", "task": "Commute From Office"},
        {"start_time": "16:30", "end_time": "17:30", "task": "Relaxation Time"},
        {"start_time": "17:30", "end_time": "19:00", "task": "Gym Workout"},
        {"start_time": "19:00", "end_time": "19:30", "task": "Dinner"},
        {"start_time": "19:30", "end_time": "20:00", "task": "Learning Time"},
        {"start_time": "20:00", "end_time": "21:00", "task": "Personal Projects"},
        {"start_time": "21:00", "end_time": "21:30", "task": "Social Time"},
        {"start_time": "21:30", "end_time": "22:30", "task": "Evening Routine"},
        {"start_time": "22:30", "end_time": "00:00", "task": "Sleep"}
    ]

