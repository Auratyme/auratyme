"""Timeline preparation helpers for Plotly Gantt-like chart."""
from __future__ import annotations
from typing import List, Dict, Any
from .validation import to_minutes

COLORS = {
    "task": "#4c78a8",
    "fixed_event": "#f58518",
    "Sleep": "#72b7b2",
    "Activity": "#e45756",
    "routine": "#54a24b",
    "meal": "#eeca3b",
}

def schedule_to_rows(tasks_section: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Convert schedule data to displayable rows.
    
    Handles multiple data structures:
    - {"tasks": [...]} - from gRPC response converted by generate_page
    - {"scheduled_tasks": [...]} - from HTTP API response
    - Direct list of tasks wrapped in dict
    
    Educational Note:
        This function is resilient to different API response formats
        and handles midnight-crossing time slots by detecting when end_time
        is less than start_time (indicating next-day scheduling).
    """
    import logging
    logger = logging.getLogger(__name__)
    
    rows: List[Dict[str, Any]] = []
    
    logger.info(f"🔍 schedule_to_rows called with input type={type(tasks_section)}, keys={list(tasks_section.keys()) if isinstance(tasks_section, dict) else 'NOT_DICT'}")
    
    if not isinstance(tasks_section, dict):
        logger.error(f"   ❌ Input is not a dict! Type: {type(tasks_section)}")
        return []
    
    tasks = None
    
    if "tasks" in tasks_section and isinstance(tasks_section["tasks"], list):
        tasks = tasks_section["tasks"]
        logger.info(f"   ✅ Found 'tasks' key with {len(tasks)} items")
    elif "scheduled_tasks" in tasks_section and isinstance(tasks_section["scheduled_tasks"], list):
        tasks = tasks_section["scheduled_tasks"]
        logger.info(f"   ✅ Found 'scheduled_tasks' key with {len(tasks)} items")
    else:
        logger.error(f"   ❌ No 'tasks' or 'scheduled_tasks' found in keys: {list(tasks_section.keys())}")
        tasks = []
    
    logger.info(f"   📊 Processing {len(tasks)} tasks for display")
    
    for idx, t in enumerate(tasks):
        if not isinstance(t, dict):
            logger.warning(f"   ⚠️ Task {idx} is not a dict, skipping: {type(t)}")
            continue
        
        st = t.get("start_time")
        et = t.get("end_time")
        task_name = t.get("task", t.get("name", "Unknown Task"))
        
        logger.info(f"   📍 Task {idx}: '{task_name}' | {st} → {et}")
        
        if not st or not et:
            logger.warning(f"      ⚠️ Missing times: start={st}, end={et} - SKIPPING")
            continue
        
        if not isinstance(st, str) or not isinstance(et, str):
            logger.warning(f"      ⚠️ Times not strings: start_type={type(st)}, end_type={type(et)} - SKIPPING")
            continue
        
        try:
            start_min = to_minutes(st)
            end_min = to_minutes(et)
        except Exception as e:
            logger.error(f"      ❌ Failed to convert times to minutes: {e} - SKIPPING")
            continue
        
        if start_min < 0 or end_min < 0:
            logger.warning(f"      ⚠️ Invalid minute values: start={start_min}, end={end_min} - SKIPPING")
            continue
        
        # Check if times are reasonable (start should be before end, or end-before-start indicates next day)
        # Allow end_min <= start_min for midnight crossing, but still validate sanity
        if start_min == end_min:
            logger.warning(f"      ⚠️ Start and end times are the same: {st} = {et} - SKIPPING")
            continue
        
        if end_min <= start_min:
            duration = (1440 - start_min) + end_min
            logger.info(f"      ⏰ Midnight crossing: {st} → {et} = {duration}min (next day)")
        else:
            duration = end_min - start_min
            logger.info(f"      ⏰ Same day: {st} → {et} = {duration}min")
        
        if duration <= 0:
            logger.warning(f"      ⚠️ Invalid duration {duration}min - SKIPPING")
            continue
        
        # Add the row
        rows.append({
            "Task": task_name,
            "Start": st,
            "End": et,
            "Minutes": duration,
            "Color": COLORS.get(task_name, COLORS["task"])
        })
        logger.info(f"      ✅ Added: {task_name} ({duration}min)")
    
    logger.info(f"🎯 schedule_to_rows returning {len(rows)}/{len(tasks)} rows")
    
    if len(rows) == 0 and len(tasks) > 0:
        logger.error("⚠️ WARNING: Tasks found but no rows created! All tasks were skipped.")
        logger.error(f"   This usually means time format validation failed.")
        logger.error(f"   First task structure: {tasks[0] if tasks else 'NO TASKS'}")
    
    return rows
