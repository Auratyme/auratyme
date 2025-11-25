"""
Sleep session identification for wearable data.

Finds primary sleep session from multiple sleep records.

Educational Note:
    Sleep detection logic isolated for testing and tuning
    without affecting other wearable processing functionality.
"""

import logging
from datetime import date, datetime, timezone
from typing import Any, List, Optional

logger = logging.getLogger(__name__)


def find_primary_sleep_session(
    sleep_records: List[Any],
    target_date: date,
    window_start_hour: int,
    window_end_hour: int
) -> Optional[Any]:
    """
    Identifies main sleep session ending on target date morning.
    
    Educational Note:
        Longest-sleep heuristic works for most users but may need
        adaptation for polyphasic sleepers or shift workers.
    
    Args:
        sleep_records: List of sleep data records
        target_date: Date to find sleep for
        window_start_hour: Start hour of detection window (0-23)
        window_end_hour: End hour of detection window (0-23)
        
    Returns:
        Primary sleep record or None if not found
    """
    if not sleep_records:
        return None
    
    from .config import create_sleep_window_times
    window_start, window_end = create_sleep_window_times(
        window_start_hour, window_end_hour
    )
    
    target_start_dt = datetime.combine(target_date, window_start, tzinfo=timezone.utc)
    target_end_dt = datetime.combine(target_date, window_end, tzinfo=timezone.utc)
    
    relevant_records = filter_records_in_window(
        sleep_records, target_start_dt, target_end_dt
    )
    
    if not relevant_records:
        return None
    
    return select_longest_sleep(relevant_records)


def filter_records_in_window(
    records: List[Any],
    window_start: datetime,
    window_end: datetime
) -> List[Any]:
    """
    Filters sleep records ending within time window.
    
    Educational Note:
        Timezone handling critical for accurate sleep detection
        across daylight saving transitions and user travel.
    """
    relevant = []
    
    for record in records:
        if not is_record_timezone_aware(record):
            logger.warning(
                f"Skipping timezone-naive record: "
                f"{getattr(record, 'source_record_id', 'unknown')}"
            )
            continue
        
        record_end_utc = record.end_time.astimezone(timezone.utc)
        
        if window_start <= record_end_utc <= window_end:
            relevant.append(record)
    
    return relevant


def is_record_timezone_aware(record: Any) -> bool:
    """
    Checks if sleep record has timezone-aware timestamps.
    
    Educational Note:
        Timezone-naive datetimes cause subtle bugs in sleep detection
        when users cross time zones or during DST changes.
    """
    if not hasattr(record, 'start_time') or not hasattr(record, 'end_time'):
        return False
    
    return (
        record.start_time.tzinfo is not None and
        record.end_time.tzinfo is not None
    )


def select_longest_sleep(records: List[Any]) -> Any:
    """
    Selects longest sleep from candidate records.
    
    Educational Note:
        Duration-based selection assumes primary sleep is longest
        period, filtering out naps and awake periods.
    """
    return max(records, key=lambda r: r.duration)
