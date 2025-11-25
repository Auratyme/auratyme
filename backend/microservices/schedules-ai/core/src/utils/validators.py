"""
Data Validation Utilities.

Provides a collection of reusable functions for validating common data types
and structures used throughout the scheduler application, promoting data
integrity and robustness.
"""

import logging
import re
from datetime import date, datetime, time, timedelta
from typing import Any, Dict, Optional, Tuple, Type, Union
from uuid import UUID
from src.utils.time_utils import parse_time_string

logger = logging.getLogger(__name__)

# --- Constants ---
EMAIL_REGEX = re.compile(
    r"^(?=[a-zA-Z0-9@._%+-]{6,254}$)[a-zA-Z0-9._%+-]{1,64}@"
    r"(?:[a-zA-Z0-9-]{1,63}\.){1,8}[a-zA-Z]{2,63}$"
)


# --- Validation Functions ---

def is_valid_email(email: Optional[str]) -> bool:
    """
    Validates if a string conforms to a common email address format.

    Args:
        email (Optional[str]): The string to validate.

    Returns:
        bool: True if the email format appears valid, False otherwise.
    """
    if not isinstance(email, str) or not email:
        return False
   
    return EMAIL_REGEX.match(email) is not None


def is_positive_number(value: Any) -> bool:
    """
    Validates if a value is a positive number (int or float, greater than zero).

    Args:
        value (Any): The value to check.

    Returns:
        bool: True if the value is a positive number, False otherwise.
    """
   
    return isinstance(value, (int, float)) and not isinstance(value, bool) and value > 0


def is_non_negative_number(value: Any) -> bool:
    """
    Validates if a value is a non-negative number (int or float, >= 0).

    Args:
        value (Any): The value to check.

    Returns:
        bool: True if the value is a non-negative number, False otherwise.
    """
    return isinstance(value, (int, float)) and not isinstance(value, bool) and value >= 0


def is_within_range(
    value: Any, min_val: Union[int, float], max_val: Union[int, float]
) -> bool:
    """
    Validates if a numeric value falls within a specified range (inclusive).

    Args:
        value (Any): The numeric value to check.
        min_val (Union[int, float]): The minimum allowed value.
        max_val (Union[int, float]): The maximum allowed value.

    Returns:
        bool: True if the value is a number within the specified range, False otherwise.
    """
   
    return isinstance(value, (int, float)) and not isinstance(value, bool) and min_val <= value <= max_val


def validate_slider_value(value: Any, min_val: int = 0, max_val: int = 100) -> bool:
    """
    Validates if a value is suitable for a slider (numeric, within range).

    Args:
        value (Any): The value from the slider.
        min_val (int): The minimum allowed slider value (default: 0).
        max_val (int): The maximum allowed slider value (default: 100).

    Returns:
        bool: True if the value is a number within the specified range, False otherwise.
    """
    return is_within_range(value, min_val, max_val)


def validate_feedback_rating(rating: Any, min_rating: int = 1, max_rating: int = 5) -> bool:
    """
    Validates if a feedback rating is an integer within a specified range.

    Args:
        rating (Any): The feedback rating value.
        min_rating (int): The minimum allowed rating (default: 1).
        max_rating (int): The maximum allowed rating (default: 5).

    Returns:
        bool: True if the rating is a valid integer within the range, False otherwise.
    """
   
    return isinstance(rating, int) and not isinstance(rating, bool) and min_rating <= rating <= max_rating


def validate_dict_structure(
    data: Optional[Dict[str, Any]],
    required_keys: Optional[Dict[str, Union[Type, Tuple[Type, ...]]]] = None,
    optional_keys: Optional[Dict[str, Union[Type, Tuple[Type, ...]]]] = None,
    log_prefix: str = "Validation",
) -> bool:
    """
    Performs generic validation on the structure of a dictionary.

    Checks for the presence of required keys and validates the types of values
    for both required and optional keys if they are present.

    Args:
        data (Optional[Dict[str, Any]]): The dictionary to validate.
        required_keys (Optional[Dict[str, Union[Type, Tuple[Type, ...]]]]):
            A dictionary mapping required key names to their expected type(s).
        optional_keys (Optional[Dict[str, Union[Type, Tuple[Type, ...]]]]):
            A dictionary mapping optional key names to their expected type(s).
        log_prefix (str): A prefix for log messages to identify the validation context.

    Returns:
        bool: True if the structure is valid according to the rules, False otherwise.
    """
    if not isinstance(data, dict):
        logger.warning(f"{log_prefix} failed: Input is not a dictionary (got {type(data)}).")
        return False

    required_keys = required_keys or {}
    optional_keys = optional_keys or {}

   
    for key, expected_type in required_keys.items():
        if key not in data:
            logger.warning(f"{log_prefix} failed: Missing required key '{key}'. Data: {data}")
            return False
        if not isinstance(data[key], expected_type):
            logger.warning(
                f"{log_prefix} failed: Key '{key}' has incorrect type "
                f"(expected {expected_type}, got {type(data[key])}). Data: {data}"
            )
            return False

   
    for key, expected_type in optional_keys.items():
        if key in data and not isinstance(data[key], expected_type):
            logger.warning(
                f"{log_prefix} failed: Optional key '{key}' has incorrect type "
                f"(expected {expected_type}, got {type(data[key])}). Data: {data}"
            )
           
            return False

   
   
   
   
   

    logger.debug(f"{log_prefix} passed basic structure validation.")
    return True


# --- Specific Structure Validators (Examples) ---

def validate_task_structure(task_data: Dict[str, Any]) -> bool:
    """Validates the structure and types for a task dictionary."""
   
    required = {
        "title": str,
       
        "priority": (str, int),
        "energy_level": (str, int),
        "duration": (str, int, float, timedelta),
    }
    optional = {
        "id": (str, UUID),
        "description": str,
        "deadline": (str, date, datetime),
        "earliest_start": (str, date, datetime, time),
        "dependencies": (list, set),
        "tags": list,
        "location": str,
        "completed": bool,
        "postponed_count": int,
    }
    if not validate_dict_structure(task_data, required, optional, log_prefix="Task Validation"):
        return False

   
   
   
   
   
   

    return True


def validate_user_preferences_structure(prefs_data: Dict[str, Any]) -> bool:
    """Validates the structure and types for a user preferences dictionary."""
   
    required = {}
    optional = {
        "theme": str,
        "preferred_work_start_time": str,
        "preferred_work_end_time": str,
        "sleep_duration_goal_hours": (int, float),
       
        "break_frequency_minutes": int,
        "break_duration_minutes": int,
        "sleep_need_scale": (int, float),
    }
    if not validate_dict_structure(prefs_data, required, optional, log_prefix="User Prefs Validation"):
        return False

   
    if "sleep_need_scale" in prefs_data and not validate_slider_value(prefs_data["sleep_need_scale"]):
         logger.warning(f"User Prefs Validation failed: Invalid slider value for 'sleep_need_scale'.")
         return False
    if "preferred_work_start_time" in prefs_data and parse_time_string(prefs_data["preferred_work_start_time"]) is None:
         logger.warning(f"User Prefs Validation failed: Invalid time format for 'preferred_work_start_time'.")
         return False
   

    return True


# --- Example Usage ---
async def run_example():
    """Runs examples demonstrating validator functions."""
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger.info("--- Running validators Example ---")

    print("\n--- Email Validation ---")
    print(f"'test@example.com' is valid: {is_valid_email('test@example.com')}")
    print(f"'test@example' is valid: {is_valid_email('test@example')}")
    print(f"'test @ example.com' is valid: {is_valid_email('test @ example.com')}")
    print(f"None is valid: {is_valid_email(None)}")

    print("\n--- Number Validation ---")
    print(f"5 is positive: {is_positive_number(5)}")
    print(f"0 is positive: {is_positive_number(0)}")
    print(f"-2 is positive: {is_positive_number(-2)}")
    print(f"True is positive: {is_positive_number(True)}")
    print(f"0 is non-negative: {is_non_negative_number(0)}")
    print(f"-0.1 is non-negative: {is_non_negative_number(-0.1)}")

    print("\n--- Range/Slider Validation ---")
    print(f"75 is within [0, 100]: {is_within_range(75, 0, 100)}")
    print(f"101 is within [0, 100]: {is_within_range(101, 0, 100)}")
    print(f"-1 is within [0, 100]: {is_within_range(-1, 0, 100)}")
    print(f"Slider 88.5 is valid (0-100): {validate_slider_value(88.5)}")
    print(f"Slider '90' is valid (0-100): {validate_slider_value('90')}")

    print("\n--- Feedback Rating Validation ---")
    print(f"Rating 4 is valid (1-5): {validate_feedback_rating(4)}")
    print(f"Rating 6 is valid (1-5): {validate_feedback_rating(6)}")
    print(f"Rating 0 is valid (1-5): {validate_feedback_rating(0)}")
    print(f"Rating 3.5 is valid (1-5): {validate_feedback_rating(3.5)}")

    print("\n--- Dictionary Structure Validation ---")
    valid_task = {"title": "Write report", "priority": "HIGH", "duration": "2h", "tags": ["work"]}
    invalid_task_missing = {"priority": "LOW", "duration": "1h"}
    invalid_task_type = {"title": 123, "priority": "MEDIUM", "duration": "30m"}
    invalid_task_optional_type = {"title": "Review", "priority": "MEDIUM", "duration": "1h", "tags": "urgent"}
    print(f"Valid task structure: {validate_task_structure(valid_task)}")
    print(f"Invalid task (missing title): {validate_task_structure(invalid_task_missing)}")
    print(f"Invalid task (wrong title type): {validate_task_structure(invalid_task_type)}")
    print(f"Invalid task (wrong tags type): {validate_task_structure(invalid_task_optional_type)}")

    valid_prefs = {"sleep_need_scale": 75.5, "preferred_work_start_time": "09:15"}
    invalid_prefs_range = {"sleep_need_scale": 110}
    invalid_prefs_time = {"preferred_work_start_time": "25:00"}
    print(f"Valid prefs structure: {validate_user_preferences_structure(valid_prefs)}")
    print(f"Invalid prefs (range): {validate_user_preferences_structure(invalid_prefs_range)}")
    print(f"Invalid prefs (time format): {validate_user_preferences_structure(invalid_prefs_time)}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(run_example())
