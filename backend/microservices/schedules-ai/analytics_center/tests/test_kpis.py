"""Tests for KPI computation."""
from utils.kpis import build_kpis

def test_kpis_basic():
    requested = [{"duration_minutes": 60}, {"duration_minutes": 120}]
    scheduled = [
        {"start_time": "09:00", "end_time": "10:00"},
        {"start_time": "10:30", "end_time": "12:00"},
    ]
    k = build_kpis(requested, scheduled)
    assert k['total_scheduled_minutes'] == 150
    assert k['utilization_ratio'] > 0
