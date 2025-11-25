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

from models.ui import AppState, CanonicalInput
from utils.validation import detect_overlaps, total_scheduled_minutes
from utils.repairs import apply_repairs

def _clean_dataframe_row(row: pd.Series) -> Dict[str, Any]:
    """Clean a dataframe row for safe Pydantic validation."""
    cleaned = {}
    for key, value in row.items():
        if pd.isna(value) or value is None:
            # Set safe defaults based on field type
            if key in ['date']:
                cleaned[key] = "2025-01-01"
            elif key in ['task_type']:
                cleaned[key] = "Task"
            elif key in ['start_time']:
                cleaned[key] = "09:00"
            elif key in ['end_time']:  
                cleaned[key] = "10:00"
            elif key in ['task_priority']:
                cleaned[key] = 3
            elif key in ['breaks_count', 'breaks_duration', 'duration']:
                cleaned[key] = 0
            elif key in ['fixed_task']:
                cleaned[key] = False
            elif key in ['no_overlaps', 'enforce_total_minutes', 'rounding_flag']:
                cleaned[key] = True
            else:
                cleaned[key] = None
        elif isinstance(value, float) and math.isnan(value):
            # Handle NaN values
            if key in ['task_priority']:
                cleaned[key] = 3
            elif key in ['breaks_count', 'breaks_duration', 'duration']:
                cleaned[key] = 0
            else:
                cleaned[key] = None
        else:
            cleaned[key] = value
    return cleaned

def _new_row() -> Dict[str, Any]:
    """Create a new default row for the inputs table."""
    return CanonicalInput(
        date="2025-01-01",
        task_type="Task",
        start_time="09:00",
        end_time="10:00",
        duration=60,
        task_priority=3
    ).model_dump()

def render(state: AppState) -> None:
    """Render the enhanced inputs editing interface."""
    st.title("📝 Task & Event Inputs")
    st.markdown("Configure your tasks, events, and scheduling preferences below.")
    
    # Action buttons in columns
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("➕ Add Row", width="stretch"):
            from models.enhanced_ui import TaskForSchedule
            state.current_inputs.tasks.append(TaskForSchedule())
            st.rerun()
    
    with col2:
        if st.button("🔧 Apply Repairs", width="stretch"):
            repaired_rows, change_log = apply_repairs([item.model_dump() for item in state.current_inputs.tasks])
            if change_log:
                st.success(f"Applied {len(change_log)} repairs!")
                with st.expander("📋 Change Log"):
                    for change in change_log:
                        st.write(f"• Row {change['row']}: {change.get('field', 'multiple')} - {change['action']}")
                
                try:
                    from models.enhanced_ui import TaskForSchedule
                    state.current_inputs.tasks = [TaskForSchedule(**row) for row in repaired_rows]
                    st.rerun()
                except Exception as e:
                    st.error(f"Error applying repairs: {e}")
            else:
                st.info("No repairs needed!")
    
    with col3:
        if st.button("✅ Validate", width="stretch"):
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
        if st.button("🗑️ Clear All", width="stretch", type="secondary"):
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
        "date": st.column_config.TextColumn("📅 Date", help="Format: YYYY-MM-DD"),
        "task_type": st.column_config.SelectboxColumn("🏷️ Type", options=["Task", "Meeting", "Break", "Exercise", "Sleep", "Meal", "Travel", "Other"]),
        "start_time": st.column_config.TextColumn("🕐 Start", help="Format: HH:MM"),
        "end_time": st.column_config.TextColumn("🕑 End", help="Format: HH:MM"), 
        "duration": st.column_config.NumberColumn("⏱️ Duration (min)", min_value=0, max_value=1440),
        "task_priority": st.column_config.NumberColumn("⭐ Priority", min_value=1, max_value=5),
        "breaks_count": st.column_config.NumberColumn("☕ Breaks #", min_value=0, max_value=20),
        "breaks_duration": st.column_config.NumberColumn("⏸️ Break Min", min_value=0, max_value=120),
        "energy_level": st.column_config.NumberColumn("⚡ Energy", min_value=1, max_value=5),
        "fixed_task": st.column_config.CheckboxColumn("📌 Fixed"),
        "no_overlaps": st.column_config.CheckboxColumn("🚫 No Overlap"),
        "rounding_flag": st.column_config.CheckboxColumn("🔄 Round Time")
    }
    
    # Show data editor
    st.subheader("📋 Task & Event Details")
    edited = st.data_editor(
        df, 
        column_config=column_config,
        width="stretch",
        num_rows="dynamic",
        key="inputs_editor",
        height=400
    )
    
    # Safely convert back to CanonicalInput objects
    try:
        cleaned_rows = []
        for idx, row in edited.iterrows():
            cleaned_row = _clean_dataframe_row(row)
            from models.enhanced_ui import TaskForSchedule
            cleaned_rows.append(TaskForSchedule(**cleaned_row))
        
        state.current_inputs.tasks = cleaned_rows
        
        # Show summary
        with st.expander("📊 Quick Summary", expanded=False):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Items", len(state.current_inputs.tasks))
            with col2:
                total_time = sum(item.duration_hours * 60 if item.duration_hours else 0 for item in state.current_inputs.tasks)
                st.metric("Total Duration", f"{total_time} min")
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
