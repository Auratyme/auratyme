"""
Example data generators for schedule API demonstrations.

This module provides comprehensive example datasets for testing
and demonstration of the schedule generation API. Contains realistic
user profiles, tasks, and preferences that showcase the system's
capabilities while serving as educational examples of data structures.
"""

from datetime import date, datetime, time, timedelta, timezone
from typing import Dict, Any, List
from uuid import UUID

from src.core.task import Task, TaskPriority, EnergyLevel
from src.core.scheduler import ScheduleInputData


def create_example_schedule_input() -> ScheduleInputData:
    """
    Creates comprehensive example input for schedule generation.
    
    This function generates a realistic example containing tasks,
    user profile, preferences, and contextual data. Demonstrates
    the complete data structure required for intelligent schedule
    generation while serving as documentation for API consumers.
    """
    user_id = UUID("f0e1d2c3-b4a5-6789-0123-456789abcdef")
    target_date = date(2025, 5, 27)
    
    return ScheduleInputData(
        tasks=_create_example_tasks(target_date),
        user_id=user_id,
        target_date=target_date,
        fixed_events_input=_create_example_fixed_events(),
        preferences=_create_example_preferences(),
        user_profile_data=_create_example_user_profile(),
        wearable_data_today=_create_example_wearable_data(),
        historical_data=_create_example_historical_data()
    )


def _create_example_tasks(target_date: date) -> List[Task]:
    """
    Creates realistic example tasks for demonstration.
    
    This function generates a diverse set of tasks with
    varying priorities, durations, and energy requirements.
    Demonstrates task modeling patterns and provides examples
    of how different task types should be structured.
    """
    base_datetime = datetime.combine(target_date, time(0, 0), timezone.utc)
    
    return [
        Task(
            title="Prepare Monthly Report",
            priority=TaskPriority.HIGH,
            energy_level=EnergyLevel.HIGH,
            duration=timedelta(hours=2, minutes=30),
            deadline=base_datetime.replace(hour=17),
            earliest_start=base_datetime.replace(hour=9)
        ),
        Task(
            title="Review Budget Proposal",
            priority=TaskPriority.HIGH,
            energy_level=EnergyLevel.HIGH,
            duration=timedelta(hours=1, minutes=30),
            deadline=base_datetime.replace(hour=18),
            earliest_start=base_datetime.replace(hour=13, minute=45)
        )
    ]


def _create_example_fixed_events() -> List[Dict[str, str]]:
    """
    Creates example fixed events for schedule constraints.
    
    This function generates realistic fixed events including
    commutes, meetings, and appointments that serve as
    immutable constraints in schedule generation. Demonstrates
    how external commitments are integrated into scheduling.
    """
    return [
        {"id": "commute_to_office", "start_time": "07:30", "end_time": "08:00"},
        {"id": "weekly_team_meeting", "start_time": "10:00", "end_time": "10:45"},
        {"id": "client_presentation", "start_time": "14:00", "end_time": "15:00"},
        {"id": "commute_from_office", "start_time": "16:00", "end_time": "16:30"}
    ]


def _create_example_preferences() -> Dict[str, Any]:
    """
    Creates comprehensive user preference settings.
    
    This function demonstrates the full range of user
    preferences that influence schedule generation including
    work patterns, meal times, and activity goals. Essential
    for understanding personalization capabilities.
    """
    return {
        "preferred_wake_time": "06:00",
        "sleep_need_scale": 70,
        "chronotype_scale": 65,
        "work": _create_work_preferences(),
        "meals": _create_meal_preferences(),
        "routines": _create_routine_preferences(),
        "activity_goals": _create_activity_goals()
    }


def _create_work_preferences() -> Dict[str, Any]:
    """
    Creates work-related preference settings.
    
    This helper function demonstrates work schedule preferences
    including start/end times, commute considerations, and
    work location flexibility. Essential for workplace
    schedule optimization and work-life balance.
    """
    return {
        "start_time": "08:00",
        "end_time": "16:00",
        "commute_minutes": 30,
        "location": "Downtown Office / Home Office",
        "type": "hybrid"
    }


def _create_meal_preferences() -> Dict[str, Any]:
    """
    Creates meal timing and duration preferences.
    
    This function demonstrates how meal preferences are
    structured for schedule integration. Shows the importance
    of considering biological needs in intelligent scheduling
    systems for maintaining energy and productivity.
    """
    return {
        "breakfast_duration_minutes": 30,
        "lunch_duration_minutes": 45,
        "dinner_duration_minutes": 30
    }


def _create_routine_preferences() -> Dict[str, Any]:
    """
    Creates morning and evening routine preferences.
    
    This function demonstrates how personal routines are
    integrated into schedule generation. Shows consideration
    for transition times and personal preparation needs
    essential for realistic schedule adherence.
    """
    return {
        "morning_duration_minutes": 60,
        "evening_duration_minutes": 60
    }


def _create_activity_goals() -> List[Dict[str, Any]]:
    """
    Creates activity and wellness goal preferences.
    
    This function demonstrates how wellness and personal
    development goals are integrated into daily scheduling.
    Shows the holistic approach to schedule generation
    beyond just work tasks and appointments.
    """
    return [
        {
            "name": "Gym Workout",
            "duration_minutes": 90,
            "frequency": "Mon,Wed,Fri",
            "preferred_time": ["evening"]
        },
        {
            "name": "Focus Work Session",
            "duration_minutes": 60,
            "frequency": "daily",
            "preferred_time": ["morning"]
        }
    ]


def _create_example_user_profile() -> Dict[str, Any]:
    """
    Creates example user profile information.
    
    This function provides demographic and role information
    that influences schedule personalization. Demonstrates
    how user characteristics inform scheduling decisions
    and optimization strategies.
    """
    return {
        "age": 30,
        "meq_score": 65,
        "name": "Alex Johnson",
        "role": "Business Manager",
        "industry": "Technology Services"
    }


def _create_example_wearable_data() -> Dict[str, Any]:
    """
    Creates example wearable device data.
    
    This function demonstrates integration of biometric
    and activity data from wearable devices. Shows how
    physiological data informs schedule optimization
    for energy management and performance.
    """
    return {
        "sleep_quality": "Good",
        "stress_level": "Moderate",
        "readiness_score": 0.85,
        "steps_yesterday": 8500,
        "avg_heart_rate": 65,
        "sleep_duration_hours": 7.5
    }


def _create_example_historical_data() -> Dict[str, Any]:
    """
    Creates example historical behavior patterns.
    
    This function demonstrates how historical user behavior
    informs future schedule recommendations. Shows the
    learning aspect of intelligent scheduling through
    pattern recognition and preference evolution.
    """
    return {
        "typical_lunch_time": "12:00",
        "task_completion_ratio": 0.9,
        "productive_hours": ["08:00-10:00", "12:45-15:00"],
        "peak_focus_times": ["08:00-10:00", "13:00-15:00"],
        "typical_sleep_duration": 7.5
    }
