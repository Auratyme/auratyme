"""
Correlation analysis between metrics.

Educational Note:
    Correlation coefficients quantify relationships between variables,
    revealing whether improving one metric (e.g., sleep) affects another (e.g., satisfaction).
"""

import logging
from typing import Any, List, Optional

logger = logging.getLogger(__name__)

STATS_LIBS_AVAILABLE = False

try:
    import pandas as pd
    import numpy as np
    STATS_LIBS_AVAILABLE = True
except ImportError:
    STATS_LIBS_AVAILABLE = False
    logger.warning("Pandas/NumPy not available. Correlation disabled.")


def calculate_sleep_feedback_correlation(
    sleep_data_list: List[Any],
    feedback_list: List[Any],
    min_points: int = 5,
) -> Optional[float]:
    """
    Calculates correlation between sleep duration and feedback rating.
    
    Args:
        sleep_data_list: List of HistoricalSleepData objects
        feedback_list: List of UserFeedback objects
        min_points: Minimum overlapping data points required
    
    Returns:
        Correlation coefficient (-1 to 1) or None if insufficient data
    
    Educational Note:
        Merging on date ensures paired observations - correlation
        requires matching sleep/feedback for same day, not just
        independent lists of values.
    """
    if not STATS_LIBS_AVAILABLE:
        logger.debug("Correlation requires Pandas/NumPy (not available).")
        return None
    
    try:
        sleep_df = pd.DataFrame([
            {"date": d.target_date, "sleep": d.actual_sleep_duration_minutes}
            for d in sleep_data_list
            if d.actual_sleep_duration_minutes
        ])
        
        feedback_df = pd.DataFrame([
            {"date": f.schedule_date, "rating": f.rating}
            for f in feedback_list
            if f.rating
        ])
        
        if sleep_df.empty or feedback_df.empty:
            return None
        
        merged = pd.merge(sleep_df, feedback_df, on="date").dropna()
        
        if len(merged) < min_points:
            logger.debug(
                f"Insufficient paired data: {len(merged)} < {min_points}"
            )
            return None
        
        correlation_matrix = np.corrcoef(merged["sleep"], merged["rating"])
        correlation = correlation_matrix[0, 1]
        
        if np.isnan(correlation):
            return None
        
        logger.debug(
            f"Calculated Sleep vs Feedback correlation: {correlation:.2f}"
        )
        return correlation
    
    except Exception as e:
        logger.error(f"Error calculating correlation: {e}")
        return None
