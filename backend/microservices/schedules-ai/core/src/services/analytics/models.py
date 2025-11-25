"""
Analytics data models and structures.

Educational Note:
    Frozen dataclasses provide immutability for analysis results,
    preventing accidental modifications to historical insights.
"""

import logging
from dataclasses import dataclass, field
from datetime import date
from typing import Any, Dict, List, Optional
from uuid import UUID

logger = logging.getLogger(__name__)


@dataclass
class HistoricalSleepData:
    """
    Represents historical sleep metrics for a single day.
    
    Attributes:
        target_date: Date of the sleep session
        actual_sleep_duration_minutes: Total sleep time in minutes
        sleep_quality_score: Calculated quality score (0-100)
        mid_sleep_hour_local: Midpoint of sleep in local hour (0-24)
    
    Educational Note:
        Mid-sleep hour helps detect chronotype patterns - early
        birds have lower values (~3-4), night owls higher (~5-6).
    """
    target_date: date
    actual_sleep_duration_minutes: Optional[float] = None
    sleep_quality_score: Optional[float] = None
    mid_sleep_hour_local: Optional[float] = None


@dataclass(frozen=True)
class TrendAnalysisResult:
    """
    Structured output of historical trend analysis.
    
    Attributes:
        user_id: User being analyzed
        analysis_period_start_date: Analysis period start
        analysis_period_end_date: Analysis period end
        avg_sleep_duration_minutes: Average sleep duration
        avg_sleep_quality_score: Average sleep quality
        sleep_timing_consistency_score: Consistency (0-1, higher=better)
        avg_feedback_rating: Average user rating (1-5)
        avg_tasks_completed_per_day: Average daily task completion
        avg_scheduled_task_minutes: Average daily scheduled time
        productivity_trend_slope: Trend slope (min/day)
        correlation_sleep_duration_vs_feedback: Sleep-feedback correlation
        insights: Human-readable insights from analysis
        recommendations: Suggested adjustments/actions
    
    Educational Note:
        Frozen dataclass ensures analysis results remain immutable
        after creation, preventing accidental modifications during
        multi-step processing pipelines.
    """
    user_id: UUID
    analysis_period_start_date: date
    analysis_period_end_date: date
    avg_sleep_duration_minutes: Optional[float] = None
    avg_sleep_quality_score: Optional[float] = None
    sleep_timing_consistency_score: Optional[float] = None
    avg_feedback_rating: Optional[float] = None
    avg_tasks_completed_per_day: Optional[float] = None
    avg_scheduled_task_minutes: Optional[float] = None
    productivity_trend_slope: Optional[float] = None
    correlation_sleep_duration_vs_feedback: Optional[float] = None
    insights: List[str] = field(default_factory=list)
    recommendations: Dict[str, Any] = field(default_factory=dict)
