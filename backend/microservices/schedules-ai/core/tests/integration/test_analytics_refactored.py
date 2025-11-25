"""
Integration tests for analytics package refactoring.

Validates that refactored analytics/ package works correctly.

Educational Note:
    Analytics testing validates statistical calculations, mock data
    generation, and insight generation rules work as designed.
"""

import sys
import logging
from pathlib import Path
from uuid import uuid4
from datetime import date, timedelta

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_imports():
    """
    Test 1: Verify analytics package exports importable.
    
    Educational Note:
        Import test catches missing __all__ exports or broken
        dependencies preventing package loading.
    """
    logger.info("\nTest 1: Testing imports from analytics package...")
    
    try:
        from src.services.analytics import (
            AnalyticsService,
            TrendAnalysisResult,
            HistoricalSleepData,
            DEFAULT_ANALYTICS_PARAMS,
        )
        logger.info("✓ All imports successful")
        return True
    except ImportError as e:
        logger.error(f"✗ Import failed: {e}")
        return False


def test_package_structure():
    """
    Test 2: Verify analytics package structure complete.
    
    Educational Note:
        Structure test ensures internal modules accessible
        and properly organized within package.
    """
    logger.info("\nTest 2: Testing package structure...")
    
    try:
        from src.services import analytics
        
        required_attrs = [
            'AnalyticsService',
            'TrendAnalysisResult',
            'HistoricalSleepData',
            'DEFAULT_ANALYTICS_PARAMS',
        ]
        
        missing = [attr for attr in required_attrs if not hasattr(analytics, attr)]
        
        if missing:
            logger.error(f"✗ Missing attributes: {missing}")
            return False
        
        logger.info("✓ All package attributes accessible")
        return True
    except Exception as e:
        logger.error(f"✗ Package structure test failed: {e}")
        return False


def test_config_defaults():
    """
    Test 3: Verify default analytics configuration.
    
    Educational Note:
        Config test validates defaults provide reasonable starting
        values for all parameters without requiring user input.
    """
    logger.info("\nTest 3: Testing default configuration...")
    
    try:
        from src.services.analytics import DEFAULT_ANALYTICS_PARAMS
        
        required_keys = [
            "min_data_points_for_trend",
            "low_sleep_threshold_minutes",
            "low_feedback_threshold",
            "consistency_stdev_scale",
            "consistency_score_threshold",
            "negative_trend_threshold",
        ]
        
        missing = [key for key in required_keys if key not in DEFAULT_ANALYTICS_PARAMS]
        
        if missing:
            logger.error(f"✗ Missing config keys: {missing}")
            return False
        
        logger.info(f"  ✓ All config keys present: {len(required_keys)}")
        logger.info(f"  ✓ Min data points: {DEFAULT_ANALYTICS_PARAMS['min_data_points_for_trend']}")
        logger.info(f"  ✓ Low sleep threshold: {DEFAULT_ANALYTICS_PARAMS['low_sleep_threshold_minutes']}min")
        logger.info("✓ Default configuration complete")
        return True
    except Exception as e:
        logger.error(f"✗ Config defaults test failed: {e}")
        return False


def test_historical_sleep_data():
    """
    Test 4: Verify HistoricalSleepData dataclass creation.
    
    Educational Note:
        Dataclass test validates data structure works correctly
        with optional fields and type hints.
    """
    logger.info("\nTest 4: Testing HistoricalSleepData...")
    
    try:
        from src.services.analytics import HistoricalSleepData
        
        target = date.today()
        data = HistoricalSleepData(
            target_date=target,
            actual_sleep_duration_minutes=450.0,
            sleep_quality_score=85.0,
            mid_sleep_hour_local=4.5,
        )
        
        assert data.target_date == target
        assert data.actual_sleep_duration_minutes == 450.0
        assert data.sleep_quality_score == 85.0
        assert data.mid_sleep_hour_local == 4.5
        
        logger.info("  ✓ All fields set correctly")
        
        minimal = HistoricalSleepData(target_date=target)
        assert minimal.actual_sleep_duration_minutes is None
        
        logger.info("  ✓ Optional fields default to None")
        logger.info("✓ HistoricalSleepData creation works")
        return True
    except Exception as e:
        logger.error(f"✗ HistoricalSleepData test failed: {e}")
        return False


def test_trend_analysis_result():
    """
    Test 5: Verify TrendAnalysisResult dataclass creation.
    
    Educational Note:
        Frozen dataclass test validates immutability and that
        default factory for lists/dicts works correctly.
    """
    logger.info("\nTest 5: Testing TrendAnalysisResult...")
    
    try:
        from src.services.analytics import TrendAnalysisResult
        
        user_id = uuid4()
        start = date.today() - timedelta(days=7)
        end = date.today()
        
        result = TrendAnalysisResult(
            user_id=user_id,
            analysis_period_start_date=start,
            analysis_period_end_date=end,
        )
        
        assert result.user_id == user_id
        assert result.analysis_period_start_date == start
        assert result.analysis_period_end_date == end
        assert result.insights == []
        assert result.recommendations == {}
        
        logger.info("  ✓ Required fields set")
        logger.info("  ✓ Lists/dicts initialized as empty")
        logger.info("✓ TrendAnalysisResult creation works")
        return True
    except Exception as e:
        logger.error(f"✗ TrendAnalysisResult test failed: {e}")
        return False


def test_service_initialization():
    """
    Test 6: Verify AnalyticsService initializes correctly.
    
    Educational Note:
        Service initialization test validates config processing
        and database connection handling work properly.
    """
    logger.info("\nTest 6: Testing AnalyticsService initialization...")
    
    try:
        from src.services.analytics import AnalyticsService
        
        service = AnalyticsService()
        assert service._analytics_params is not None
        assert service._db_client is None
        
        logger.info("  ✓ Default initialization without DB")
        
        custom_service = AnalyticsService(config={
            "analytics_params": {
                "min_data_points_for_trend": 3,
                "low_sleep_threshold_minutes": 400,
            },
            "db_uri": "postgresql://test"
        })
        
        assert custom_service._analytics_params["min_data_points_for_trend"] == 3
        assert custom_service._analytics_params["low_sleep_threshold_minutes"] == 400
        assert custom_service._db_client is not None
        
        logger.info("  ✓ Custom config applied")
        logger.info("  ✓ DB client initialized with URI")
        logger.info("✓ Service initialization works")
        return True
    except Exception as e:
        logger.error(f"✗ Service initialization failed: {e}")
        return False


async def test_analyze_trends_no_data():
    """
    Test 7: Verify analyze_trends with no historical data.
    
    Educational Note:
        Empty data test validates graceful handling when no
        history exists for user (new accounts, data loss).
    """
    logger.info("\nTest 7: Testing analyze_trends with no data...")
    
    try:
        from src.services.analytics import AnalyticsService
        
        service = AnalyticsService(config={"db_uri": "test://fake"})
        
        user_id = uuid4()
        result = await service.analyze_trends(user_id, period_days=7)
        
        assert result is not None
        assert result.user_id == user_id
        assert len(result.insights) == 1
        assert "No historical data" in result.insights[0]
        
        logger.info("  ✓ Returns TrendAnalysisResult")
        logger.info("  ✓ Contains no-data insight")
        logger.info("✓ No-data handling works")
        return True
    except Exception as e:
        logger.error(f"✗ No-data test failed: {e}")
        return False


async def test_analyze_trends_with_mock():
    """
    Test 8: Verify analyze_trends with mock data generation.
    
    Educational Note:
        Mock data test validates full pipeline (fetch → calculate →
        correlate → insights) works end-to-end.
    """
    logger.info("\nTest 8: Testing analyze_trends with mock data...")
    
    try:
        from src.services.analytics import AnalyticsService
        
        service = AnalyticsService(config={
            "analytics_params": {
                "min_data_points_for_trend": 3,
            }
        })
        
        user_id = uuid4()
        result = await service.analyze_trends(user_id, period_days=14)
        
        assert result is not None
        assert result.user_id == user_id
        assert result.avg_sleep_duration_minutes is not None
        assert result.avg_feedback_rating is not None
        assert result.avg_scheduled_task_minutes is not None
        
        logger.info(f"  ✓ Sleep duration: {result.avg_sleep_duration_minutes:.1f}min")
        logger.info(f"  ✓ Feedback rating: {result.avg_feedback_rating:.1f}/5")
        logger.info(f"  ✓ Insights generated: {len(result.insights)}")
        logger.info("✓ Mock data analysis works")
        return True
    except Exception as e:
        logger.error(f"✗ Mock data test failed: {e}")
        return False


def run_all_tests():
    """
    Runs all analytics package integration tests.
    
    Educational Note:
        Test runner aggregates results for quick validation
        after refactoring complex analytics logic.
    """
    import asyncio
    
    logger.info("\n" + "="*60)
    logger.info("PHASE 9: ANALYTICS PACKAGE INTEGRATION TESTS")
    logger.info("="*60 + "\n")
    
    tests = [
        ("Imports", test_imports),
        ("Package Structure", test_package_structure),
        ("Config Defaults", test_config_defaults),
        ("HistoricalSleepData", test_historical_sleep_data),
        ("TrendAnalysisResult", test_trend_analysis_result),
        ("Service Initialization", test_service_initialization),
        ("Analyze Trends (No Data)", lambda: asyncio.run(test_analyze_trends_no_data())),
        ("Analyze Trends (Mock Data)", lambda: asyncio.run(test_analyze_trends_with_mock())),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed))
        except Exception as e:
            logger.error(f"Test '{name}' crashed: {e}")
            results.append((name, False))
    
    logger.info("\n" + "="*60)
    logger.info("TEST RESULTS SUMMARY")
    logger.info("="*60)
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        logger.info(f"  {status}: {name}")
    
    logger.info("-"*60)
    logger.info(f"  TOTAL: {passed_count}/{total_count} tests passed")
    logger.info("="*60 + "\n")
    
    if passed_count == total_count:
        logger.info("🎉 ALL TESTS PASSED! Refactoring successful.")
        return True
    else:
        logger.error(f"❌ {total_count - passed_count} test(s) failed. Review needed.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
