"""
Script to run the API server without database connection.

This script runs the API server using uvicorn, but disables the database connection.
"""

import uvicorn
import os
import sys
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ["DISABLE_DB"] = "true"

def main():
    """Run the API server without database connection."""
    try:
        logger.info("Starting API server without database connection...")
        
        logger.debug(f"Current working directory: {os.getcwd()}")
        logger.debug(f"Python path: {sys.path}")
        
        uvicorn.run(
            "api.server:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="debug",
        )
    except Exception as e:
        logger.exception(f"Error starting API server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
