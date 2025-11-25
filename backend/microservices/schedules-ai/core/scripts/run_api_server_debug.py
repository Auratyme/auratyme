"""
Script to run the API server in debug mode.

This script runs the API server using uvicorn with debug logging.
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

def main():
    """Run the API server in debug mode."""
    try:
        logger.info("Starting API server in debug mode...")
        
        logger.debug(f"Current working directory: {os.getcwd()}")
        logger.debug(f"Python path: {sys.path}")
        
        try:
            import api
            logger.debug(f"API module found at: {api.__file__}")
        except ImportError as e:
            logger.error(f"Error importing api module: {e}")
            sys.exit(1)
        
        try:
            import api.server
            logger.debug(f"API server module found at: {api.server.__file__}")
        except ImportError as e:
            logger.error(f"Error importing api.server module: {e}")
            sys.exit(1)
        
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
