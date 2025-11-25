"""
Data models for adaptive engine (RL) service.

Defines adaptation parameters and placeholder models for optional dependencies.

Educational Note:
    Dummy classes with dataclasses enable graceful degradation when optional
    analytics/feedback modules unavailable, keeping service functional.
"""

import logging
from dataclasses import dataclass, field
from datetime import date
from typing import Any, Dict, List, Optional
from uuid import UUID

logger = logging.getLogger(__name__)


@dataclass
class AdaptationParameters:
    """
    Represents suggested adjustments to scheduling parameters.
    
    Educational Note:
        Small delta adjustments (±0.05-0.15) allow gradual parameter tuning
        without drastic schedule changes that might confuse users.
    """
    sleep_need_scale_adjustment: float = 0.0
    chronotype_scale_adjustment: float = 0.0
    prioritizer_weight_adjustments: Dict[str, float] = field(default_factory=dict)


def import_trend_analysis():
    """
    Dynamically imports TrendAnalysisResult from analytics service.
    
    Educational Note:
        Dynamic imports with fallbacks prevent circular dependencies
        and allow RL engine to work even if analytics unavailable.
    """
    try:
        from src.services.analytics import TrendAnalysisResult
        logger.debug("TrendAnalysisResult imported successfully")
        return TrendAnalysisResult, True
    except ImportError as e:
        logger.warning(f"TrendAnalysisResult unavailable: {e}")
        return create_dummy_trend_analysis(), False


def create_dummy_trend_analysis():
    """
    Creates placeholder TrendAnalysisResult for fallback.
    
    Educational Note:
        Duck typing with dataclass mimics real class interface,
        allowing code to run without modifications when dependency missing.
    """
    @dataclass
    class DummyTrendAnalysisResult:
        """Placeholder trend analysis result."""
        user_id: UUID
        analysis_period_start_date: date
        analysis_period_end_date: date
        avg_sleep_duration_minutes: Optional[float] = None
        productivity_trend_slope: Optional[float] = None
        insights: List[str] = field(default_factory=list)
        recommendations: Dict[str, Any] = field(default_factory=dict)
    
    return DummyTrendAnalysisResult


def import_feedback_analysis():
    """
    Dynamically imports FeedbackAnalysis from feedback processor.
    
    Educational Note:
        Isolates feedback module dependency, making RL engine testable
        without full feedback infrastructure.
    """
    try:
        from feedback.processors.analyzer import FeedbackAnalysis
        logger.debug("FeedbackAnalysis imported successfully")
        return FeedbackAnalysis, True
    except Exception as e:
        logger.warning(f"FeedbackAnalysis unavailable: {e}")
        return create_dummy_feedback_analysis(), False


def create_dummy_feedback_analysis():
    """
    Creates placeholder FeedbackAnalysis for fallback.
    
    Educational Note:
        Minimal interface (rating, issues) covers most adaptation use cases
        even when full feedback analysis unavailable.
    """
    @dataclass
    class DummyFeedbackAnalysis:
        """Placeholder feedback analysis result."""
        rating: Optional[int] = None
        issues_identified: List[str] = field(default_factory=list)
    
    return DummyFeedbackAnalysis


TrendAnalysisResult, TREND_AVAILABLE = import_trend_analysis()
FeedbackAnalysis, FEEDBACK_AVAILABLE = import_feedback_analysis()
DATA_MODELS_AVAILABLE = TREND_AVAILABLE
