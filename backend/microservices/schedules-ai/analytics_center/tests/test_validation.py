"""Tests for validation helpers."""
from utils.validation import to_minutes, detect_overlaps, total_scheduled_minutes

def test_to_minutes():
    assert to_minutes("00:00") == 0
    assert to_minutes("01:30") == 90

def test_detect_overlaps():
    rows = [
        {"start_time": "09:00", "end_time": "10:00"},
        {"start_time": "09:30", "end_time": "09:45"},
        {"start_time": "11:00", "end_time": "12:00"},
    ]
    overlaps = detect_overlaps(rows)
    assert overlaps == [(0,1)]

def test_total_scheduled_minutes():
    rows = [
        {"start_time": "09:00", "end_time": "10:00"},
        {"duration": 30},
    ]
    assert total_scheduled_minutes(rows) == 90
