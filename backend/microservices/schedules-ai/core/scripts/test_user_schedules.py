"""
Script to test user schedules API endpoints.

This script tests the CRUD operations for user schedules.
"""

import os
import sys
import json
import logging
import requests
from uuid import uuid4

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")


def test_user_schedules_crud():
    """Test CRUD operations for user schedules."""
    user_id = str(uuid4())

    try:
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from api.middleware.jwt_auth import create_jwt_token

        token = create_jwt_token(user_id)
        logger.info(f"Created token for user {user_id}")

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        list_url = f"{API_BASE_URL}/v1/user-schedules"
        logger.info(f"Testing GET {list_url}")

        list_response = requests.get(list_url, headers=headers)

        if list_response.status_code != 200:
            logger.error(f"Error listing schedules: {list_response.status_code}")
            logger.error(f"Response: {list_response.text}")
            return

        schedules = list_response.json()
        logger.info(f"Initial schedules: {json.dumps(schedules, indent=2)}")

        create_url = f"{API_BASE_URL}/v1/user-schedules"
        logger.info(f"Testing POST {create_url}")

        create_data = {
            "name": "Test Schedule",
            "description": "This is a test schedule created by the test script."
        }

        create_response = requests.post(create_url, headers=headers, json=create_data)

        if create_response.status_code != 201:
            logger.error(f"Error creating schedule: {create_response.status_code}")
            logger.error(f"Response: {create_response.text}")
            return

        created_schedule = create_response.json()
        logger.info(f"Created schedule: {json.dumps(created_schedule, indent=2)}")

        schedule_id = created_schedule["id"]

        get_url = f"{API_BASE_URL}/v1/user-schedules/{schedule_id}"
        logger.info(f"Testing GET {get_url}")

        get_response = requests.get(get_url, headers=headers)

        if get_response.status_code != 200:
            logger.error(f"Error getting schedule: {get_response.status_code}")
            logger.error(f"Response: {get_response.text}")
            return

        schedule = get_response.json()
        logger.info(f"Retrieved schedule: {json.dumps(schedule, indent=2)}")

        update_url = f"{API_BASE_URL}/v1/user-schedules/{schedule_id}"
        logger.info(f"Testing PATCH {update_url}")

        update_data = {
            "name": "Updated Test Schedule",
            "description": "This schedule has been updated."
        }

        update_response = requests.patch(update_url, headers=headers, json=update_data)

        if update_response.status_code != 204:
            logger.error(f"Error updating schedule: {update_response.status_code}")
            logger.error(f"Response: {update_response.text}")
            return

        logger.info("Schedule updated successfully.")

        get_response = requests.get(get_url, headers=headers)

        if get_response.status_code != 200:
            logger.error(f"Error getting updated schedule: {get_response.status_code}")
            logger.error(f"Response: {get_response.text}")
            return

        updated_schedule = get_response.json()
        logger.info(f"Updated schedule: {json.dumps(updated_schedule, indent=2)}")

        list_response = requests.get(list_url, headers=headers)

        if list_response.status_code != 200:
            logger.error(f"Error listing schedules: {list_response.status_code}")
            logger.error(f"Response: {list_response.text}")
            return

        schedules = list_response.json()
        logger.info(f"Schedules after creation: {json.dumps(schedules, indent=2)}")

        delete_url = f"{API_BASE_URL}/v1/user-schedules/{schedule_id}"
        logger.info(f"Testing DELETE {delete_url}")

        delete_response = requests.delete(delete_url, headers=headers)

        if delete_response.status_code != 204:
            logger.error(f"Error deleting schedule: {delete_response.status_code}")
            logger.error(f"Response: {delete_response.text}")
            return

        logger.info("Schedule deleted successfully.")

        list_response = requests.get(list_url, headers=headers)

        if list_response.status_code != 200:
            logger.error(f"Error listing schedules: {list_response.status_code}")
            logger.error(f"Response: {list_response.text}")
            return

        schedules = list_response.json()
        logger.info(f"Schedules after deletion: {json.dumps(schedules, indent=2)}")

        logger.info("All tests passed successfully!")
    except Exception as e:
        logger.exception(f"Error testing user schedules: {e}")


if __name__ == "__main__":
    test_user_schedules_crud()
