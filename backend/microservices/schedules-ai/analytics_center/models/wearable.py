"""Wearable ingestion models.

These schemas describe raw uploaded records, user-provided column mapping,
extracted feature aggregates, and conversion to canonical inputs.
"""
from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any

class WearableMapping(BaseModel):
    """Column name mapping provided by user for CSV/JSON ingestion."""
    sleep_start: Optional[str] = None
    sleep_end: Optional[str] = None
    sleep_quality: Optional[str] = None
    steps: Optional[str] = None
    heart_rate_avg: Optional[str] = None
    stress_level: Optional[str] = None
    readiness_score: Optional[str] = None
    activity_start: Optional[str] = None
    activity_end: Optional[str] = None
    activity_type: Optional[str] = None
    intensity: Optional[str] = None

class WearableRawRecord(BaseModel):
    """Single raw wearable row (loosely typed)."""
    data: Dict[str, Any]

class ExtractedFeatures(BaseModel):
    """Aggregated features derived from wearable data."""
    total_sleep_minutes: Optional[int] = None
    main_sleep_window: Optional[str] = None
    sleep_quality: Optional[str] = None
    readiness_score: Optional[float] = None
    stress_level: Optional[str] = None
    steps_total: Optional[int] = None
    activity_blocks: List[Dict[str, Any]] = Field(default_factory=list)

class WearableIngestionResult(BaseModel):
    """Full ingestion result containing normalized features and diagnostics."""
    features: ExtractedFeatures
    mapping_used: WearableMapping
    raw_count: int
    notes: List[str] = Field(default_factory=list)
