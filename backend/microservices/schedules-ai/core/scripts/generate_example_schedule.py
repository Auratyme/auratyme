"""
Script to generate an example schedule.

This script generates a simple example schedule with predefined tasks and saves it
to a JSON file in the data/processed directory with a unique ID.
"""

import json
import os
import sys
import uuid

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def generate_example_schedule():
    """
    Generate an example schedule with predefined tasks.

    Creates a schedule with fixed tasks for a workday, saves it to a JSON file
    in the data/processed directory, and returns the schedule ID and file path.

    Returns:
        tuple: A tuple containing the schedule ID (str) and the file path (str).
    """
    schedule_id = str(uuid.uuid4())

    schedule = {
        "tasks": [
            {
                "start_time": "08:00",
                "end_time": "09:00",
                "task": "Morning Meeting"
            },
            {
                "start_time": "09:30",
                "end_time": "12:00",
                "task": "Project Work"
            },
            {
                "start_time": "12:00",
                "end_time": "13:00",
                "task": "Lunch Break"
            },
            {
                "start_time": "13:00",
                "end_time": "15:30",
                "task": "Development"
            },
            {
                "start_time": "15:30",
                "end_time": "16:00",
                "task": "Coffee Break"
            },
            {
                "start_time": "16:00",
                "end_time": "17:30",
                "task": "Code Review"
            }
        ]
    }

    os.makedirs(os.path.join("data", "processed"), exist_ok=True)

    file_path = os.path.join("data", "processed", f"schedule_{schedule_id}.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(schedule, f, indent=2, ensure_ascii=False)

    print(f"Example schedule generated with ID: {schedule_id}")
    print(f"Saved to: {file_path}")

    return schedule_id, file_path

if __name__ == "__main__":
    generate_example_schedule()
