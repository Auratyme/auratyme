"""Automatic repair utilities for canonical input rows.

Educational Focus:
Each function performs a single, easily testable normalization step.
Repairs return both updated rows and a change log for transparency.
"""
from __future__ import annotations
from typing import List, Dict, Any, Tuple
from .validation import to_minutes, round_to_half_hour

Change = Dict[str, Any]

def enforce_rounding(rows: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Change]]:
    """Rounds start/end times to :00 or :30 if rounding_flag true."""
    changes: List[Change] = []
    for idx, r in enumerate(rows):
        if not r.get("rounding_flag"):
            continue
        for field in ["start_time", "end_time"]:
            val = r.get(field)
            if val and ":" in val:
                new_val = round_to_half_hour(val)
                if new_val != val:
                    changes.append({"row": idx, "field": field, "before": val, "after": new_val, "action": "rounded"})
                    r[field] = new_val
    return rows, changes

def fill_missing_end(rows: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Change]]:
    """If duration present but end_time missing, derive end_time from start_time."""
    changes: List[Change] = []
    for idx, r in enumerate(rows):
        if r.get("start_time") and not r.get("end_time") and r.get("duration"):
            start_m = to_minutes(r["start_time"])
            end_m = start_m + int(r["duration"])
            end_h, end_min = divmod(end_m % 1440, 60)
            end_str = f"{end_h:02d}:{end_min:02d}"
            r["end_time"] = end_str
            changes.append({"row": idx, "field": "end_time", "before": None, "after": end_str, "action": "filled_end"})
    return rows, changes

def clamp_day(rows: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Change]]:
    """Ensures times stay within a 0..1440 minute day window."""
    changes: List[Change] = []
    for idx, r in enumerate(rows):
        if r.get("start_time") and r.get("end_time"):
            s = to_minutes(r["start_time"])
            e = to_minutes(r["end_time"])
            if s < 0 or s > 1439:
                s = max(0, min(1439, s))
            if e < 1 or e > 1440:
                e = max(1, min(1440, e))
            if e <= s:
                e = s + 1
            new_start = f"{s//60:02d}:{s%60:02d}"
            new_end = f"{e//60:02d}:{e%60:02d}"
            if new_start != r["start_time"]:
                changes.append({"row": idx, "field": "start_time", "before": r["start_time"], "after": new_start, "action": "clamped"})
                r["start_time"] = new_start
            if new_end != r["end_time"]:
                changes.append({"row": idx, "field": "end_time", "before": r["end_time"], "after": new_end, "action": "clamped"})
                r["end_time"] = new_end
    return rows, changes

def shift_collisions(rows: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Change]]:
    """Naive forward shift for overlapping consecutive blocks (UI convenience).

    This does not guarantee global optimality; solver will still generate
    authoritative non-overlapping schedule. Here we give quick visual feedback.
    """
    changes: List[Change] = []
    # Build sortable list
    enriched = []
    for i, r in enumerate(rows):
        if r.get("start_time") and r.get("end_time"):
            enriched.append((to_minutes(r["start_time"]), to_minutes(r["end_time"]), i))
    enriched.sort()
    for idx in range(1, len(enriched)):
        prev_s, prev_e, prev_row = enriched[idx-1]
        cur_s, cur_e, cur_row = enriched[idx]
        if cur_s < prev_e:
            delta = prev_e - cur_s
            cur_s += delta
            cur_e += delta
            new_start = f"{(cur_s)%1440//60:02d}:{(cur_s)%60:02d}"
            new_end = f"{(cur_e)%1440//60:02d}:{(cur_e)%60:02d}"
            rows[cur_row]["start_time"], rows[cur_row]["end_time"] = new_start, new_end
            changes.append({"row": cur_row, "action": "shifted", "reason": "overlap", "after_start": new_start, "after_end": new_end})
            enriched[idx] = (cur_s, cur_e, cur_row)
    return rows, changes

def apply_repairs(rows: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Change]]:
    """Composite repair pipeline returning merged change log."""
    full_changes: List[Change] = []
    for func in (enforce_rounding, fill_missing_end, clamp_day, shift_collisions):
        rows, ch = func(rows)
        full_changes.extend(ch)
    return rows, full_changes
