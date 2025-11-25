"""
Script to run the development environment in a simple way.

This script provides a simplified development environment setup by first generating
an example schedule and then running the API server in sequence.
"""

import os
import subprocess
import sys
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def main():
    """
    Run the development environment.

    Executes the following steps in sequence:
    1. Generates an example schedule using generate_example_schedule.py
    2. Waits briefly to ensure the schedule is properly saved
    3. Starts the API server using run_api_server.py
    """
    print("Starting development environment...")

    print("\n=== Generating Example Schedule ===")
    subprocess.run([sys.executable, os.path.join("scripts", "generate_example_schedule.py")])

    time.sleep(1)

    print("\n=== Starting API Server ===")
    subprocess.run([sys.executable, os.path.join("scripts", "run_api_server.py")])

if __name__ == "__main__":
    main()
