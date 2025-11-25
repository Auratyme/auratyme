"""
Test script for APIdog endpoints.

This script tests the APIdog endpoints by making requests to the API server.
It verifies that the endpoints are working correctly and returning the expected data.
"""

from pprint import pprint
import requests

# --- Configuration ---
BASE_URL = "http://localhost:8000/v1/apidog"

def test_list_schedules():
    """
    Test the endpoint to list all available schedules.

    Makes a GET request to the /schedules endpoint and prints the results.

    Returns:
        list: List of schedule objects if successful, empty list otherwise.
    """
    print("\n=== Testing List Schedules Endpoint ===")
    response = requests.get(f"{BASE_URL}/schedules")

    if response.status_code == 200:
        print("✅ Success! Status code:", response.status_code)
        schedules = response.json()
        print(f"Found {len(schedules)} schedules:")
        pprint(schedules)
        return schedules
    else:
        print("❌ Error! Status code:", response.status_code)
        print("Response:", response.text)
        return []

def test_get_schedule(schedule_id):
    """
    Test the endpoint to get a specific schedule.

    Makes a GET request to the /schedule/{schedule_id} endpoint and prints
    information about the retrieved schedule.

    Args:
        schedule_id: The ID of the schedule to retrieve.
    """
    print(f"\n=== Testing Get Schedule Endpoint (ID: {schedule_id}) ===")
    response = requests.get(f"{BASE_URL}/schedule/{schedule_id}")

    if response.status_code == 200:
        print("✅ Success! Status code:", response.status_code)
        schedule = response.json()
        print(f"Schedule has {len(schedule['tasks'])} tasks.")
        print("First 3 tasks:")
        for task in schedule['tasks'][:3]:
            print(f"  - {task['task']} ({task['start_time']} - {task['end_time']})")
    else:
        print("❌ Error! Status code:", response.status_code)
        print("Response:", response.text)

def test_get_latest_schedule():
    """
    Test the endpoint to get the latest schedule.

    Makes a GET request to the /latest-schedule endpoint and prints
    information about the retrieved schedule.
    """
    print("\n=== Testing Get Latest Schedule Endpoint ===")
    response = requests.get(f"{BASE_URL}/latest-schedule")

    if response.status_code == 200:
        print("✅ Success! Status code:", response.status_code)
        schedule = response.json()
        print(f"Latest schedule has {len(schedule['tasks'])} tasks.")
        print("First 3 tasks:")
        for task in schedule['tasks'][:3]:
            print(f"  - {task['task']} ({task['start_time']} - {task['end_time']})")
    else:
        print("❌ Error! Status code:", response.status_code)
        print("Response:", response.text)

def main():
    """
    Main function to run all tests.

    Executes all test functions in sequence and reports the results.
    """
    print("Starting APIdog endpoints tests...")

    schedules = test_list_schedules()

    if schedules:
        test_get_schedule(schedules[0]['schedule_id'])

    test_get_latest_schedule()

    print("\nAll tests completed!")

if __name__ == "__main__":
    main()
