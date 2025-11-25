"""Validation helpers for canonical inputs.

Educational Rationale:
Small, pure functions facilitate targeted unit tests and composable
validation/repair pipelines.
"""
from __future__ import annotations
from typing import List, Dict, Any, Tuple

_DEF_DAY_MINUTES = 1440

def parse_hhmm(value: str) -> Tuple[int, int]:
    """
    Parses HH:MM time string into hour and minute integers.
    
    Handles both string and datetime-like objects that have strftime method.
    
    Educational Note:
        Duck typing approach allows flexibility while maintaining type hints
        for the common case. This prevents errors when LLM returns datetime
        objects instead of formatted strings.
    """
    if hasattr(value, 'strftime'):
        value = value.strftime('%H:%M')
    elif not isinstance(value, str):
        value = str(value)
    
    parts = value.split(":")
    if len(parts) != 2:
        raise ValueError(f"Expected HH:MM format, got: {value}")
    
    h, m = parts
    return int(h), int(m)

def to_minutes(value: str) -> int:
    """
    Converts HH:MM time to minutes since midnight.
    
    Educational Note:
        Centralizing time conversion ensures consistent handling across
        the application and makes timezone-aware extensions easier.
    """
    h, m = parse_hhmm(value)
    return h * 60 + m

def is_overlap(a_start: int, a_end: int, b_start: int, b_end: int) -> bool:
    return not (a_end <= b_start or b_end <= a_start)

def detect_overlaps(rows: List[Dict[str, Any]]) -> List[Tuple[int, int]]:
    minutes_ranges = []
    for idx, r in enumerate(rows):
        if not r.get("start_time") or not r.get("end_time"):
            continue
        start = to_minutes(r["start_time"])
        end = to_minutes(r["end_time"])
        minutes_ranges.append((idx, start, end))
    overlaps = []
    for i in range(len(minutes_ranges)):
        for j in range(i + 1, len(minutes_ranges)):
            a = minutes_ranges[i]
            b = minutes_ranges[j]
            if is_overlap(a[1], a[2], b[1], b[2]):
                overlaps.append((a[0], b[0]))
    return overlaps

def total_scheduled_minutes(rows: List[Dict[str, Any]]) -> int:
    total = 0
    for r in rows:
        if r.get("start_time") and r.get("end_time"):
            total += to_minutes(r["end_time"]) - to_minutes(r["start_time"])
        elif r.get("duration"):
            total += int(r["duration"])
    return total

def round_to_half_hour(value: str) -> str:
    h, m = parse_hhmm(value)
    bucket = 0 if m < 15 else 30 if m < 45 else 0
    if m >= 45:
        h = (h + 1) % 24
    return f"{h:02d}:{bucket:02d}"
