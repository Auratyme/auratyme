"""Tests for wearable ingestion service."""
from services.wearable_ingest import parse_uploaded_file, ingest_wearable
from models.wearable import WearableMapping

def test_parse_csv():
    data = b"sleep_start,sleep_end,steps\n23:00,07:00,5000\n"
    recs = parse_uploaded_file("sample.csv", data)
    assert len(recs) == 1

def test_ingest_sleep_window():
    mapping = WearableMapping(sleep_start="sleep_start", sleep_end="sleep_end")
    data = b"sleep_start,sleep_end\n23:00,07:00\n"
    result = ingest_wearable("a.csv", data, mapping)
    assert result.features.total_sleep_minutes is not None
