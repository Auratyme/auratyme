"""
Script to generate and save a schedule.

This script generates a schedule using the scheduler core engine and saves it to a JSON file
in the data/processed directory. It uses the run_example_and_save function from the scheduler
module to create a realistic example schedule.
"""

import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.scheduler import run_example_and_save

async def main():
    """
    Generate and save a schedule.

    Calls the run_example_and_save function from the scheduler module to generate
    a schedule and save it to a JSON file. Prints the schedule ID and file path
    upon successful completion.
    """
    print("Generating and saving schedule...")
    result = await run_example_and_save()
    print(f"Schedule generated and saved with ID: {result.schedule_id}")
    print(f"File path: data/processed/schedule_{result.schedule_id}.json")

if __name__ == "__main__":
    asyncio.run(main())
