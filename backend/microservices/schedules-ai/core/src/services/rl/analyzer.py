"""
Trend and feedback analysis for parameter adaptation.

Analyzes historical trends and user feedback to suggest parameter adjustments.

Educational Note:
    Heuristic rules provide interpretable, predictable adaptations that
    users and developers can understand and debug without ML complexity.
    Duck typing enables testing with dummy objects without hard dependencies.
"""

import logging
from typing import Any, Dict, Optional
from uuid import UUID

from .models import AdaptationParameters

logger = logging.getLogger(__name__)


def analyze_sleep_trends(
    trend_analysis: Any,
    adaptations: AdaptationParameters,
    config: Dict[str, Any],
    adaptation_step: float
) -> None:
    """
    Adjusts sleep parameters based on trend analysis.
    
    Educational Note:
        Sleep deficit threshold (45min below 7h) indicates chronic under-rest
        requiring schedule adjustment to prioritize sleep.
    """
    if not hasattr(trend_analysis, 'avg_sleep_duration_minutes'):
        return
    
    avg_sleep = trend_analysis.avg_sleep_duration_minutes
    if avg_sleep is None:
        return
    
    threshold = config.get("low_sleep_threshold_minutes", 420)
    deficit = config.get("high_sleep_deficit_threshold_minutes", 45)
    
    if avg_sleep < (threshold - deficit):
        logger.info("Sleep deficit detected, increasing sleep need scale")
        adaptations.sleep_need_scale_adjustment += adaptation_step * 1.5


def analyze_productivity_trends(
    trend_analysis: Any,
    adaptations: AdaptationParameters,
    config: Dict[str, Any],
    adaptation_step: float
) -> None:
    """
    Adjusts priority weights based on productivity trends.
    
    Educational Note:
        Negative productivity slope suggests tasks not completing on time,
        indicating need to prioritize deadlines more aggressively.
    """
    if not hasattr(trend_analysis, 'productivity_trend_slope'):
        return
    
    slope = trend_analysis.productivity_trend_slope
    if slope is None:
        return
    
    threshold = config.get("negative_trend_threshold", -5)
    
    if slope < threshold:
        logger.info("Productivity declining, increasing deadline weight")
        current = adaptations.prioritizer_weight_adjustments.get("deadline", 0.0)
        adaptations.prioritizer_weight_adjustments["deadline"] = (
            current + adaptation_step
        )


def analyze_feedback_rating(
    feedback_analysis: Any,
    adaptations: AdaptationParameters,
    low_threshold: float,
    adaptation_step: float
) -> None:
    """
    Adjusts parameters based on user satisfaction rating.
    
    Educational Note:
        Very low ratings (< 2.0/5.0) indicate serious dissatisfaction,
        warranting aggressive parameter adjustments to improve UX.
    """
    if not hasattr(feedback_analysis, 'rating'):
        return
    
    rating = getattr(feedback_analysis, 'rating', None)
    if rating is None:
        return
    
    if rating < (low_threshold - 0.5):
        logger.info("Very low rating, strongly increasing priority weight")
        current = adaptations.prioritizer_weight_adjustments.get("priority", 0.0)
        adaptations.prioritizer_weight_adjustments["priority"] = (
            current + adaptation_step * 2
        )


def analyze_feedback_issues(
    feedback_analysis: Any,
    adaptations: AdaptationParameters,
    adaptation_step: float
) -> None:
    """
    Adjusts parameters based on specific user-reported issues.
    
    Educational Note:
        Issue-specific adaptations address root causes rather than
        applying generic fixes, improving adaptation precision.
    """
    if not hasattr(feedback_analysis, 'issues_identified'):
        return
    
    issues = getattr(feedback_analysis, 'issues_identified', [])
    
    handle_dense_schedule_issue(issues, adaptations, adaptation_step)
    handle_energy_misalignment_issue(issues, adaptations, adaptation_step)
    handle_sleep_issue(issues, adaptations, adaptation_step)


def handle_dense_schedule_issue(
    issues: list,
    adaptations: AdaptationParameters,
    adaptation_step: float
) -> None:
    """
    Adjusts for overly dense schedules.
    
    Educational Note:
        Dense schedules indicate too many dependencies or constraints,
        reducing dependency weight creates more scheduling flexibility.
    """
    if "schedule_too_dense" not in issues:
        return
    
    logger.info("Dense schedule reported, decreasing dependency weight")
    current = adaptations.prioritizer_weight_adjustments.get("dependencies", 0.0)
    adaptations.prioritizer_weight_adjustments["dependencies"] = (
        current - adaptation_step
    )


def handle_energy_misalignment_issue(
    issues: list,
    adaptations: AdaptationParameters,
    adaptation_step: float
) -> None:
    """
    Adjusts for energy-task misalignment.
    
    Educational Note:
        Energy misalignment (high-energy tasks at low-energy times) causes
        poor performance; increasing energy_match weight fixes this.
    """
    if "tasks_misaligned_with_energy" not in issues:
        return
    
    logger.info("Energy misalignment reported, increasing energy match weight")
    current = adaptations.prioritizer_weight_adjustments.get("energy_match", 0.0)
    adaptations.prioritizer_weight_adjustments["energy_match"] = (
        current + adaptation_step
    )


def handle_sleep_issue(
    issues: list,
    adaptations: AdaptationParameters,
    adaptation_step: float
) -> None:
    """
    Adjusts for sleep recommendation issues.
    
    Educational Note:
        Sleep problems can stem from schedule cutting into sleep time,
        increasing sleep_need_scale reserves more time for rest.
    """
    if "sleep_recommendation_off" not in issues:
        return
    
    logger.info("Sleep issues reported, increasing sleep need scale")
    adaptations.sleep_need_scale_adjustment += adaptation_step


def calculate_adaptations(
    user_id: UUID,
    trend_analysis: Optional[Any],
    feedback_analysis: Optional[Any],
    config: Dict[str, Any],
    adaptation_step: float,
    low_feedback_thr: float
) -> AdaptationParameters:
    """
    Main adaptation calculation orchestrator.
    
    Educational Note:
        Separates adaptation logic from data access, making it testable
        with mocked analytics/feedback without database dependencies.
        Uses duck typing instead of isinstance for flexibility.
    """
    logger.info(f"Calculating adaptations for user {user_id}")
    
    adaptations = AdaptationParameters()
    
    if trend_analysis:
        logger.debug(f"Analyzing trends: {trend_analysis}")
        analyze_sleep_trends(trend_analysis, adaptations, config, adaptation_step)
        analyze_productivity_trends(trend_analysis, adaptations, config, adaptation_step)
    
    if feedback_analysis:
        logger.debug(f"Analyzing feedback: {feedback_analysis}")
        analyze_feedback_rating(
            feedback_analysis, adaptations, low_feedback_thr, adaptation_step
        )
        analyze_feedback_issues(feedback_analysis, adaptations, adaptation_step)
    
    logger.info(f"Calculated adaptations: {adaptations}")
    return adaptations
