"""
Wearable data processing orchestration.

Coordinates fetching and processing of wearable data from device adapter.

Educational Note:
    Separating orchestration logic from service initialization
    enables testing processing without full service context.
"""

import logging
import asyncio
from datetime import date, timedelta
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from .models import ProcessedWearableData

logger = logging.getLogger(__name__)


async def fetch_activity_summary(
    adapter: Any,
    user_id: UUID,
    target_date: date,
    source: Any
) -> Tuple[Optional[Any], Dict[str, Any]]:
    """
    Fetches activity summary for target date.
    
    Educational Note:
        Separate fetch functions enable retry logic and
        parallel processing of independent data sources.
    """
    raw_info = {}
    
    try:
        activity = await adapter.get_activity_summary(
            user_id, target_date, source
        )
        
        if activity:
            if hasattr(activity, 'source_record_id') and activity.source_record_id:
                raw_info["activity_record_id"] = activity.source_record_id
            
            logger.debug(f"Fetched activity: Steps={getattr(activity, 'steps', 'N/A')}")
            return activity, raw_info
        else:
            logger.info("No activity summary found")
            return None, raw_info
            
    except Exception as e:
        logger.error(f"Failed to get activity: {e}", exc_info=True)
        return None, raw_info


async def fetch_sleep_data(
    adapter: Any,
    user_id: UUID,
    start_date: date,
    end_date: date,
    source: Any
) -> List[Any]:
    """
    Fetches sleep records for date range.
    
    Educational Note:
        Range-based fetching (previous day to target) ensures
        we capture sleep sessions that started late previous night.
    """
    try:
        records = await adapter.get_sleep_data(
            user_id, start_date, end_date, source
        )
        return records
    except Exception as e:
        logger.error(f"Failed to get sleep data: {e}", exc_info=True)
        return []


async def fetch_physiological_data(
    adapter: Any,
    user_id: UUID,
    start_time: Any,
    end_time: Any,
    source: Any
) -> Tuple[List[Any], List[Any]]:
    """
    Fetches HR and HRV data during sleep period.
    
    Educational Note:
        Parallel fetching with asyncio.create_task reduces
        total wait time when adapter supports concurrent requests.
    """
    try:
        hr_task = asyncio.create_task(
            adapter.get_heart_rate_data(user_id, start_time, end_time, source)
        )
        hrv_task = asyncio.create_task(
            adapter.get_hrv_data(user_id, start_time, end_time, source)
        )
        
        hr_data = await hr_task
        hrv_data = await hrv_task
        
        logger.debug(
            f"Fetched {len(hr_data)} HR points, {len(hrv_data)} HRV points"
        )
        return hr_data, hrv_data
        
    except Exception as e:
        logger.error(f"Failed to fetch physiological data: {e}", exc_info=True)
        return [], []


def analyze_sleep_quality(
    sleep_calculator: Any,
    recommended: Any,
    sleep_record: Any,
    hr_data: List[Any],
    hrv_data: List[Any]
) -> Optional[Any]:
    """
    Analyzes sleep quality using calculator.
    
    Educational Note:
        Quality analysis requires recommended baseline for comparison,
        without it we can only report actual sleep duration/times.
    """
    if not recommended:
        logger.warning("No recommended sleep provided, skipping quality analysis")
        return create_basic_sleep_metrics(sleep_record)
    
    try:
        hr_tuples = [
            (p.timestamp, p.bpm) for p in hr_data
            if hasattr(p, 'timestamp') and hasattr(p, 'bpm')
        ]
        
        hrv_tuples = [
            (p.timestamp, p.rmssd_ms) for p in hrv_data
            if hasattr(p, 'timestamp') and 
               hasattr(p, 'rmssd_ms') and 
               p.rmssd_ms is not None
        ]
        
        analysis = sleep_calculator.analyze_sleep_quality(
            recommended=recommended,
            sleep_start=sleep_record.start_time,
            sleep_end=sleep_record.end_time,
            heart_rate_data=hr_tuples,
            hrv_data=hrv_tuples
        )
        
        logger.info(
            f"Sleep quality: {getattr(analysis, 'sleep_quality_score', 'N/A'):.1f}"
        )
        return analysis
        
    except Exception as e:
        logger.error(f"Sleep quality analysis failed: {e}", exc_info=True)
        return None


def create_basic_sleep_metrics(sleep_record: Any) -> Any:
    """
    Creates basic sleep metrics without quality score.
    
    Educational Note:
        Fallback metrics ensure some sleep data available
        even when full analysis impossible.
    """
    try:
        from src.core.sleep import SleepMetrics
        from datetime import time as time_class, timedelta as td
        
        return SleepMetrics(
            ideal_duration=td(0),
            ideal_bedtime=time_class(0, 0),
            ideal_wake_time=time_class(0, 0),
            actual_duration=sleep_record.duration,
            actual_bedtime=sleep_record.start_time.astimezone(None).time(),
            actual_wake_time=sleep_record.end_time.astimezone(None).time(),
        )
    except Exception as e:
        logger.error(f"Failed to create basic metrics: {e}")
        return None


def update_processed_data(
    processed_data: ProcessedWearableData,
    activity: Optional[Any],
    sleep_analysis: Optional[Any],
    resting_hr: Optional[float],
    hrv_rmssd: Optional[float],
    raw_info: Dict[str, Any]
) -> ProcessedWearableData:
    """
    Updates frozen dataclass using object.__setattr__.
    
    Educational Note:
        Frozen dataclass requires __setattr__ for updates,
        ensuring mutations are explicit and traceable.
    """
    if activity:
        object.__setattr__(processed_data, 'activity_summary', activity)
    
    if sleep_analysis:
        object.__setattr__(processed_data, 'sleep_analysis', sleep_analysis)
    
    if resting_hr:
        object.__setattr__(processed_data, 'resting_hr_avg_bpm', resting_hr)
    
    if hrv_rmssd:
        object.__setattr__(processed_data, 'hrv_avg_rmssd_ms', hrv_rmssd)
    
    if raw_info:
        object.__setattr__(processed_data, 'raw_data_info', raw_info)
    
    return processed_data


async def process_wearable_data(
    device_adapter: Any,
    sleep_calculator: Any,
    user_id: UUID,
    target_date: date,
    preferred_source: Any,
    recommended_sleep: Optional[Any],
    window_start_hour: int,
    window_end_hour: int
) -> ProcessedWearableData:
    """
    Main orchestrator for wearable data processing.
    
    Educational Note:
        Pipeline pattern breaks complex process into stages,
        each handling one concern (fetch, analyze, aggregate).
    
    Args:
        device_adapter: Adapter for device data access
        sleep_calculator: Calculator for sleep analysis
        user_id: User identifier
        target_date: Date to process data for
        preferred_source: Data source preference
        recommended_sleep: Recommended sleep for comparison
        window_start_hour: Sleep detection window start
        window_end_hour: Sleep detection window end
        
    Returns:
        Processed wearable data with all available metrics
    """
    logger.info(
        f"Processing wearable data for user {user_id} on {target_date} "
        f"from {getattr(preferred_source, 'name', 'unknown')}"
    )
    
    processed_data = ProcessedWearableData(
        user_id=user_id,
        target_date=target_date
    )
    
    activity, activity_info = await fetch_activity_summary(
        device_adapter, user_id, target_date, preferred_source
    )
    
    sleep_query_start = target_date - timedelta(days=1)
    sleep_records = await fetch_sleep_data(
        device_adapter, user_id, sleep_query_start, target_date, preferred_source
    )
    
    sleep_analysis = None
    resting_hr = None
    hrv_rmssd = None
    sleep_info = {}
    
    if sleep_records:
        from .sleep_finder import find_primary_sleep_session
        from .metrics import calculate_average_metric
        
        primary_sleep = find_primary_sleep_session(
            sleep_records, target_date, window_start_hour, window_end_hour
        )
        
        if primary_sleep:
            logger.info(
                f"Primary sleep: {primary_sleep.start_time} - "
                f"{primary_sleep.end_time}"
            )
            
            if hasattr(primary_sleep, 'source_record_id') and primary_sleep.source_record_id:
                sleep_info["sleep_record_id"] = primary_sleep.source_record_id
            
            hr_data, hrv_data = await fetch_physiological_data(
                device_adapter,
                user_id,
                primary_sleep.start_time,
                primary_sleep.end_time,
                preferred_source
            )
            
            resting_hr = calculate_average_metric(hr_data, 'bpm', "Resting HR")
            hrv_rmssd = calculate_average_metric(hrv_data, 'rmssd_ms', "HRV (RMSSD)")
            
            sleep_analysis = analyze_sleep_quality(
                sleep_calculator,
                recommended_sleep,
                primary_sleep,
                hr_data,
                hrv_data
            )
        else:
            logger.info(f"No primary sleep found for {target_date} morning")
    
    raw_info = {**activity_info, **sleep_info}
    
    processed_data = update_processed_data(
        processed_data,
        activity,
        sleep_analysis,
        resting_hr,
        hrv_rmssd,
        raw_info
    )
    
    logger.info(f"Processing complete for user {user_id}, date {target_date}")
    return processed_data
