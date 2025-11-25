"""Inputs page: editable canonical inputs table and basic actions.

This page lets the user review and modify all task/event rows.
Focus is on transparency and quick iteration before generation.
"""
from __future__ import annotations
import streamlit as st
import sys
import os
from typing import Any

# Add analytics_center to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from models.ui import AppState, CanonicalInput
from utils.validation import detect_overlaps, total_scheduled_minutes
from utils.repairs import apply_repairs

def _new_row() -> dict[str, Any]:
    return CanonicalInput(
        date="2025-01-01",
        task_type="Task",
        start_time="09:00",
        end_time="10:00",
        task_priority=3
    ).model_dump()

def _repair_rounding(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    repaired = []
    for r in rows:
        repaired.append(r)
    return repaired

def _validate(rows: list[dict[str, Any]]) -> dict[str, Any]:
    overlaps = detect_overlaps(rows)
    total = total_scheduled_minutes(rows)
    return {"overlaps": overlaps, "total_minutes": total}

def render(state: AppState) -> None:
    st.title("Inputs")
    data = [r.model_dump() for r in state.current_inputs.tasks]
    if not data:
        data.append(_new_row())
    edited = st.data_editor(data, num_rows="dynamic", key="inputs_editor")
    if st.button("Add Row"):
        edited.append(_new_row())
    if st.button("Repair Common Issues"):
        repaired, changes = apply_repairs(edited)
        st.session_state["inputs_editor"] = repaired
        st.info(f"Applied {len(changes)} changes")
        with st.expander("Change Log"):
            st.json(changes)
    if st.button("Validate"):
        report = _validate(edited)
        st.write(report)
    state.current_inputs.tasks = [CanonicalInput(**r) for r in edited]
