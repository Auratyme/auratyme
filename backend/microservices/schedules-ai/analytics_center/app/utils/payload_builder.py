"""
Payload building utilities for API requests.

This module provides functions to construct API request payloads
from application state. Demonstrates data transformation patterns
for converting UI state into API-compatible structures while
maintaining separation of concerns.

Educational Note:
    Breaking payload construction into focused functions improves
    testability and makes data transformations explicit and
    traceable, following single-responsibility principle.
"""

from typing import Dict, Any, List
from uuid import uuid4
import logging
from models.ui import AppState

logger = logging.getLogger(__name__)


def build_api_payload(state: AppState) -> dict:
    """
    Constructs complete API request payload from application state.
    
    Orchestrates the construction of a complete API payload by
    extracting and transforming tasks, fixed events, user profile data,
    and preferences from application state. Demonstrates composition
    pattern for building complex data structures.
    
    Args:
        state: Application state containing user inputs
        
    Returns:
        Complete API request payload dictionary
        
    Educational Note:
        Centralizing payload construction allows for consistent
        data transformation logic and makes API contract changes
        easier to manage in a single location.
    """
    logger.info("=" * 100)
    logger.info("🔍 BUILD_API_PAYLOAD STARTED")
    logger.info("=" * 100)
    
    tasks, fixed_events = extract_tasks_and_events(state)
    logger.info(f"📋 Tasks extracted: {len(tasks)} items")
    for i, t in enumerate(tasks):
        logger.info(f"   [{i}] {t.get('name')} - {t.get('duration_minutes')}min, priority={t.get('priority')}")
    
    logger.info(f"📍 Fixed Events extracted: {len(fixed_events)} items")
    for i, fe in enumerate(fixed_events):
        logger.info(f"   [{i}] {fe.get('name')} - {fe.get('start_time')} to {fe.get('end_time')}")
    
    preferences = build_preferences_dict(state)
    logger.info(f"⚙️  Preferences built:")
    logger.info(f"   🍽️  Meals: lunch_duration={preferences['meals'].get('lunch_duration')}min")
    logger.info(f"   🌅 Routines: morning={preferences['routines'].get('morning_routine_minutes')}min, evening={preferences['routines'].get('evening_routine_minutes')}min")
    logger.info(f"   💼 Work: {preferences['work'].get('start')} - {preferences['work'].get('end')}")
    
    user_profile_data = extract_user_profile_data(state)
    logger.info(f"👤 User Profile:")
    logger.info(f"   meq_score={user_profile_data.get('meq_score')}, age={user_profile_data.get('age')}, sleep_need={user_profile_data.get('sleep_need')}")
    
    payload = assemble_request_payload(state, tasks, fixed_events, preferences, user_profile_data)
    
    logger.info("=" * 100)
    logger.info("✅ BUILD_API_PAYLOAD COMPLETED - FULL PAYLOAD:")
    logger.info("=" * 100)
    import json
    logger.info(json.dumps(payload, indent=2, default=str))
    logger.info("=" * 100)
    
    return payload


def extract_tasks_and_events(state: AppState) -> tuple:
    """
    Separates tasks into regular and fixed-time categories.
    Also adds automatic fixed events for work hours and meals.
    
    Processes task list from state to categorize tasks based on
    whether they have fixed time constraints. Demonstrates data
    classification patterns for API payload preparation.
    
    IMPORTANT: Work hours are ALWAYS added as fixed events!
    NOTE: Commute times are handled by BACKEND via work_type and commute_minutes!
    """
    tasks, fixed_events = [], []
    categorize_task_list(state.current_inputs.tasks, tasks, fixed_events)
    
    # Add work hours as fixed event (ALWAYS)
    # Backend will automatically create commute blocks if work_type is office/hybrid
    add_work_as_fixed_event(state, fixed_events)
    
    logger.info(f"✅ After work extraction: tasks={len(tasks)}, fixed_events={len(fixed_events)}")
    
    return tasks, fixed_events


def add_work_as_fixed_event(state: AppState, fixed_events: List) -> None:
    """
    Adds work hours as a fixed event.
    
    Work hours should ALWAYS be treated as fixed events so the scheduler
    can build the day around them. This is critical for proper schedule generation.
    
    Educational Note:
        ID is NOT included here - backend will auto-generate it.
        This reduces payload size and client complexity.
    """
    profile = state.current_inputs.user_profile
    
    if not profile.start_time or not profile.end_time:
        logger.warning("⚠️ No work hours defined, skipping work fixed event")
        return
    
    work_event = {
        "name": "School/Work",
        "start_time": format_time_for_api(profile.start_time),  # Add seconds
        "end_time": format_time_for_api(profile.end_time),      # Add seconds
    }
    
    fixed_events.append(work_event)
    logger.info(f"✅ Added Work as fixed event: {profile.start_time} - {profile.end_time}")


def categorize_task_list(task_list, tasks: List, fixed_events: List) -> None:
    """
    Processes each task and categorizes into appropriate list.
    
    Iterates through task list applying transformation and
    categorization logic to each task based on its properties.
    Demonstrates list processing with side effects pattern.
    
    IMPORTANT: Skips "Work" task to avoid duplication with
    add_work_as_fixed_event() which always adds work hours.
    """
    for task_item in task_list:
        if should_skip_task(task_item):
            logger.info(f"⏭️  Skipping '{task_item.title}' - handled separately")
            continue
        process_single_task(task_item, tasks, fixed_events)


def process_single_task(task_item, tasks: List, fixed_events: List) -> None:
    """
    Transforms and categorizes a single task item.
    
    Applies transformation logic to individual task and adds
    to appropriate category list. Handles both regular and
    fixed-time tasks with proper field mapping.
    """
    if should_treat_as_fixed_event(task_item):
        add_to_fixed_events(task_item, fixed_events)
    else:
        add_to_regular_tasks(task_item, tasks)


def should_skip_task(task_item) -> bool:
    """
    Determines if task should be skipped from processing.
    
    Returns True for tasks that are handled separately
    (e.g., "Work" which is always added via add_work_as_fixed_event).
    """
    task_name_lower = getattr(task_item, 'title', '').lower().strip()
    return task_name_lower == 'work'


def should_treat_as_fixed_event(task_item) -> bool:
    """
    Determines if task should be treated as fixed event.
    
    Evaluates task properties to determine categorization
    based on fixed time flag and time availability.
    """
    return task_item.is_fixed_time and task_item.start_time and task_item.end_time


def add_to_fixed_events(task_item, fixed_events: List) -> None:
    """
    Adds task to fixed events list with proper formatting.
    
    Transforms task into fixed event format with corrected
    time strings for API compatibility. Demonstrates field
    transformation with validation requirements.
    """
    fixed_events.append(create_fixed_event_dict(task_item))


def create_fixed_event_dict(task_item) -> dict:
    """
    Creates fixed event dictionary with API-compatible fields.
    
    Constructs dictionary with required fields for fixed events
    including properly formatted time strings with seconds.
    
    Educational Note:
        ID is NOT included - backend will auto-generate it.
    """
    return {
        "name": task_item.title,
        "start_time": format_time_for_api(task_item.start_time),
        "end_time": format_time_for_api(task_item.end_time),
    }


def format_time_for_api(time_string: str) -> str:
    """
    Formats time string for API compatibility.
    
    Converts HH:MM format to HH:MM:SS format required by
    API time parsing. Demonstrates string transformation
    for API contract compliance.
    
    Educational Note:
        Adding seconds component ensures Pydantic can parse
        time strings correctly, preventing validation errors.
    """
    return f"{time_string}:00"


def add_to_regular_tasks(task_item, tasks: List) -> None:
    """
    Adds task to regular tasks list with proper formatting.
    
    Transforms task into regular task format with duration
    converted to minutes as required by API.
    """
    tasks.append(create_task_dict(task_item))


def create_task_dict(task_item) -> dict:
    """
    Creates task dictionary with API-compatible fields.
    
    Constructs dictionary with required task fields including
    duration conversion from hours to minutes.
    
    Educational Note:
        ID is NOT included - backend will auto-generate it.
        This reduces client-side complexity and payload size.
    """
    return {
        "name": task_item.title,
        "duration_minutes": convert_hours_to_minutes(task_item.duration_hours),
        "priority": task_item.priority,
    }


def convert_hours_to_minutes(hours: float) -> int:
    """
    Converts duration from hours to minutes.
    
    Performs unit conversion required by API while handling
    None values with sensible default.
    """
    return int((hours or 1.0) * 60)


def build_preferences_dict(state: AppState) -> Dict[str, Any]:
    """
    Constructs preferences dictionary with scheduling preferences.
    
    Builds preferences object including meals, routines, and work hours
    needed for schedule personalization. Note: chronotype data moved to
    user_profile_data for proper API processing.
    
    Educational Note:
        Separating user profile data from preferences maintains clear
        data boundaries and ensures proper processing by backend modules.
        Only sending configurable values (not hardcoded defaults like
        rounding=true) keeps the API contract minimal.
    """
    profile = state.current_inputs.user_profile
    return {
        "meals": extract_meal_preferences(profile),
        "routines": extract_routine_preferences(profile),
        "work": extract_work_hours(profile),
    }


def extract_user_profile_data(state: AppState) -> Dict[str, Any]:
    """
    Extracts user profile data for API payload.
    
    Collects chronotype-related data (MEQ, age, sleep_need) that
    needs to be processed by chronotype analyzer and sleep calculator.
    
    Educational Note:
        User profile data is separate from preferences to ensure
        proper routing to specialized analysis modules (chronotype, sleep).
    """
    profile = state.current_inputs.user_profile
    return extract_chronotype_data(profile)


def extract_meal_preferences(profile) -> Dict[str, Any]:
    """
    Extracts meal-related preferences from user profile.
    
    Only lunch duration is configurable. Lunch is always enabled
    by default in the backend, so we don't need to send the flag.
    
    Educational Note:
        Sending only configurable values reduces payload size and
        makes the API contract clearer - what you send is what
        actually varies, not hardcoded defaults.
    """
    return {
        "lunch_duration": profile.lunch_duration_minutes,
    }


def extract_routine_preferences(profile) -> Dict[str, int]:
    """
    Extracts routine duration preferences from profile.
    
    Only morning and evening routine durations are configurable.
    Afternoon breaks are not used in the current system.
    
    Educational Note:
        Sending only the values that actually vary keeps the API
        contract minimal and clear. Backend applies defaults for
        any missing optional fields.
    """
    return {
        "morning_routine_minutes": profile.morning_duration_minutes,
        "evening_routine_minutes": profile.evening_duration_minutes,
    }


def extract_chronotype_data(profile) -> Dict[str, Any]:
    """
    Extracts chronotype-related data from user profile.
    
    Collects MEQ score, age, and sleep need for chronotype analysis
    and sleep schedule personalization.
    
    Educational Note:
        Sleep need is sent as user_profile_data (not preferences) to ensure
        it's properly processed by the sleep calculator's SleepNeed enum converter.
    """
    return {
        "meq_score": profile.meq_score,
        "age": profile.age,
        "sleep_need": profile.sleep_need,
    }


def extract_work_hours(profile) -> Dict[str, Any]:
    """
    Extracts work schedule from user profile.
    
    Sends complete WorkHours structure matching gRPC proto:
    - start: work start time (HH:MM format)
    - end: work end time (HH:MM format)
    - work_type: "remote", "office", or "hybrid" (default: "remote")
    - commute_minutes: commute time in minutes (default: 0)
    
    Educational Note:
        Field names MUST match proto schema for proper protobuf serialization.
    """
    # Profile has field named 'type', not 'work_type'
    work_type = getattr(profile, 'type', 'remote') or 'remote'
    commute_minutes = getattr(profile, 'commute_minutes', 0) or 0
    
    return {
        "start": profile.start_time,
        "end": profile.end_time,
        "work_type": work_type,
        "commute_minutes": commute_minutes,
    }


def assemble_request_payload(
    state: AppState,
    tasks: List,
    fixed_events: List,
    preferences: Dict,
    user_profile_data: Dict
) -> dict:
    """
    Assembles final API request payload from components.
    
    Combines all payload components into final request
    structure with proper field names and organization.
    Includes user_profile for chronotype and sleep analysis.
    
    Educational Note:
        user_id and target_date are now OPTIONAL - they are
        not sent in the payload. Backend auto-generates them
        if not provided, simplifying client code.
    """
    payload = {
        "tasks": tasks,
        "fixed_events": fixed_events,
        "preferences": preferences,
        "user_profile": user_profile_data,
    }
    
    logger.info("=" * 80)
    logger.info("📦 MINIMAL PAYLOAD BUILT FOR REST API:")
    logger.info(f"   📋 Tasks: {len(tasks)} items")
    logger.info(f"   📍 Fixed Events: {len(fixed_events)} items")
    logger.info(f"   🍽️  Meal Preferences: {preferences.get('meals', {})}")
    logger.info(f"   🌅 Routine Preferences: {preferences.get('routines', {})}")
    logger.info(f"   💼 Work Hours: {preferences.get('work', {})}")
    logger.info(f"   👤 User Profile: meq={user_profile_data.get('meq_score')}, age={user_profile_data.get('age')}, sleep_need={user_profile_data.get('sleep_need')}")
    logger.info("=" * 80)
    
    return payload
