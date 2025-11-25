"""Inputs page: enhanced editable canonical inputs table.

This page provides an intuitive interface for managing tasks and events
with validation, repairs, and comprehensive error handling.
"""
from __future__ import annotations
import streamlit as st
import pandas as pd
import sys
import os
from typing import Any, Dict, List
import math

# Add analytics_center to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from models.enhanced_ui import AppState, TaskForSchedule
from utils.validation import detect_overlaps, total_scheduled_minutes
from utils.repairs import apply_repairs

def _clean_dataframe_row(row: pd.Series) -> Dict[str, Any]:
    """Clean a dataframe row for safe TaskForSchedule validation."""
    cleaned = {}
    for key, value in row.items():
        # Map old field names to new ones
        if key == 'task_type':
            key = 'title'
        elif key == 'task_priority':
            key = 'priority'
        elif key == 'duration':
            key = 'duration_hours'
            if pd.notna(value) and value is not None:
                value = value / 60.0  # Convert minutes to hours
        elif key == 'fixed_task':
            key = 'is_fixed_time'
            
        if pd.isna(value) or value is None:
            # Set safe defaults based on field type
            if key in ['title']:
                cleaned[key] = "Task"
            elif key in ['start_time', 'end_time']:
                cleaned[key] = None  # Only set if is_fixed_time is True
            elif key in ['priority']:
                cleaned[key] = 3
            elif key in ['duration_hours']:
                cleaned[key] = 1.0
            elif key in ['is_fixed_time']:
                cleaned[key] = False
            else:
                cleaned[key] = None
        elif isinstance(value, float) and math.isnan(value):
            # Handle NaN values
            if key in ['priority']:
                cleaned[key] = 3
            elif key in ['duration_hours']:
                cleaned[key] = 1.0
            else:
                cleaned[key] = None
        else:
            cleaned[key] = value
    return cleaned

def _new_row() -> Dict[str, Any]:
    """Create a new default row for the inputs table."""
    return TaskForSchedule(
        title="Task",
        priority=3,
        duration_hours=1.0,
        is_fixed_time=False
    ).model_dump()

def render(state: AppState) -> None:
    """Render the enhanced inputs editing interface."""
    st.title("📝 Task & Event Inputs")
    st.markdown("Configure your tasks, events, and scheduling preferences below.")
    
    # Action buttons in columns
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("➕ Add Row", use_container_width=True):
            state.current_inputs.tasks.append(TaskForSchedule())
            st.rerun()
    
    with col2:
        if st.button("🔧 Apply Repairs", use_container_width=True):
            result = apply_repairs([item.model_dump() for item in state.current_inputs.tasks])
            if result.change_log:
                st.success(f"Applied {len(result.change_log)} repairs!")
                with st.expander("📋 Change Log"):
                    for change in result.change_log:
                        st.write(f"• Row {change['row']}: {change['field']} - {change['action']}")
            else:
                st.info("No repairs needed!")
    
    with col3:
        if st.button("✅ Validate", use_container_width=True):
            overlaps = detect_overlaps([item.model_dump() for item in state.current_inputs.tasks])
            total_mins = total_scheduled_minutes([item.model_dump() for item in state.current_inputs.tasks])
            
            if overlaps:
                st.warning(f"⚠️ Found {len(overlaps)} overlaps!")
                with st.expander("🔍 View Overlaps"):
                    for overlap in overlaps:
                        st.write(f"• {overlap}")
            else:
                st.success("✅ No overlaps detected!")
            
            st.info(f"📊 Total scheduled time: {total_mins} minutes ({total_mins/60:.1f} hours)")
    
    with col4:
        if st.button("🗑️ Clear All", use_container_width=True, type="secondary"):
            if st.session_state.get("confirm_clear", False):
                state.current_inputs.tasks = []
                st.session_state["confirm_clear"] = False
                st.success("Cleared all inputs!")
                st.rerun()
            else:
                st.session_state["confirm_clear"] = True
                st.warning("Click again to confirm!")
    
    if not state.current_inputs.tasks:
        st.info("👋 No inputs yet! Add your first task or event above.")
        return
    
    # Convert to DataFrame for editing
    df = pd.DataFrame([item.model_dump() for item in state.current_inputs.tasks])
    
    # Configure column display
    column_config = {
        "title": st.column_config.SelectboxColumn("🏷️ Title", options=["Task", "Meeting", "Break", "Exercise", "Sleep", "Meal", "Travel", "Other"]),
        "priority": st.column_config.NumberColumn("⭐ Priority", min_value=1, max_value=5),
        "duration_hours": st.column_config.NumberColumn("⏱️ Duration (hours)", min_value=0.0, max_value=24.0, step=0.25),
        "is_fixed_time": st.column_config.CheckboxColumn("📌 Fixed Time"),
        "start_time": st.column_config.TextColumn("🕐 Start Time", help="Format: HH:MM (only for fixed time tasks)"),
        "end_time": st.column_config.TextColumn("� End Time", help="Format: HH:MM (only for fixed time tasks)")
    }
    
    # Show data editor
    st.subheader("📋 Task & Event Details")
    edited = st.data_editor(
        df, 
        column_config=column_config,
        use_container_width=True,
        num_rows="dynamic",
        key="inputs_editor",
        height=400
    )
    
    # Safely convert back to CanonicalInput objects
    try:
        cleaned_rows = []
        for idx, row in edited.iterrows():
            cleaned_row = _clean_dataframe_row(row)
            cleaned_rows.append(TaskForSchedule(**cleaned_row))
        
        state.current_inputs.tasks = cleaned_rows
        
        # Show summary
        with st.expander("📊 Quick Summary", expanded=False):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Items", len(state.current_inputs.tasks))
            with col2:
                total_time = sum((item.duration_hours or 0) * 60 for item in state.current_inputs.tasks)
                st.metric("Total Duration", f"{int(total_time)} min")
            with col3:
                fixed_count = sum(1 for item in state.current_inputs.tasks if item.is_fixed_time)
                st.metric("Fixed Tasks", fixed_count)
        
    except Exception as e:
        st.error(f"❌ Error processing data: {str(e)}")
        st.info("💡 Try using the 'Apply Repairs' button to fix common issues.")
        
        # Show debug info in expander
        with st.expander("🔍 Debug Info"):
            st.write("Raw edited data:")
            st.write(edited)
            st.write("Error details:")
            st.exception(e)
