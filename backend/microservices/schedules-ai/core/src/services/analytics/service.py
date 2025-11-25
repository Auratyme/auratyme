"""
Analytics Service main orchestration.

Educational Note:
    Service layer coordinates multiple specialized modules,
    keeping each focused on single responsibility.
"""

import logging
from datetime import date, timedelta
from typing import Any, Dict, Optional
from uuid import UUID

from .models import TrendAnalysisResult
from .config import initialize_analytics_config, extract_thresholds
from .fetcher import fetch_historical_data
from .calculator import (
    calculate_sleep_metrics,
    calculate_feedback_metrics,
    calculate_productivity_metrics,
    calculate_productivity_trend,
)
from .correlator import calculate_sleep_feedback_correlation
from .insights import generate_all_insights

logger = logging.getLogger(__name__)


class AnalyticsService:
    """
    Performs historical data analysis for user insights.
    
    Educational Note:
        Thin service class delegates to specialized modules,
        maintaining clear separation between configuration,
        data fetching, calculations, and insight generation.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """
        Initializes AnalyticsService with configuration.
        
        Args:
            config: Configuration dictionary with analytics_params, db_uri
        
        Educational Note:
            Configuration handled by dedicated module simplifies
            testing and allows parameter tuning without service changes.
        """
        self._config = config or {}
        self._analytics_params = initialize_analytics_config(self._config)
        
        db_uri = self._config.get("db_uri")
        if db_uri:
            self._db_client = "mock_db_client"
            logger.info(f"AnalyticsService initialized with DB: {db_uri[:10]}...")
        else:
            self._db_client = None
            logger.warning("AnalyticsService initialized WITHOUT database. Using mocks.")
    
    async def analyze_trends(
        self,
        user_id: UUID,
        period_days: int = 7,
    ) -> Optional[TrendAnalysisResult]:
        """
        Analyzes user trends over specified period.
        
        Args:
            user_id: User to analyze
            period_days: Analysis window in days
        
        Returns:
            TrendAnalysisResult with metrics and insights, or None on error
        
        Educational Note:
            Pipeline: fetch → calculate metrics → correlate → generate insights.
            Each stage isolated in separate module for testability.
        """
        if period_days <= 1:
            logger.error(f"Period must be > 1 day, got {period_days}.")
            return None
        
        end_date = date.today() - timedelta(days=1)
        start_date = end_date - timedelta(days=period_days - 1)
        
        logger.info(
            f"Analyzing trends for user {user_id} from {start_date} "
            f"to {end_date} ({period_days} days)"
        )
        
        try:
            historical_data = await fetch_historical_data(
                user_id, start_date, end_date, self._db_client
            )
            
            schedules = historical_data.get("schedules", [])
            feedback_list = historical_data.get("feedback", [])
            sleep_data_list = historical_data.get("sleep_data", [])
            
            if not schedules and not feedback_list and not sleep_data_list:
                logger.warning(f"No historical data for user {user_id}.")
                return TrendAnalysisResult(
                    user_id=user_id,
                    analysis_period_start_date=start_date,
                    analysis_period_end_date=end_date,
                    insights=["No historical data found for the selected period."],
                )
            
            result = TrendAnalysisResult(
                user_id=user_id,
                analysis_period_start_date=start_date,
                analysis_period_end_date=end_date,
            )
            
            min_points = self._analytics_params.get("min_data_points_for_trend", 5)
            consistency_scale = self._analytics_params.get("consistency_stdev_scale", 2.0)
            
            if sleep_data_list:
                avg_duration, avg_quality, consistency = calculate_sleep_metrics(
                    sleep_data_list, consistency_scale
                )
                object.__setattr__(result, "avg_sleep_duration_minutes", avg_duration)
                object.__setattr__(result, "avg_sleep_quality_score", avg_quality)
                object.__setattr__(result, "sleep_timing_consistency_score", consistency)
            
            if feedback_list:
                avg_rating = calculate_feedback_metrics(feedback_list)
                object.__setattr__(result, "avg_feedback_rating", avg_rating)
            
            if schedules:
                avg_scheduled, avg_completed = calculate_productivity_metrics(schedules)
                object.__setattr__(result, "avg_scheduled_task_minutes", avg_scheduled)
                object.__setattr__(result, "avg_tasks_completed_per_day", avg_completed)
                
                trend_slope = calculate_productivity_trend(schedules, min_points)
                object.__setattr__(result, "productivity_trend_slope", trend_slope)
            
            if sleep_data_list and feedback_list:
                correlation = calculate_sleep_feedback_correlation(
                    sleep_data_list, feedback_list, min_points
                )
                object.__setattr__(result, "correlation_sleep_duration_vs_feedback", correlation)
            
            low_sleep, low_feedback, consistency_thresh, trend_thresh = extract_thresholds(
                self._analytics_params
            )
            
            insights, recommendations = generate_all_insights(
                result.avg_sleep_duration_minutes,
                result.sleep_timing_consistency_score,
                result.avg_feedback_rating,
                result.productivity_trend_slope,
                result.correlation_sleep_duration_vs_feedback,
                low_sleep,
                low_feedback,
                consistency_thresh,
                trend_thresh,
            )
            
            result.insights.extend(insights)
            result.recommendations.update(recommendations)
            
            logger.info(f"Trend analysis complete for user {user_id}. {len(result.insights)} insights.")
            return result
        
        except Exception:
            logger.exception(f"Error during trend analysis for user {user_id}")
            return None
