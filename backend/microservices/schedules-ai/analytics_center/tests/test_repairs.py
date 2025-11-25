"""Tests for repair pipeline."""
from utils.repairs import enforce_rounding, fill_missing_end, clamp_day, shift_collisions, apply_repairs

def test_enforce_rounding():
    rows = [{"start_time": "09:17", "end_time": "10:44", "rounding_flag": True}]
    out, changes = enforce_rounding(rows)
    assert out[0]["start_time"].endswith(":00") or out[0]["start_time"].endswith(":30")
    assert any(c["action"] == "rounded" for c in changes)

def test_fill_missing_end():
    rows = [{"start_time": "09:00", "duration": 30}]
    out, changes = fill_missing_end(rows)
    assert out[0]["end_time"] == "09:30"
    assert changes

def test_clamp_day():
    rows = [{"start_time": "23:50", "end_time": "25:10"}]
    out, changes = clamp_day(rows)
    assert out[0]["end_time"] <= "24:00"
    assert changes

def test_shift_collisions():
    rows = [
        {"start_time": "09:00", "end_time": "10:00"},
        {"start_time": "09:30", "end_time": "10:15"},
    ]
    out, changes = shift_collisions(rows)
    assert changes

def test_apply_repairs():
    rows = [{"start_time": "09:17", "end_time": "09:17", "duration": 30, "rounding_flag": True}]
    out, changes = apply_repairs(rows)
    assert changes
