"""Tests for heuristic metrics."""
from utils.heuristics import build_heuristics

def test_heuristics_basic():
    rows = [
        {"start_time": "09:00", "end_time": "10:00", "energy_level": 3},
        {"start_time": "15:00", "end_time": "16:30", "energy_level": 4},
    ]
    prime = [{"start": "09:00", "end": "12:00"}, {"start": "14:00", "end": "17:00"}]
    metrics = build_heuristics(rows, prime)
    assert metrics["utilization_ratio"] > 0
    assert metrics["prime_energy_alignment"] is not None
