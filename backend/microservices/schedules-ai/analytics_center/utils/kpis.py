"""KPI computation helpers for generated schedules.

Pure functions enabling deterministic testing.
"""
from __future__ import annotations
from typing import List, Dict, Any
from .validation import to_minutes

_DEF_DAY = 1440

def _duration(start: str, end: str) -> int:
    return to_minutes(end) - to_minutes(start)

def total_minutes(tasks: List[Dict[str, str]]) -> int:
    return sum(max(0, _duration(t['start_time'], t['end_time'])) for t in tasks if t.get('start_time') and t.get('end_time'))

def avg_block(tasks: List[Dict[str, str]]) -> float | None:
    filtered = [ _duration(t['start_time'], t['end_time']) for t in tasks if t.get('start_time') and t.get('end_time')]
    if not filtered:
        return None
    return round(sum(filtered)/len(filtered),2)

def coverage(requested: List[Dict[str, Any]], scheduled: List[Dict[str, str]]) -> float | None:
    req_total = sum(t.get('duration_minutes', 0) or t.get('duration',0) for t in requested)
    if not req_total:
        return None
    sched_total = total_minutes(scheduled)
    return round(sched_total / req_total, 4)

def build_kpis(requested_tasks: List[Dict[str, Any]], scheduled_tasks: List[Dict[str, str]]) -> Dict[str, Any]:
    tm = total_minutes(scheduled_tasks)
    return {
        'utilization_ratio': round(tm / _DEF_DAY, 4),
        'total_scheduled_minutes': tm,
        'avg_block_minutes': avg_block(scheduled_tasks),
        'task_coverage': coverage(requested_tasks, scheduled_tasks)
    }
