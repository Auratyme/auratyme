"""Heuristic explainability metrics.

These metrics act as a fallback when backend does not supply detailed
explanations. Each function is small and composable for clarity.
"""
from __future__ import annotations
from typing import List, Dict, Any
from .validation import to_minutes

PrimeWindow = Dict[str, str]

def _range_minutes(start: str, end: str) -> range:
    s = to_minutes(start); e = to_minutes(end)
    if e <= s:
        e = s + 1
    return range(s, e)

def utilization(rows: List[Dict[str, Any]]) -> float:
    total = 0
    for r in rows:
        if r.get("start_time") and r.get("end_time"):
            total += to_minutes(r["end_time"]) - to_minutes(r["start_time"])
    return round(total / 1440, 4)

def prime_alignment(rows: List[Dict[str, Any]], prime_windows: List[PrimeWindow]) -> float | None:
    focused = [r for r in rows if r.get("energy_level") and r["energy_level"] >= 3 and r.get("start_time") and r.get("end_time")]
    if not focused:
        return None
    prime_minutes = set()
    for w in prime_windows:
        prime_minutes.update(_range_minutes(w['start'], w['end']))
    aligned = 0; total = 0
    for r in focused:
        rng = _range_minutes(r['start_time'], r['end_time'])
        for m in rng:
            total += 1
            if m in prime_minutes:
                aligned += 1
    if total == 0:
        return None
    return round(aligned / total, 4)

def break_density(rows: List[Dict[str, Any]]) -> float | None:
    act = 0; brk = 0
    for r in rows:
        if r.get("start_time") and r.get("end_time"):
            dur = to_minutes(r['end_time']) - to_minutes(r['start_time'])
            act += dur
            brk += r.get('breaks_duration', 0) or 0
    if act == 0:
        return None
    return round(brk / act, 4)

def rounding_compliance(rows: List[Dict[str, Any]]) -> float | None:
    checked = 0; ok = 0
    for r in rows:
        for field in ("start_time", "end_time"):
            val = r.get(field)
            if val and ":" in val:
                checked += 1
                if val.endswith(":00") or val.endswith(":30"):
                    ok += 1
    if checked == 0:
        return None
    return round(ok / checked, 4)

def build_heuristics(rows: List[Dict[str, Any]], prime_windows: List[PrimeWindow]) -> Dict[str, Any]:
    return {
        "utilization_ratio": utilization(rows),
        "prime_energy_alignment": prime_alignment(rows, prime_windows),
        "break_density": break_density(rows),
        "rounding_compliance": rounding_compliance(rows),
    }
