"""
Analytics package for historical data analysis.

Usage:
    from src.services.analytics import AnalyticsService, TrendAnalysisResult
    
    service = AnalyticsService(config={"analytics_params": {...}})
    result = await service.analyze_trends(user_id, period_days=14)
"""

from .models import HistoricalSleepData, TrendAnalysisResult
from .service import AnalyticsService
from .config import DEFAULT_ANALYTICS_PARAMS

__all__ = [
    "AnalyticsService",
    "TrendAnalysisResult",
    "HistoricalSleepData",
    "DEFAULT_ANALYTICS_PARAMS",
]
