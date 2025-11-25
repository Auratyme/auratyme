"""
API Router for APIdog Integration (Version 1).

Provides endpoints to serve generated schedule JSON files to APIdog.
"""

import json
import logging
import os
from datetime import time
from typing import Dict, List, Optional, Any
from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)
router = APIRouter()

# --- Response Models ---

class ScheduleTask(BaseModel):
    """Represents a single task in the schedule for APIdog."""
    start_time: str = Field(..., description="Start time of the task in HH:MM format.")
    end_time: str = Field(..., description="End time of the task in HH:MM format.")
    task: str = Field(..., description="Name of the task.")


class ScheduleResponse(BaseModel):
    """Response payload containing the schedule in APIdog format."""
    tasks: List[ScheduleTask] = Field(..., description="List of scheduled tasks.")
    user_id: Optional[str] = Field(None, description="User ID associated with this schedule.")
    target_date: Optional[str] = Field(None, description="Target date for this schedule.")
    scheduled_items: Optional[List[Dict[str, Any]]] = Field(None, description="Original scheduled items.")


# --- Helper Functions ---

def time_to_minutes(t: time) -> int:
    """Converts a time object to minutes from midnight."""
    return t.hour * 60 + t.minute

def time_str_to_minutes(time_str: str) -> int:
    """Converts a string in HH:MM or HH:MM:SS format to minutes from midnight."""
    try:
        parts = time_str.split(":")
        if len(parts) >= 2:
            hours = int(parts[0])
            minutes = int(parts[1])
            return hours * 60 + minutes
        return 0
    except (ValueError, IndexError):
        return 0

def process_schedule_data(schedule_data: Dict[str, Any], schedule_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Process schedule data to ensure it's in the correct format.

    Args:
        schedule_data: The schedule data to process.
        schedule_id: Optional schedule ID to use if user_id is missing.

    Returns:
        The processed schedule data.
    """
    if "tasks" in schedule_data:
        for task in schedule_data["tasks"]:
            if "start_time" in task and ":" in task["start_time"] and task["start_time"].count(":") == 2:
                task["start_time"] = ":".join(task["start_time"].split(":")[:2])
            if "end_time" in task and ":" in task["end_time"] and task["end_time"].count(":") == 2:
                task["end_time"] = ":".join(task["end_time"].split(":")[:2])

    if "user_id" not in schedule_data and schedule_id:
        schedule_data["user_id"] = str(schedule_id)
    if "target_date" not in schedule_data:
        schedule_data["target_date"] = "2025-05-15"
    if "scheduled_items" not in schedule_data:
        schedule_data["scheduled_items"] = []

    return schedule_data

def get_schedule_file_path(schedule_id: UUID) -> str:
    """
    Constructs the file path for a schedule JSON file.

    Args:
        schedule_id: The unique identifier of the schedule.

    Returns:
        The file path to the schedule JSON file.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    return os.path.join(base_dir, 'data', 'processed', f"schedule_{schedule_id}.json")


def list_available_schedules() -> List[Dict[str, str]]:
    """
    Lists all available schedule files in the processed data directory.

    Returns:
        A list of dictionaries containing schedule_id and file_path.
    """
    schedules = []
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    data_dir = os.path.join(base_dir, 'data', 'processed')

    if not os.path.exists(data_dir):
        return schedules

    for filename in os.listdir(data_dir):
        if filename.startswith('schedule_') and filename.endswith('.json'):
            schedule_id = filename.replace('schedule_', '').replace('.json', '')
            schedules.append({
                'schedule_id': schedule_id,
                'file_path': os.path.join(data_dir, filename)
            })

    return schedules


# --- API Endpoints ---

@router.get(
    "/schedules",
    response_model=List[Dict[str, str]],
    summary="List Available Schedules",
    description="Returns a list of all available schedule IDs that can be retrieved.",
    tags=["V1 - APIdog"],
)
async def list_schedules() -> List[Dict[str, str]]:
    """
    Lists all available schedule IDs.

    Returns:
        A list of dictionaries containing schedule_id.

    Raises:
        HTTPException: If an error occurs during retrieval.
    """
    logger.info("Received request to list all available schedules.")

    try:
        disable_db = os.environ.get("DISABLE_DB", "false").lower() == "true"

        if not disable_db:
            try:
                from api.db import list_schedules_from_db
                db_schedules = await list_schedules_from_db()

                if db_schedules:
                    logger.info(f"Found {len(db_schedules)} schedules in database.")
                    return db_schedules
            except Exception as db_error:
                logger.warning(f"Error accessing database: {db_error}")
        else:
            logger.info("Database connection disabled, using file-based schedules.")

        logger.info("Trying to get schedules from files.")
        file_schedules = list_available_schedules()
        return [{'schedule_id': s['schedule_id']} for s in file_schedules]
    except Exception as e:
        logger.exception("Error listing schedules")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while listing schedules: {str(e)}",
        )


@router.get(
    "/schedule/{schedule_id}",
    response_model=ScheduleResponse,
    summary="Get Schedule by ID",
    description="Retrieves a generated schedule by its ID in a format compatible with APIdog.",
    tags=["V1 - APIdog"],
)
async def get_schedule(schedule_id: UUID) -> ScheduleResponse:
    """
    Retrieves a schedule by its ID.

    Args:
        schedule_id: The unique identifier of the schedule.

    Raises:
        HTTPException: If the schedule is not found or an error occurs during retrieval.

    Returns:
        The requested schedule in APIdog format.
    """
    logger.info(f"Received request to get schedule with ID '{schedule_id}'.")

    try:
        disable_db = os.environ.get("DISABLE_DB", "false").lower() == "true"

        if not disable_db:
            try:
                from api.db import get_schedule_from_db
                db_schedule_data = await get_schedule_from_db(schedule_id)

                if db_schedule_data:
                    logger.info(f"Found schedule {schedule_id} in database.")
                    return ScheduleResponse(**db_schedule_data)
            except Exception as db_error:
                logger.warning(f"Error accessing database: {db_error}")
        else:
            logger.info("Database connection disabled, using file-based schedules.")

        logger.info(f"Trying to get schedule {schedule_id} from file.")
        file_path = get_schedule_file_path(schedule_id)

        if not os.path.exists(file_path):
            logger.warning(f"Schedule file not found: {file_path}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Schedule with ID {schedule_id} not found.",
            )

        with open(file_path, 'r', encoding='utf-8') as f:
            schedule_data = json.load(f)
            schedule_data = process_schedule_data(schedule_data, str(schedule_id))

            if not disable_db:
                try:
                    from api.db import save_schedule_to_db
                    await save_schedule_to_db(schedule_id, None, None, schedule_data)
                except Exception as db_error:
                    logger.warning(f"Error saving schedule to database: {db_error}")

        return ScheduleResponse(**schedule_data)

    except json.JSONDecodeError as e:
        logger.error(f"Error parsing JSON: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error parsing schedule data: {str(e)}",
        )
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        logger.exception(f"Error retrieving schedule {schedule_id}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving the schedule: {str(e)}",
        )


@router.get(
    "/latest-schedule",
    response_model=ScheduleResponse,
    summary="Get Latest Schedule",
    description="Retrieves the most recently generated schedule in a format compatible with APIdog.",
    tags=["V1 - APIdog"],
)
async def get_latest_schedule() -> ScheduleResponse:
    """
    Retrieves the most recently generated schedule.

    Raises:
        HTTPException: If no schedules are found or an error occurs during retrieval.

    Returns:
        The most recent schedule in APIdog format.
    """
    logger.info("Received request to get the latest schedule.")

    try:
        disable_db = os.environ.get("DISABLE_DB", "false").lower() == "true"
        if not disable_db:
            try:
                from api.db import get_latest_schedule_from_db
                db_schedule_data = await get_latest_schedule_from_db()

                if db_schedule_data:
                    logger.info("Found latest schedule in database.")
                    return ScheduleResponse(**db_schedule_data)
            except Exception as db_error:
                logger.warning(f"Error accessing database: {db_error}")
        else:
            logger.info("Database connection disabled, using file-based schedules.")

        logger.info("Trying to get latest schedule from files.")
        schedules = list_available_schedules()

        if not schedules:
            logger.warning("No schedules found in files. Generating a new schedule.")
            try:
                from api.dependencies import get_scheduler
                from src.core.scheduler import ScheduleInputData
                from src.core.task_prioritizer import Task, TaskPriority, EnergyLevel
                import datetime
                import uuid
                from typing import Dict, Any

                scheduler = get_scheduler()

                user_id = uuid.UUID("06a80008-676a-4e50-acf7-2e19dadf13bf")
                logger.info(f"Using fixed user ID for consistency: {user_id}")

                today = datetime.date(2025, 5, 15)

                preferences: Dict[str, Any] = {
                    "preferred_wake_time": "06:30",
                    "sleep_need_scale": 60,
                    "chronotype_scale": 40,
                    "work": {
                        "start_time": "08:00",
                        "end_time": "16:00",
                        "commute_minutes": 20,
                        "location": "Biuro w centrum miasta",
                        "type": "stacjonarna"
                    },
                    "meals": {
                        "breakfast_time": "07:00",
                        "breakfast_duration_minutes": 20,
                        "lunch_time": "12:30",
                        "lunch_duration_minutes": 30,
                        "dinner_time": "19:30",
                        "dinner_duration_minutes": 30
                    },
                    "routines": {
                        "morning_duration_minutes": 30,
                        "evening_duration_minutes": 45
                    },
                    "activity_goals": [
                        {
                            "name": "Gym Workout",
                            "duration_minutes": 60,
                            "frequency": "Mon,Wed,Fri",
                            "preferred_time": ["evening"]
                        },
                        {
                            "name": "Reading",
                            "duration_minutes": 30,
                            "frequency": "daily",
                            "preferred_time": ["evening", "before_sleep"]
                        }
                    ]
                }

                user_profile_data = {
                    "age": 30,
                    "meq_score": 55,
                    "name": "Użytkownik Testowy"
                }

                fixed_events = [
                    {
                        "id": "praca",
                        "start_time": "08:00",
                        "end_time": "16:00"
                    },
                    {
                        "id": "dojazd_do_pracy",
                        "start_time": "07:40",
                        "end_time": "08:00"
                    },
                    {
                        "id": "dojazd_z_pracy",
                        "start_time": "16:00",
                        "end_time": "16:20"
                    }
                ]

                tasks = [
                    Task(
                        title="Przygotuj raport kwartalny",
                        priority=TaskPriority.HIGH,
                        energy_level=EnergyLevel.MEDIUM,
                        duration=datetime.timedelta(hours=1, minutes=30),
                        deadline=datetime.datetime.combine(today, datetime.time(21, 0), tzinfo=datetime.timezone.utc),
                        earliest_start=datetime.datetime.combine(today, datetime.time(16, 30), tzinfo=datetime.timezone.utc)
                    ),
                    Task(
                        title="Spotkanie z przyjacielem",
                        priority=TaskPriority.MEDIUM,
                        energy_level=EnergyLevel.LOW,
                        duration=datetime.timedelta(minutes=45),
                        earliest_start=datetime.datetime.combine(today, datetime.time(18, 0), tzinfo=datetime.timezone.utc)
                    ),
                    Task(
                        title="Czytanie książki",
                        priority=TaskPriority.LOW,
                        energy_level=EnergyLevel.MEDIUM,
                        duration=datetime.timedelta(hours=1),
                        earliest_start=datetime.datetime.combine(today, datetime.time(20, 0), tzinfo=datetime.timezone.utc)
                    )
                ]

                wearable_data = {
                    "sleep_quality": "Good",
                    "stress_level": "Low",
                    "readiness_score": 0.85,
                    "steps_yesterday": 8500,
                    "avg_heart_rate": 68,
                    "sleep_duration_hours": 7.5,
                    "deep_sleep_percentage": 22,
                    "rem_sleep_percentage": 18
                }

                historical_data = {
                    "typical_lunch_time": "13:05",
                    "common_activity": "Evening walk around 18:00",
                    "task_completion_ratio": 1.1,
                    "productive_hours": ["09:00-12:00", "15:00-17:00"],
                    "common_breaks": ["10:30", "15:30"],
                    "typical_sleep_duration": 7.5
                }

                input_data = ScheduleInputData(
                    tasks=tasks,
                    user_id=user_id,
                    target_date=today,
                    fixed_events_input=fixed_events,
                    preferences=preferences,
                    user_profile_data=user_profile_data,
                    wearable_data_today=wearable_data,
                    historical_data=historical_data
                )

                generated_schedule = await scheduler.generate_schedule(input_data)
                logger.info(f"Generated new schedule for user: {user_id}")

                schedule_data = {
                    "tasks": [],
                    "user_id": str(user_id),
                    "target_date": str(today),
                    "scheduled_items": []
                }

                sorted_items = sorted(
                    generated_schedule.scheduled_items,
                    key=lambda x: (
                        time_to_minutes(x.get("start_time")) if isinstance(x.get("start_time"), time) else
                        time_str_to_minutes(x.get("start_time")) if isinstance(x.get("start_time"), str) and ":" in x.get("start_time") else
                        float('inf')
                    )
                )

                for item in sorted_items:
                    start_time = item.get("start_time")
                    end_time = item.get("end_time")

                    if isinstance(start_time, time):
                        start_time = start_time.strftime("%H:%M")
                    elif isinstance(start_time, str) and ":" in start_time:
                        if start_time.count(":") == 2:
                            start_time = ":".join(start_time.split(":")[:2])
                    else:
                        start_time = "N/A"

                    if isinstance(end_time, time):
                        end_time = end_time.strftime("%H:%M")
                    elif isinstance(end_time, str) and ":" in end_time:
                        if end_time.count(":") == 2:
                            end_time = ":".join(end_time.split(":")[:2])
                    else:
                        end_time = "N/A"

                    task = {
                        "start_time": start_time,
                        "end_time": end_time,
                        "task": item.get("name", "Unknown Task")
                    }
                    schedule_data["tasks"].append(task)

                schedule_data["scheduled_items"] = generated_schedule.scheduled_items

                base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
                data_dir = os.path.join(base_dir, 'data', 'processed')

                os.makedirs(data_dir, exist_ok=True)

                file_path = os.path.join(data_dir, f"schedule_{generated_schedule.schedule_id}.json")
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(schedule_data, f, indent=2)

                logger.info(f"Saved generated schedule to file: {file_path}")

                if not disable_db:
                    try:
                        from api.db import save_schedule_to_db
                        await save_schedule_to_db(str(generated_schedule.schedule_id), None, None, schedule_data)
                        logger.info(f"Saved generated schedule to database: {generated_schedule.schedule_id}")
                    except Exception as db_error:
                        logger.warning(f"Error saving schedule to database: {db_error}")

                return ScheduleResponse(**schedule_data)

            except Exception as gen_error:
                logger.error(f"Error generating new schedule: {gen_error}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to generate a new schedule: {str(gen_error)}",
                )

        schedules.sort(key=lambda s: os.path.getmtime(s['file_path']), reverse=True)
        latest_schedule = schedules[0]

        with open(latest_schedule['file_path'], 'r', encoding='utf-8') as f:
            schedule_data = json.load(f)
            schedule_data = process_schedule_data(schedule_data, latest_schedule['schedule_id'])

            if not disable_db:
                try:
                    from api.db import save_schedule_to_db
                    schedule_id = latest_schedule['schedule_id']
                    await save_schedule_to_db(schedule_id, None, None, schedule_data)
                    logger.info(f"Saved latest schedule to database: {schedule_id}")
                except Exception as db_error:
                    logger.warning(f"Error saving schedule to database: {db_error}")

        return ScheduleResponse(**schedule_data)

    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        logger.exception("Error retrieving latest schedule")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving the latest schedule: {str(e)}",
        )
