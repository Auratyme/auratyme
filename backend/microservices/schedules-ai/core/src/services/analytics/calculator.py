"""
Metric calculations for analytics.

Educational Note:
    Separating calculation logic from data fetching enables
    unit testing with controlled inputs and reuse across contexts.
"""

import logging
import statistics
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

STATS_LIBS_AVAILABLE = False

try:
    import pandas as pd
    import numpy as np
    from scipy.stats import linregress
    STATS_LIBS_AVAILABLE = True
except ImportError:
    STATS_LIBS_AVAILABLE = False
    logger.warning("Pandas/NumPy/SciPy not available. Using basic stats.")


def calculate_sleep_metrics(
    sleep_data_list: List[Any], consistency_scale: float = 2.0
) -> Tuple[Optional[float], Optional[float], Optional[float]]:
    """
    Calculates sleep duration, quality, and consistency metrics.
    
    Args:
        sleep_data_list: List of HistoricalSleepData objects
        consistency_scale: Scale factor for consistency scoring
    
    Returns:
        Tuple of (avg_duration, avg_quality, consistency_score)
    
    Educational Note:
        Standard deviation measures timing variance - dividing by
        scale factor normalizes to 0-1 range for interpretability.
    """
    durations = [
        d.actual_sleep_duration_minutes
        for d in sleep_data_list
        if d.actual_sleep_duration_minutes is not None
    ]
    
    qualities = [
        d.sleep_quality_score
        for d in sleep_data_list
        if d.sleep_quality_score is not None
    ]
    
    mid_sleeps = [
        d.mid_sleep_hour_local
        for d in sleep_data_list
        if d.mid_sleep_hour_local is not None
    ]
    
    avg_duration = statistics.mean(durations) if durations else None
    avg_quality = statistics.mean(qualities) if qualities else None
    
    consistency_score = None
    if len(mid_sleeps) > 1:
        stdev = statistics.stdev(mid_sleeps)
        consistency_score = max(0.0, 1.0 - (stdev / max(0.1, consistency_scale)))
    elif len(mid_sleeps) == 1:
        consistency_score = 1.0
    
    return avg_duration, avg_quality, consistency_score


def calculate_feedback_metrics(
    feedback_list: List[Any],
) -> Optional[float]:
    """
    Calculates average feedback rating.
    
    Args:
        feedback_list: List of UserFeedback objects
    
    Returns:
        Average rating (1-5) or None if no valid ratings
    
    Educational Note:
        Filtering invalid ratings (None or out-of-range) prevents
        data quality issues from contaminating statistical analysis.
    """
    valid_ratings = [
        f.rating
        for f in feedback_list
        if f.rating is not None and 1 <= f.rating <= 5
    ]
    
    if not valid_ratings:
        return None
    
    return statistics.mean(valid_ratings)


def calculate_productivity_metrics(
    schedules: List[Any],
) -> Tuple[Optional[float], Optional[float]]:
    """
    Calculates productivity metrics from schedule history.
    
    Args:
        schedules: List of GeneratedSchedule objects
    
    Returns:
        Tuple of (avg_scheduled_minutes, avg_tasks_completed)
    
    Educational Note:
        Subtracting unscheduled from scheduled gives completion
        estimate - assumes unscheduled tasks were deprioritized.
    """
    scheduled_minutes = [
        s.metrics.get("total_scheduled_task_minutes")
        for s in schedules
        if isinstance(s.metrics, dict)
        and s.metrics.get("total_scheduled_task_minutes") is not None
    ]
    
    completed_tasks = [
        s.metrics.get("scheduled_task_count", 0)
        - s.metrics.get("unscheduled_task_count", 0)
        for s in schedules
        if isinstance(s.metrics, dict)
        and s.metrics.get("scheduled_task_count") is not None
        and s.metrics.get("unscheduled_task_count") is not None
    ]
    
    avg_scheduled = statistics.mean(scheduled_minutes) if scheduled_minutes else None
    avg_completed = statistics.mean(completed_tasks) if completed_tasks else None
    
    return avg_scheduled, avg_completed


def calculate_productivity_trend(
    schedules: List[Any], min_points: int = 5
) -> Optional[float]:
    """
    Calculates productivity trend slope over time.
    
    Args:
        schedules: List of GeneratedSchedule objects
        min_points: Minimum data points required for trend
    
    Returns:
        Slope in minutes/day or None if insufficient data
    
    Educational Note:
        Linear regression (linregress) quantifies trend direction
        and strength - positive slope means increasing productivity.
    """
    metric_values = [
        (s.target_date, s.metrics.get("total_scheduled_task_minutes"))
        for s in schedules
        if isinstance(s.metrics, dict)
        and s.metrics.get("total_scheduled_task_minutes") is not None
    ]
    
    if len(metric_values) < min_points:
        return None
    
    if STATS_LIBS_AVAILABLE:
        try:
            df = pd.DataFrame(metric_values, columns=["date", "minutes"])
            df["date_ordinal"] = df["date"].apply(lambda d: d.toordinal())
            df = df.dropna()
            
            if len(df) < min_points:
                return None
            
            slope, _, _, p_value, _ = linregress(
                df["date_ordinal"], df["minutes"]
            )
            logger.debug(
                f"Calculated trend slope (linregress): {slope:.2f} "
                f"min/day (p={p_value:.3f})"
            )
            return slope
        except Exception as e:
            logger.error(f"Error calculating trend with SciPy: {e}")
            return None
    else:
        metric_values.sort()
        days_diff = (metric_values[-1][0] - metric_values[0][0]).days
        value_diff = metric_values[-1][1] - metric_values[0][1]
        
        if days_diff > 0:
            slope = value_diff / days_diff
            logger.debug(f"Calculated trend slope (basic): {slope:.2f} min/day")
            return slope
        
        return None
