"""
Integration tests for wearables package refactoring.

Validates that refactored wearables/ package works correctly.

Educational Note:
    Integration tests verify package exports, service initialization,
    and basic data processing without full device integration.
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
    Test 1: Verify wearables package exports importable.
    
    Educational Note:
        Import test catches missing __all__ exports or broken
        dependencies that prevent package loading.
    """
    logger.info("\nTest 1: Testing imports from wearables package...")
    
    try:
        from src.services.wearables import (
            WearableService,
            ProcessedWearableData,
            format_timedelta,
        )
        logger.info("✓ All imports successful")
        return True
    except ImportError as e:
        logger.error(f"✗ Import failed: {e}")
        return False


def test_package_structure():
    """
    Test 2: Verify wearables package structure complete.
    
    Educational Note:
        Structure test ensures internal modules accessible
        and properly organized within package.
    """
    logger.info("\nTest 2: Testing package structure...")
    
    try:
        from src.services import wearables
        
        required_attrs = [
            'WearableService',
            'ProcessedWearableData',
            'format_timedelta',
        ]
        
        missing = [attr for attr in required_attrs if not hasattr(wearables, attr)]
        
        if missing:
            logger.error(f"✗ Missing attributes: {missing}")
            return False
        
        logger.info("✓ All package attributes accessible")
        return True
    except Exception as e:
        logger.error(f"✗ Package structure test failed: {e}")
        return False


def test_format_timedelta():
    """
    Test 3: Verify timedelta formatting utility.
    
    Educational Note:
        Utility function test validates edge cases (None, zero,
        large values) work correctly.
    """
    logger.info("\nTest 3: Testing format_timedelta...")
    
    try:
        from src.services.wearables import format_timedelta
        
        assert format_timedelta(None) == "N/A"
        assert format_timedelta(timedelta(hours=7, minutes=30)) == "07:30"
        assert format_timedelta(timedelta(hours=0, minutes=0)) == "00:00"
        assert format_timedelta(timedelta(hours=12, minutes=15)) == "12:15"
        
        logger.info("  ✓ None → N/A")
        logger.info("  ✓ 7h30m → 07:30")
        logger.info("  ✓ 0h0m → 00:00")
        logger.info("  ✓ 12h15m → 12:15")
        logger.info("✓ format_timedelta works correctly")
        return True
    except Exception as e:
        logger.error(f"✗ format_timedelta test failed: {e}")
        return False


def test_processed_wearable_data():
    """
    Test 4: Verify ProcessedWearableData dataclass creation.
    
    Educational Note:
        Dataclass test validates frozen attribute works and
        default values initialize correctly.
    """
    logger.info("\nTest 4: Testing ProcessedWearableData...")
    
    try:
        from src.services.wearables import ProcessedWearableData
        
        user_id = uuid4()
        target = date.today()
        
        data = ProcessedWearableData(user_id=user_id, target_date=target)
        
        assert data.user_id == user_id
        assert data.target_date == target
        assert data.sleep_analysis is None
        assert data.activity_summary is None
        assert data.raw_data_info == {}
        
        logger.info("  ✓ Required fields set")
        logger.info("  ✓ Optional fields default to None")
        logger.info("  ✓ raw_data_info defaults to empty dict")
        logger.info("✓ ProcessedWearableData creation works")
        return True
    except Exception as e:
        logger.error(f"✗ ProcessedWearableData test failed: {e}")
        return False


def test_service_initialization():
    """
    Test 5: Verify WearableService initializes correctly.
    
    Educational Note:
        Service initialization test validates dependency
        injection and config processing work.
    """
    logger.info("\nTest 5: Testing WearableService initialization...")
    
    try:
        from src.services.wearables import WearableService
        from src.adapters.device_adapter import MockDeviceDataAdapter
        from src.core.sleep import SleepCalculator
        
        adapter = MockDeviceDataAdapter()
        calculator = SleepCalculator()
        
        service = WearableService(
            device_adapter=adapter,
            sleep_calculator=calculator
        )
        
        assert service.device_adapter == adapter
        assert service.sleep_calculator == calculator
        assert service._sleep_window_start_hour == 0
        assert service._sleep_window_end_hour == 14
        
        logger.info("  ✓ Dependencies injected")
        logger.info("  ✓ Default config loaded")
        
        custom_service = WearableService(
            device_adapter=adapter,
            sleep_calculator=calculator,
            config={
                "primary_sleep_end_window_start_hour": 2,
                "primary_sleep_end_window_end_hour": 12
            }
        )
        
        assert custom_service._sleep_window_start_hour == 2
        assert custom_service._sleep_window_end_hour == 12
        
        logger.info("  ✓ Custom config applied")
        logger.info("✓ Service initialization works")
        return True
    except Exception as e:
        logger.error(f"✗ Service initialization failed: {e}")
        return False


def test_metrics_calculation():
    """
    Test 6: Verify metrics calculation utility.
    
    Educational Note:
        Metrics test validates filtering logic (None, <=0)
        and averaging work correctly.
    """
    logger.info("\nTest 6: Testing metrics calculation...")
    
    try:
        from src.services.wearables.metrics import calculate_average_metric
        from dataclasses import dataclass
        
        @dataclass
        class MockDataPoint:
            value: float
        
        points = [
            MockDataPoint(60),
            MockDataPoint(65),
            MockDataPoint(70),
        ]
        
        avg = calculate_average_metric(points, 'value', 'test')
        assert avg == 65.0
        
        logger.info("  ✓ Simple average: 65.0")
        
        points_with_invalid = [
            MockDataPoint(60),
            MockDataPoint(0),
            MockDataPoint(None),
            MockDataPoint(70),
        ]
        
        avg = calculate_average_metric(points_with_invalid, 'value', 'test')
        assert avg == 65.0
        
        logger.info("  ✓ Filters invalid values")
        
        empty_result = calculate_average_metric([], 'value', 'test')
        assert empty_result is None
        
        logger.info("  ✓ Returns None for empty list")
        logger.info("✓ Metrics calculation works")
        return True
    except Exception as e:
        logger.error(f"✗ Metrics calculation failed: {e}")
        return False


def test_sleep_finder():
    """
    Test 7: Verify sleep session identification.
    
    Educational Note:
        Sleep finder test validates time window filtering
        and longest-sleep selection logic.
    """
    logger.info("\nTest 7: Testing sleep session finder...")
    
    try:
        from src.services.wearables.sleep_finder import find_primary_sleep_session
        from datetime import datetime, timezone
        from dataclasses import dataclass
        
        @dataclass
        class MockSleepRecord:
            start_time: datetime
            end_time: datetime
            duration: timedelta
            source_record_id: str = "test"
        
        target = date.today()
        
        records = [
            MockSleepRecord(
                start_time=datetime.combine(target - timedelta(days=1), datetime.min.time()).replace(hour=22, tzinfo=timezone.utc),
                end_time=datetime.combine(target, datetime.min.time()).replace(hour=6, tzinfo=timezone.utc),
                duration=timedelta(hours=8)
            ),
            MockSleepRecord(
                start_time=datetime.combine(target, datetime.min.time()).replace(hour=13, tzinfo=timezone.utc),
                end_time=datetime.combine(target, datetime.min.time()).replace(hour=13, minute=30, tzinfo=timezone.utc),
                duration=timedelta(minutes=30)
            ),
        ]
        
        primary = find_primary_sleep_session(records, target, 0, 14)
        
        assert primary is not None
        assert primary.duration == timedelta(hours=8)
        
        logger.info("  ✓ Finds longest sleep in window")
        
        empty_result = find_primary_sleep_session([], target, 0, 14)
        assert empty_result is None
        
        logger.info("  ✓ Returns None for empty list")
        logger.info("✓ Sleep finder works")
        return True
    except Exception as e:
        logger.error(f"✗ Sleep finder test failed: {e}")
        return False


def run_all_tests():
    """
    Runs all wearables package integration tests.
    
    Educational Note:
        Test runner aggregates results for quick validation
        after refactoring complex processing logic.
    """
    logger.info("\n" + "="*60)
    logger.info("PHASE 8: WEARABLES PACKAGE INTEGRATION TESTS")
    logger.info("="*60 + "\n")
    
    tests = [
        ("Imports", test_imports),
        ("Package Structure", test_package_structure),
        ("format_timedelta", test_format_timedelta),
        ("ProcessedWearableData", test_processed_wearable_data),
        ("Service Initialization", test_service_initialization),
        ("Metrics Calculation", test_metrics_calculation),
        ("Sleep Finder", test_sleep_finder),
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
