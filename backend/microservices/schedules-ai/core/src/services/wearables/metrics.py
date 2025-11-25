"""
Metric calculation utilities for wearable data.

Calculates averages from physiological data points.

Educational Note:
    Separating calculation logic enables unit testing without
    full wearable integration, improving test coverage.
"""

import logging
import statistics
from typing import Any, List, Optional

logger = logging.getLogger(__name__)


def calculate_average_metric(
    data_points: List[Any],
    attribute_name: str,
    metric_name: str
) -> Optional[float]:
    """
    Calculates average of specific attribute from data points.
    
    Educational Note:
        Filters invalid values (None, <=0) before averaging,
        ensuring statistical validity and preventing skewed results.
    
    Args:
        data_points: List of data point objects
        attribute_name: Name of attribute to average
        metric_name: Human-readable metric name for logging
        
    Returns:
        Average value or None if no valid data
    """
    if not data_points:
        logger.debug(f"No data points for {metric_name}")
        return None
    
    valid_values = extract_valid_values(data_points, attribute_name)
    
    if not valid_values:
        logger.debug(f"No valid '{attribute_name}' values for {metric_name}")
        return None
    
    return compute_mean(valid_values, metric_name)


def extract_valid_values(data_points: List[Any], attribute: str) -> List[float]:
    """
    Extracts valid numeric values from data points.
    
    Educational Note:
        Three-stage filtering (hasattr, not None, > 0) ensures
        only meaningful physiological values included in calculations.
    """
    valid = []
    
    for point in data_points:
        if not hasattr(point, attribute):
            continue
        
        value = getattr(point, attribute)
        
        if value is None or value <= 0:
            continue
        
        valid.append(value)
    
    return valid


def compute_mean(values: List[float], metric_name: str) -> Optional[float]:
    """
    Computes mean with error handling.
    
    Educational Note:
        Catching StatisticsError handles edge cases (empty list)
        while generic Exception catches unexpected issues.
    """
    try:
        average = statistics.mean(values)
        logger.debug(
            f"Calculated {metric_name}: {average:.2f} "
            f"from {len(values)} points"
        )
        return average
    except statistics.StatisticsError as e:
        logger.warning(f"Could not calculate mean {metric_name}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error calculating {metric_name}: {e}")
        return None
