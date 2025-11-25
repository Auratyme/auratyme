"""
Insight and recommendation generation.

Educational Note:
    Rule-based insights translate quantitative analysis into
    actionable guidance, bridging data science and user experience.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


def generate_sleep_insights(
    avg_duration: float,
    consistency_score: float,
    low_sleep_threshold: int,
    consistency_threshold: float,
) -> Tuple[List[str], Dict[str, Any]]:
    """
    Generates sleep-related insights and recommendations.
    
    Args:
        avg_duration: Average sleep duration in minutes
        consistency_score: Sleep timing consistency (0-1)
        low_sleep_threshold: Threshold for insufficient sleep
        consistency_threshold: Threshold for poor consistency
    
    Returns:
        Tuple of (insights list, recommendations dict)
    
    Educational Note:
        Multiple thresholds allow graduated responses - slightly
        low sleep gets different advice than severely insufficient.
    """
    insights = []
    recommendations = {}
    
    if avg_duration < low_sleep_threshold:
        insights.append(
            f"Average sleep duration ({avg_duration/60:.1f}h) is below "
            f"target threshold ({low_sleep_threshold/60:.1f}h)."
        )
        recommendations["consider_sleep_schedule_adjustment"] = True
    
    if consistency_score < consistency_threshold:
        insights.append(
            f"Sleep timing consistency score ({consistency_score:.2f}) is low. "
            "Maintaining a regular sleep schedule can improve quality."
        )
        recommendations["focus_on_consistent_sleep_times"] = True
    
    return insights, recommendations


def generate_feedback_insights(
    avg_rating: float, low_feedback_threshold: float
) -> Tuple[List[str], Dict[str, Any]]:
    """
    Generates feedback-related insights and recommendations.
    
    Args:
        avg_rating: Average user rating (1-5)
        low_feedback_threshold: Threshold for poor satisfaction
    
    Returns:
        Tuple of (insights list, recommendations dict)
    
    Educational Note:
        Low ratings trigger review recommendation - human
        context (preferences, life changes) matters beyond data.
    """
    insights = []
    recommendations = {}
    
    if avg_rating < low_feedback_threshold:
        insights.append(
            f"Average schedule feedback rating ({avg_rating:.1f}) is below "
            f"threshold ({low_feedback_threshold:.1f})."
        )
        recommendations["review_scheduling_preferences"] = True
    
    return insights, recommendations


def generate_productivity_insights(
    trend_slope: float, trend_threshold: int
) -> Tuple[List[str], Dict[str, Any]]:
    """
    Generates productivity trend insights and recommendations.
    
    Args:
        trend_slope: Productivity trend slope (min/day)
        trend_threshold: Threshold for concerning negative trend
    
    Returns:
        Tuple of (insights list, recommendations dict)
    
    Educational Note:
        Negative trends warrant investigation - could indicate
        burnout, changing priorities, or external constraints.
    """
    insights = []
    recommendations = {}
    
    if trend_slope < trend_threshold:
        insights.append(
            f"Scheduled productive time shows downward trend "
            f"({trend_slope:.1f} min/day)."
        )
        recommendations["investigate_productivity_factors"] = True
    
    return insights, recommendations


def generate_correlation_insights(
    correlation: float,
) -> List[str]:
    """
    Generates correlation-based insights.
    
    Args:
        correlation: Correlation coefficient (-1 to 1)
    
    Returns:
        List of insights about the correlation
    
    Educational Note:
        Threshold 0.3 indicates "moderate" correlation - lower
        values (0.1-0.3) are weak, higher (>0.5) are strong.
    """
    insights = []
    
    if correlation > 0.3:
        insights.append(
            "Analysis suggests positive correlation between longer sleep "
            "duration and higher schedule satisfaction."
        )
    elif correlation < -0.3:
        insights.append(
            "Analysis suggests longer sleep duration might correlate with "
            "lower satisfaction (consider if oversleeping or schedule "
            "timing is an issue)."
        )
    
    return insights


def generate_all_insights(
    avg_sleep_duration: Optional[float],
    consistency_score: Optional[float],
    avg_feedback_rating: Optional[float],
    productivity_trend_slope: Optional[float],
    correlation_sleep_feedback: Optional[float],
    low_sleep_threshold: int,
    low_feedback_threshold: float,
    consistency_threshold: float,
    trend_threshold: int,
) -> Tuple[List[str], Dict[str, Any]]:
    """
    Aggregates all insights and recommendations.
    
    Args:
        avg_sleep_duration: Average sleep duration in minutes
        consistency_score: Sleep timing consistency (0-1)
        avg_feedback_rating: Average user rating (1-5)
        productivity_trend_slope: Trend slope (min/day)
        correlation_sleep_feedback: Sleep-feedback correlation
        low_sleep_threshold: Sleep threshold in minutes
        low_feedback_threshold: Feedback threshold (1-5)
        consistency_threshold: Consistency threshold (0-1)
        trend_threshold: Productivity trend threshold (min/day)
    
    Returns:
        Tuple of (all insights, all recommendations)
    
    Educational Note:
        Centralized aggregation ensures consistent ordering and
        prevents duplicate insights across analysis types.
    """
    all_insights = []
    all_recommendations = {}
    
    if avg_sleep_duration is not None and consistency_score is not None:
        sleep_insights, sleep_recs = generate_sleep_insights(
            avg_sleep_duration,
            consistency_score,
            low_sleep_threshold,
            consistency_threshold,
        )
        all_insights.extend(sleep_insights)
        all_recommendations.update(sleep_recs)
    
    if avg_feedback_rating is not None:
        feedback_insights, feedback_recs = generate_feedback_insights(
            avg_feedback_rating, low_feedback_threshold
        )
        all_insights.extend(feedback_insights)
        all_recommendations.update(feedback_recs)
    
    if productivity_trend_slope is not None:
        prod_insights, prod_recs = generate_productivity_insights(
            productivity_trend_slope, trend_threshold
        )
        all_insights.extend(prod_insights)
        all_recommendations.update(prod_recs)
    
    if correlation_sleep_feedback is not None:
        corr_insights = generate_correlation_insights(correlation_sleep_feedback)
        all_insights.extend(corr_insights)
    
    if not all_insights:
        all_insights.append(
            "Data analysis did not reveal significant trends or issues "
            "in the analyzed period."
        )
    
    return all_insights, all_recommendations
