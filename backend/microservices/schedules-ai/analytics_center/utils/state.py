"""State helpers wrapping Streamlit session_state.

Educational Note:
Abstracting access centralizes default initialization and keeps page
modules pure and testable (we can patch these helpers in unit tests).
"""
from __future__ import annotations
import streamlit as st
import sys
import os

# Add analytics_center to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from models.ui import AppState
from models.enhanced_ui import AppState as EnhancedAppState, InputCollection

_STATE_KEY = "__APP_STATE__"

def init_state() -> None:
    if _STATE_KEY not in st.session_state:
        # Initialize with enhanced state that includes both old and new formats
        enhanced_state = EnhancedAppState()
        # Keep backward compatibility by also setting the old current_inputs
        enhanced_state.__dict__.update(AppState().__dict__)
        # Convert old format to new format if needed
        enhanced_state.current_inputs = InputCollection()
        st.session_state[_STATE_KEY] = enhanced_state

def get_state() -> AppState:
    return st.session_state[_STATE_KEY]
