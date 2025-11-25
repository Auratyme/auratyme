"""
Data models for wearable service.

Defines consolidated wearable data structure and utility functions.

Educational Note:
    Frozen dataclass ensures processed data immutability, preventing
    accidental mutations that could cause inconsistent state.
"""

import logging
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Any, Dict, Optional
from uuid import UUID

logger = logging.getLogger(__name__)


def format_timedelta(td: timedelta) -> str:
    """
    Formats timedelta as HH:MM string.
    
    Educational Note:
        Human-readable time formatting improves UX in logs and reports,
        converting technical timedelta objects into familiar format.
    """
    if td is None:
        return "N/A"
    
    total_minutes = int(td.total_seconds() // 60)
    hours = total_minutes // 60
    minutes = total_minutes % 60
    
    return f"{hours:02d}:{minutes:02d}"


def import_sleep_metrics():
    """
    Dynamically imports SleepMetrics from core.
    
    Educational Note:
        Dynamic import prevents circular dependencies between
        services and core modules.
    """
    try:
        from src.core.sleep import SleepMetrics
        return SleepMetrics
    except ImportError:
        logger.warning("SleepMetrics unavailable, using Any type")
        return Any


def import_activity_summary():
    """
    Dynamically imports ActivityDataSummary from adapter.
    
    Educational Note:
        Adapter types may not be available in all environments
        (e.g., testing without device integration).
    """
    try:
        from src.adapters.device_adapter import ActivityDataSummary
        return ActivityDataSummary
    except ImportError:
        logger.warning("ActivityDataSummary unavailable, using Any type")
        return Any


SleepMetrics = import_sleep_metrics()
ActivityDataSummary = import_activity_summary()


@dataclass(frozen=True)
class ProcessedWearableData:
    """
    Consolidated wearable data for specific target date.
    
    Educational Note:
        Frozen dataclass prevents accidental field mutations after creation,
        ensuring data integrity throughout processing pipeline.
    
    Attributes:
        user_id: User identifier
        target_date: Date this data pertains to
        sleep_analysis: Sleep period ending on target_date morning
        activity_summary: Activity metrics for target_date
        resting_hr_avg_bpm: Average heart rate during sleep (BPM)
        hrv_avg_rmssd_ms: Average HRV (RMSSD) during sleep (ms)
        raw_data_info: Source data metadata/references
    """
    user_id: UUID
    target_date: date
    sleep_analysis: Optional[Any] = None
    activity_summary: Optional[Any] = None
    resting_hr_avg_bpm: Optional[float] = None
    hrv_avg_rmssd_ms: Optional[float] = None
    raw_data_info: Dict[str, Any] = field(default_factory=dict)
