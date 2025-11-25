"""
Data preparation utilities for schedule generation.

This module handles the conversion of API request data into internal
formats required by the scheduling engine. Demonstrates data
transformation patterns and input validation essential for
maintaining clean boundaries between API and business logic layers.
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any
from uuid import UUID, uuid4

from src.core.task import Task as InternalTask, TaskPriority, EnergyLevel
from src.core.scheduler import ScheduleInputData

from .models import TaskInput, FixedEventInput, ScheduleGenerationRequest

logger = logging.getLogger(__name__)


def prepare_schedule_input_data(request: ScheduleGenerationRequest) -> ScheduleInputData:
    """
    Converts API request data to internal scheduling format.
    
    This function transforms external API models into internal
    data structures required by the scheduling engine. Demonstrates
    adapter pattern for maintaining separation between API and
    business logic layers while ensuring data integrity.
    
    Educational Note:
        Direct access to request.user_profile is safe because Pydantic
        model guarantees the field exists with default_factory=dict.
    """
    user_profile_data = request.user_profile
    
    logger.info(f"\n{'='*80}\n📨 SCHEDULE REQUEST\n{'='*80}")
    logger.info(f"User: {request.user_id} | Date: {request.target_date}")
    logger.info(f"Tasks: {len(request.tasks)} | Fixed Events: {len(request.fixed_events)}")
    
    if user_profile_data:
        meq = user_profile_data.get('meq_score', 'N/A')
        age = user_profile_data.get('age', 'N/A')
        sleep_need = user_profile_data.get('sleep_need', 'N/A')
        logger.info(f"Profile: MEQ={meq}, Age={age}, Sleep={sleep_need}h")
    
    if request.preferences:
        logger.info(f"\n⚙️  USER PREFERENCES:")
        
        if "work" in request.preferences:
            work = request.preferences["work"]
            logger.info(f"   Work: {work.get('start_time', 'N/A')}-{work.get('end_time', 'N/A')} ({work.get('type', 'N/A')})")
            if work.get('type') in ['hybrid', 'office']:
                logger.info(f"   Commute: {work.get('commute_minutes', 0)} min")
        
        if "meals" in request.preferences:
            meals = request.preferences["meals"]
            logger.info(f"   Meals:")
            for meal_name, meal_data in meals.items():
                if isinstance(meal_data, dict):
                    duration = meal_data.get('duration_minutes', 'N/A')
                    logger.info(f"      {meal_name.title()}: {duration} min")
                else:
                    logger.info(f"      {meal_name.title()}: {meal_data}")
        
        if "routines" in request.preferences:
            routines = request.preferences["routines"]
            morning = routines.get('morning_duration_minutes', 30)
            evening = routines.get('evening_duration_minutes', 45)
            logger.info(f"   Routines: Morning={morning}min, Evening={evening}min")
    
    logger.info(f"{'='*80}\n")
    
    internal_tasks = _convert_tasks_to_internal_format(request.tasks)
    internal_events = _convert_events_to_internal_format(request.fixed_events)
    
    logger.info(f"\n📍 FIXED EVENTS RECEIVED FROM API:")
    for idx, event in enumerate(internal_events, 1):
        logger.info(f"   {idx}. {event.get('name')} ({event.get('start_time')} - {event.get('end_time')})")
    logger.info(f"   Total: {len(internal_events)} events\n")
    
    _add_work_blocks_if_needed(internal_events, request.preferences)
    
    logger.info(f"\n📍 FIXED EVENTS AFTER ADDING WORK BLOCKS:")
    for idx, event in enumerate(internal_events, 1):
        logger.info(f"   {idx}. {event.get('name')} ({event.get('start_time')} - {event.get('end_time')})")
    logger.info(f"   Total: {len(internal_events)} events\n")
    
    return ScheduleInputData(
        user_id=request.user_id,
        target_date=request.target_date,
        tasks=internal_tasks,
        fixed_events_input=internal_events,
        preferences=request.preferences,
        user_profile_data=user_profile_data
    )


def _map_priority_to_energy_level(priority: int) -> EnergyLevel:
    """
    Maps task priority (1-5) to energy level (LOW/MEDIUM/HIGH).
    
    Priority mapping strategy:
    - Priority 5 (critical/urgent) → HIGH energy (needs peak focus hours)
    - Priority 4 (high importance) → HIGH energy (benefits from peak hours)
    - Priority 3 (medium) → MEDIUM energy (flexible placement)
    - Priority 2 (low importance) → LOW energy (off-peak acceptable)
    - Priority 1 (minimal) → LOW energy (filler tasks)
    
    Educational Note:
        High-priority tasks require user's best cognitive performance,
        so they should be scheduled during chronotype-specific peak
        energy windows (e.g., 17:00-22:00 for night owls).
        
        Low-priority tasks can be placed in off-peak hours without
        significant impact on completion quality or user experience.
    """
    if priority >= 4:
        return EnergyLevel.HIGH
    elif priority == 3:
        return EnergyLevel.MEDIUM
    else:
        return EnergyLevel.LOW


def _convert_tasks_to_internal_format(tasks: List[TaskInput]) -> List[InternalTask]:
    """
    Converts API task models to internal task objects.
    
    This helper function transforms external task representations
    into internal task objects with proper type conversion and
    validation. Demonstrates model transformation patterns for
    maintaining type safety across system boundaries.
    """
    return [_create_internal_task(task) for task in tasks]


def _create_internal_task(task: TaskInput) -> InternalTask:
    """
    Creates internal task object from API task input.
    
    This function handles the detailed conversion of individual
    task objects including duration conversion and deadline
    handling. Maps priority to energy level for intelligent
    task scheduling during peak energy hours.
    
    Educational Note:
        Priority→Energy mapping ensures high-priority tasks
        are scheduled during peak energy hours, while low-priority
        tasks can be placed in off-peak times.
        
        Task ID is auto-generated here since it's not provided
        by the client, reducing payload size and complexity.
    """
    deadline = _convert_deadline_to_datetime(task.deadline)
    energy_level = _map_priority_to_energy_level(task.priority)
    
    return InternalTask(
        id=str(uuid4()),
        title=task.name,
        duration=timedelta(minutes=task.duration_minutes),
        priority=TaskPriority(task.priority),
        energy_level=energy_level,
        deadline=deadline
    )


def _convert_deadline_to_datetime(deadline_date) -> datetime:
    """
    Converts deadline date to datetime with timezone.
    
    This utility function safely converts date objects to
    timezone-aware datetime objects for internal processing.
    Demonstrates timezone handling patterns essential for
    accurate time-based calculations in scheduling systems.
    """
    if deadline_date:
        return datetime.combine(deadline_date, datetime.min.time(), timezone.utc)
    return None


def _convert_events_to_internal_format(events: List[FixedEventInput]) -> List[Dict[str, Any]]:
    """
    Converts API event models to internal event dictionaries.
    
    This function transforms external event objects into
    dictionaries with properly formatted time strings for
    internal processing. Demonstrates flexible data structure
    conversion for system integration points.
    """
    return [_create_internal_event(event) for event in events]


def _create_internal_event(event: FixedEventInput) -> Dict[str, Any]:
    """
    Creates internal event dictionary from API event input.
    
    This helper function converts individual event objects
    with proper time formatting for internal consumption.
    Demonstrates consistent data formatting patterns across
    system boundaries while maintaining data integrity.
    
    Educational Note:
        Auto-generates ID here if not provided by API client,
        ensuring internal event representation is complete.
    """
    return {
        "id": str(uuid4()),
        "name": event.name,
        "start_time": _format_time_for_internal_use(event.start_time),
        "end_time": _format_time_for_internal_use(event.end_time)
    }


def _format_time_for_internal_use(time_obj) -> str:
    """
    Formats time object for internal system consumption.
    
    This utility function provides consistent time formatting
    for internal processing systems. Demonstrates data
    formatting standardization essential for system integration
    and avoiding time representation inconsistencies.
    """
    if hasattr(time_obj, 'isoformat'):
        return time_obj.isoformat()
    return str(time_obj)


def _add_work_blocks_if_needed(
    internal_events: List[Dict[str, Any]],
    preferences: Dict[str, Any]
) -> None:
    """
    Adds work blocks as fixed events with separate commute blocks.
    
    For hybrid/office: 3 blocks (commute to, work, commute from)
    For remote: 1 block (work only)
    
    IMPORTANT: Only adds Work event if it doesn't already exist in internal_events.
    Frontend sends "Work" as fixed_event, backend only adds commute blocks if needed.
    
    Commute timing: Morning commute MUST happen AFTER morning routine,
    so work start time is user's desired work start, and commute is
    scheduled to end exactly at that time.
    
    Educational Note:
        Separating commute as distinct blocks allows better schedule
        visualization and helps users see total time commitment.
    """
    if not preferences or "work" not in preferences:
        logger.info("⚠️ No work preferences found, skipping work blocks")
        return
    
    # Check if School/Work event already exists (from frontend)
    existing_events = [event.get("name") for event in internal_events]
    logger.info(f"🔍 Checking for existing work events. Current events: {existing_events}")
    
    work_already_exists = any(
        event.get("name") == "School/Work" 
        for event in internal_events
    )
    
    logger.info(f"🔍 work_already_exists (School/Work): {work_already_exists}")
    
    work_prefs = preferences["work"]
    # Support both old field names (start_time/end_time/type) and new field names (start/end/work_type)
    start_time = work_prefs.get("start_time") or work_prefs.get("start")
    end_time = work_prefs.get("end_time") or work_prefs.get("end")
    work_type = work_prefs.get("type") or work_prefs.get("work_type") or "remote"
    commute_minutes = work_prefs.get("commute_minutes", 0)
    
    logger.info(f"⚙️  Work preferences: start={start_time}, end={end_time}, type={work_type}, commute={commute_minutes}min")
    
    if not start_time or not end_time:
        logger.warning("⚠️ start_time or end_time is missing, cannot add work blocks")
        return
    
    from datetime import datetime, time as time_class
    
    def parse_time(time_str):
        """Parses HH:MM string to time object."""
        if isinstance(time_str, time_class):
            return time_str
        h, m = map(int, time_str.split(":"))
        return time_class(h, m)
    
    work_start = parse_time(start_time)
    work_end = parse_time(end_time)
    
    if work_type in ["hybrid", "office"] and commute_minutes > 0:
        start_minutes = work_start.hour * 60 + work_start.minute
        end_minutes = work_end.hour * 60 + work_end.minute
        
        commute_to_end_min = start_minutes
        commute_to_start_min = start_minutes - commute_minutes
        commute_from_start_min = end_minutes
        commute_from_end_min = end_minutes + commute_minutes
        
        commute_to_start = time_class(commute_to_start_min // 60, commute_to_start_min % 60)
        commute_to_end = time_class(commute_to_end_min // 60, commute_to_end_min % 60)
        commute_from_start = time_class(commute_from_start_min // 60, commute_from_start_min % 60)
        commute_from_end = time_class(commute_from_end_min // 60, commute_from_end_min % 60)
        
        internal_events.append({
            "id": "commute_to_school_work",
            "name": "Commute to School/Work",
            "start_time": commute_to_start.isoformat(),
            "end_time": commute_to_end.isoformat()
        })
        logger.info(f"✅ Added Commute to School/Work: {commute_to_start.strftime('%H:%M')}-{commute_to_end.strftime('%H:%M')}")
        
        # Add School/Work event ONLY if it doesn't already exist from frontend
        if not work_already_exists:
            internal_events.append({
                "id": "work_block",
                "name": "School/Work",
                "start_time": work_start.isoformat(),
                "end_time": work_end.isoformat()
            })
            logger.info(f"✅ Added School/Work: {work_start.strftime('%H:%M')}-{work_end.strftime('%H:%M')}")
        else:
            logger.info(f"⏭️  School/Work already exists from frontend, skipping backend addition")
        
        internal_events.append({
            "id": "commute_from_school_work",
            "name": "Commute from School/Work",
            "start_time": commute_from_start.isoformat(),
            "end_time": commute_from_end.isoformat()
        })
        logger.info(f"✅ Added Commute from School/Work: {commute_from_start.strftime('%H:%M')}-{commute_from_end.strftime('%H:%M')}")
    else:
        # Add School/Work event ONLY if it doesn't already exist from frontend
        if not work_already_exists:
            internal_events.append({
                "id": "work_block",
                "name": "School/Work",
                "start_time": work_start.isoformat(),
                "end_time": work_end.isoformat()
            })
            logger.info(f"✅ Added School/Work (remote): {work_start.strftime('%H:%M')}-{work_end.strftime('%H:%M')}")
        else:
            logger.info(f"⏭️  School/Work already exists from frontend, skipping backend addition (remote)")
