"""Analytics Center package initialization.

Adds the analytics_center directory to Python path for proper imports
within the Streamlit container environment.
"""
import sys
import os

# Add analytics_center to Python path if not already present
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)
