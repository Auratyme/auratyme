"""
LLM context preparation for schedule generation.

This module creates comprehensive context for LLM-based schedule refinement,
including user profiles, wearable data, and historical patterns.
"""

import logging
from typing import TYPE_CHECKING, Any, Dict, List

from src.services.llm import ScheduleGenerationContext, RAGContext

if TYPE_CHECKING:
    from src.core.scheduler.models import ScheduleInputData, ScheduleChronotypeContext
    from src.core.sleep import SleepMetrics
    from src.core.task import TaskPrioritizer

logger = logging.getLogger(__name__)


def create_llm_context(
    input_data: "ScheduleInputData",
    chronotype_context: "ScheduleChronotypeContext",
    sleep_metrics: "SleepMetrics",
    task_prioritizer: "TaskPrioritizer",
    wearable_service: Any,
    history_service: Any,
    all_fixed_events: List[Dict[str, Any]] = None
) -> ScheduleGenerationContext:
    """
    Creates context for the LLM engine.
    
    Educational Note:
        Aggregates multiple data sources (profile, wearables, history)
        into unified context that LLM uses for personalized refinement.
        
        all_fixed_events includes ALL solver-added events (routines, lunch)
        not just user's original fixed events.
    """
    wearable_insights = get_wearable_insights(
        input_data, wearable_service
    )
    historical_insights = get_historical_insights(
        input_data, history_service
    )
    
    user_profile_data = input_data.user_profile_data or {}
    
    fixed_events_for_llm = all_fixed_events if all_fixed_events is not None else input_data.fixed_events_input
    
    return ScheduleGenerationContext(
        user_id=input_data.user_id,
        user_name=user_profile_data.get("name", "User"),
        target_date=input_data.target_date,
        chronotype=chronotype_context.chronotype,
        prime_window=chronotype_context.prime_window,
        preferences=input_data.preferences,
        tasks=input_data.tasks,
        fixed_events=fixed_events_for_llm,
        sleep_recommendation=sleep_metrics,
        energy_pattern=task_prioritizer.get_energy_pattern(chronotype_context),
        wearable_insights=wearable_insights,
        historical_insights=historical_insights,
        rag_context=RAGContext(),
        previous_feedback=input_data.historical_data
    )


def get_wearable_insights(
    input_data: "ScheduleInputData",
    wearable_service: Any
) -> Dict[str, Any]:
    """
    Fetches and processes wearable insights for schedule personalization.
    
    Educational Note:
        Wearable data (sleep quality, stress, heart rate) informs
        activity recommendations and focus period timing.
    """
    if not _has_wearable_service(wearable_service):
        logger.debug("Wearable service not available.")
        return {}
    
    try:
        logger.info("SIMULATING wearable insights fetch.")
        raw_data = _extract_wearable_data(input_data)
        return _create_wearable_insights(raw_data)
    except Exception as e:
        logger.error(f"Error fetching wearable insights: {e}", exc_info=True)
        return {}


def _has_wearable_service(service: Any) -> bool:
    """
    Checks if wearable service is properly configured.
    
    Educational Note:
        Duck typing check ensures service has required method
        without hard coupling to specific service implementation.
    """
    return service and hasattr(service, 'get_insights_for_day')


def _extract_wearable_data(
    input_data: "ScheduleInputData"
) -> Dict[str, Any]:
    """
    Extracts wearable data from input with defaults.
    
    Educational Note:
        Provides reasonable defaults when wearable data unavailable,
        ensuring schedule generation continues smoothly.
    """
    if input_data.wearable_data_today:
        return input_data.wearable_data_today
    
    return {
        "sleep_quality": "Good",
        "stress_level": "Low",
        "readiness_score": 0.85,
        "steps_yesterday": 8500,
        "avg_heart_rate": 68
    }


def _create_wearable_insights(
    raw_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Creates structured insights from raw wearable data.
    
    Educational Note:
        Combines multiple metrics into actionable recommendations
        like activity intensity and optimal focus periods.
    """
    sleep_quality = raw_data.get("sleep_quality", "Good")
    stress_level = raw_data.get("stress_level", "Low")
    readiness_score = raw_data.get("readiness_score", 0.85)
    
    return {
        "sleep_quality": sleep_quality,
        "stress_level": stress_level,
        "readiness_score": readiness_score,
        "steps_yesterday": raw_data.get("steps_yesterday", 8500),
        "avg_heart_rate": raw_data.get("avg_heart_rate", 68),
        "recovery_needed": _needs_recovery(sleep_quality, stress_level),
        "activity_recommendation": get_activity_recommendation(
            sleep_quality, stress_level, readiness_score
        ),
        "focus_periods": get_focus_periods(
            sleep_quality, readiness_score
        )
    }


def _needs_recovery(
    sleep_quality: str,
    stress_level: str
) -> bool:
    """
    Determines if user needs recovery time.
    
    Educational Note:
        Poor sleep or high stress indicate need for lighter schedule
        with more rest periods.
    """
    return stress_level == "High" or sleep_quality == "Poor"


def get_activity_recommendation(
    sleep_quality: str,
    stress_level: str,
    readiness_score: float
) -> str:
    """
    Generate activity recommendation based on wearable data.
    
    Educational Note:
        Tiered recommendations prevent overexertion when body
        indicators suggest reduced capacity for intense activity.
    """
    if _should_recommend_light_activity(
        sleep_quality, stress_level, readiness_score
    ):
        return "Light activity only (walking, stretching)"
    
    if _should_recommend_moderate_activity(
        sleep_quality, stress_level, readiness_score
    ):
        return "Moderate activity (light cardio, yoga)"
    
    return "Full intensity workout ok"


def _should_recommend_light_activity(
    sleep_quality: str,
    stress_level: str,
    readiness_score: float
) -> bool:
    """
    Checks if only light activity is recommended.
    
    Educational Note:
        Multiple warning signs (poor sleep, high stress, low readiness)
        all suggest need for recovery rather than intense activity.
    """
    return (
        sleep_quality == "Poor" or
        stress_level == "High" or
        readiness_score < 0.6
    )


def _should_recommend_moderate_activity(
    sleep_quality: str,
    stress_level: str,
    readiness_score: float
) -> bool:
    """
    Checks if moderate activity is recommended.
    
    Educational Note:
        Fair conditions suggest capability for moderate exercise
        without risking overexertion or compromised recovery.
    """
    return (
        sleep_quality == "Fair" or
        stress_level == "Medium" or
        readiness_score < 0.8
    )


def get_focus_periods(
    sleep_quality: str,
    readiness_score: float
) -> List[str]:
    """
    Generate recommended focus periods based on sleep and readiness.
    
    Educational Note:
        Cognitive performance correlates with sleep quality and readiness.
        Fewer/shorter focus periods when capacity is reduced.
    """
    if sleep_quality == "Poor" or readiness_score < 0.6:
        return ["10:00-11:30"]
    
    if sleep_quality == "Fair" or readiness_score < 0.8:
        return ["09:30-11:30", "15:00-16:30"]
    
    return ["09:00-12:00", "14:30-17:00"]


def get_historical_insights(
    input_data: "ScheduleInputData",
    history_service: Any
) -> Dict[str, Any]:
    """
    Fetches and processes historical insights for schedule personalization.
    
    Educational Note:
        Historical patterns (typical lunch time, productive hours,
        completion rates) help LLM create realistic, achievable schedules.
    """
    if not _has_history_service(history_service):
        logger.debug("History service not available.")
        return {}
    
    try:
        logger.info("SIMULATING historical insights fetch.")
        historical_data = input_data.historical_data or {}
        weekday = input_data.target_date.strftime("%a").lower()
        
        return _create_historical_insights(historical_data, weekday)
    except Exception as e:
        logger.error(f"Error fetching historical insights: {e}", exc_info=True)
        return {}


def _has_history_service(service: Any) -> bool:
    """
    Checks if history service is properly configured.
    
    Educational Note:
        Same duck typing pattern as wearable service check,
        allowing flexible service implementations.
    """
    return service and hasattr(service, 'get_recent_patterns')


def _create_historical_insights(
    historical_data: Dict[str, Any],
    weekday: str
) -> Dict[str, Any]:
    """
    Creates structured insights from historical data.
    
    Educational Note:
        Combines user-specific patterns with day-specific norms
        to create context-aware schedule recommendations.
    """
    return {
        "typical_lunch": historical_data.get("typical_lunch_time", "13:05"),
        "common_activity": historical_data.get(
            "common_activity", "Evening walk around 18:00"
        ),
        "avg_task_completion_time_vs_estimate_ratio": historical_data.get(
            "task_completion_ratio", 1.1
        ),
        "productive_hours": historical_data.get(
            "productive_hours", ["09:00-12:00", "15:00-17:00"]
        ),
        "common_breaks": historical_data.get(
            "common_breaks", ["10:30", "15:30"]
        ),
        "day_specific_patterns": get_day_specific_patterns(weekday),
        "task_completion_success_rate": 0.85,
        "common_distractions": ["email checking", "social media"],
        "optimal_task_duration": 45,
        "typical_sleep_duration": 7.5
    }


def get_day_specific_patterns(weekday: str) -> Dict[str, Any]:
    """
    Generate day-specific patterns based on day of week.
    
    Educational Note:
        Productivity and energy levels vary by day (e.g., Monday high,
        Friday variable). Day-specific patterns help LLM create realistic
        schedules that match typical weekly rhythms.
    """
    patterns = {
        "mon": {
            "productivity": "high",
            "common_activities": ["team meeting", "planning"],
            "typical_end_time": "18:00"
        },
        "tue": {
            "productivity": "high",
            "common_activities": ["focused work"],
            "typical_end_time": "18:30"
        },
        "wed": {
            "productivity": "medium",
            "common_activities": ["mid-week review"],
            "typical_end_time": "17:30"
        },
        "thu": {
            "productivity": "medium",
            "common_activities": ["collaborative work"],
            "typical_end_time": "18:00"
        },
        "fri": {
            "productivity": "variable",
            "common_activities": ["weekly wrap-up", "social event"],
            "typical_end_time": "16:30"
        },
        "sat": {
            "productivity": "low",
            "common_activities": ["personal projects", "family time"],
            "typical_end_time": "flexible"
        },
        "sun": {
            "productivity": "low",
            "common_activities": ["preparation for week", "relaxation"],
            "typical_end_time": "flexible"
        }
    }
    
    return patterns.get(
        weekday,
        {"productivity": "medium", "typical_end_time": "18:00"}
    )
