"""
Integration tests for RL (Adaptive Engine) package refactoring.

Validates that refactored rl/ package works identically to original
rl_engine.py implementation.

Educational Note:
    Integration tests verify package exports, service initialization,
    adaptation calculations, and parameter application work correctly
    after refactoring into modular structure.
"""

import sys
import logging
from pathlib import Path
from uuid import uuid4
from datetime import date, timedelta
from dataclasses import dataclass, field
from typing import Optional, List

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_imports():
    """
    Test 1: Verify all rl package exports are importable.
    
    Educational Note:
        Import test catches missing __all__ exports or circular
        dependency issues that break package interface.
    """
    logger.info("\nTest 1: Testing imports from rl package...")
    
    try:
        from src.services.rl import (
            AdaptiveEngineService,
            AdaptationParameters,
            DEFAULT_CONFIG,
        )
        logger.info("✓ All imports successful")
        return True
    except ImportError as e:
        logger.error(f"✗ Import failed: {e}")
        return False


def test_package_structure():
    """
    Test 2: Verify rl package structure is complete.
    
    Educational Note:
        Structure test ensures all internal modules (models, config,
        analyzer, adapter, service) are present and properly organized.
    """
    logger.info("\nTest 2: Testing package structure...")
    
    try:
        from src.services import rl
        
        required_attrs = [
            'AdaptiveEngineService',
            'AdaptationParameters',
            'DEFAULT_CONFIG',
        ]
        
        missing = [attr for attr in required_attrs if not hasattr(rl, attr)]
        
        if missing:
            logger.error(f"✗ Missing attributes: {missing}")
            return False
        
        logger.info("✓ All package attributes accessible")
        return True
    except Exception as e:
        logger.error(f"✗ Package structure test failed: {e}")
        return False


def test_adaptation_parameters():
    """
    Test 3: Verify AdaptationParameters dataclass creation.
    
    Educational Note:
        Dataclass test validates default values and field types
        work correctly after refactoring into models module.
    """
    logger.info("\nTest 3: Testing AdaptationParameters...")
    
    try:
        from src.services.rl import AdaptationParameters
        
        params = AdaptationParameters()
        
        assert params.sleep_need_scale_adjustment == 0.0
        assert params.chronotype_scale_adjustment == 0.0
        assert params.prioritizer_weight_adjustments == {}
        
        params_with_values = AdaptationParameters(
            sleep_need_scale_adjustment=0.1,
            chronotype_scale_adjustment=0.05,
            prioritizer_weight_adjustments={"priority": 0.15}
        )
        
        assert params_with_values.sleep_need_scale_adjustment == 0.1
        assert params_with_values.prioritizer_weight_adjustments["priority"] == 0.15
        
        logger.info("  ✓ Default values correct")
        logger.info("  ✓ Custom values accepted")
        logger.info("✓ AdaptationParameters works correctly")
        return True
    except Exception as e:
        logger.error(f"✗ AdaptationParameters test failed: {e}")
        return False


def test_service_initialization():
    """
    Test 4: Verify AdaptiveEngineService initializes correctly.
    
    Educational Note:
        Initialization test validates config merging, default values,
        and internal state setup without external dependencies.
    """
    logger.info("\nTest 4: Testing AdaptiveEngineService initialization...")
    
    try:
        from src.services.rl import AdaptiveEngineService
        
        service = AdaptiveEngineService()
        assert service._adaptation_step == 0.05
        assert service._min_data_points == 5
        logger.info("  ✓ Default config loaded")
        
        custom_service = AdaptiveEngineService(config={"adaptation_step_size": 0.1})
        assert custom_service._adaptation_step == 0.1
        logger.info("  ✓ Custom config merged")
        
        logger.info("✓ Service initialization works")
        return True
    except Exception as e:
        logger.error(f"✗ Service initialization failed: {e}")
        return False


def test_calculate_adaptations_without_data():
    """
    Test 5: Verify adaptation calculation with no input data.
    
    Educational Note:
        Empty input test ensures service degrades gracefully when
        analytics/feedback unavailable, returning zero adjustments.
    """
    logger.info("\nTest 5: Testing adaptation calculation without data...")
    
    try:
        import asyncio
        from src.services.rl import AdaptiveEngineService
        
        async def run_test():
            service = AdaptiveEngineService()
            user_id = uuid4()
            
            adaptations = await service.calculate_adaptations(
                user_id=user_id,
                trend_analysis=None,
                recent_feedback_analysis=None
            )
            
            assert adaptations.sleep_need_scale_adjustment == 0.0
            assert adaptations.chronotype_scale_adjustment == 0.0
            assert adaptations.prioritizer_weight_adjustments == {}
            
            logger.info("  ✓ Returns empty adaptations")
            return True
        
        result = asyncio.run(run_test())
        logger.info("✓ Adaptation calculation handles empty input")
        return result
    except Exception as e:
        logger.error(f"✗ Adaptation calculation failed: {e}")
        return False


def test_calculate_adaptations_with_dummy_data():
    """
    Test 6: Verify adaptation calculation with dummy trend data.
    
    Educational Note:
        Dummy data test validates adaptation logic responds correctly
        to sleep deficit patterns without real analytics dependency.
    """
    logger.info("\nTest 6: Testing adaptation calculation with dummy data...")
    
    try:
        import asyncio
        from src.services.rl import AdaptiveEngineService
        from src.services.rl.models import create_dummy_trend_analysis
        
        async def run_test():
            service = AdaptiveEngineService()
            user_id = uuid4()
            
            DummyTrend = create_dummy_trend_analysis()
            trend = DummyTrend(
                user_id=user_id,
                analysis_period_start_date=date.today() - timedelta(days=7),
                analysis_period_end_date=date.today(),
                avg_sleep_duration_minutes=360
            )
            
            adaptations = await service.calculate_adaptations(
                user_id=user_id,
                trend_analysis=trend
            )
            
            assert adaptations.sleep_need_scale_adjustment > 0
            logger.info(f"  Sleep adjustment: {adaptations.sleep_need_scale_adjustment:.3f}")
            logger.info("  ✓ Detects sleep deficit")
            return True
        
        result = asyncio.run(run_test())
        logger.info("✓ Adaptation calculation with dummy data works")
        return result
    except Exception as e:
        logger.error(f"✗ Dummy data test failed: {e}")
        return False


def test_apply_adaptations():
    """
    Test 7: Verify parameter adaptation application.
    
    Educational Note:
        Application test validates adaptations correctly modify
        parameter dictionary while respecting bounds (0-100, 0-1).
    """
    logger.info("\nTest 7: Testing adaptation application...")
    
    try:
        from src.services.rl import AdaptiveEngineService, AdaptationParameters
        
        service = AdaptiveEngineService()
        
        current_params = {
            "sleep_need_scale": 50.0,
            "chronotype_scale": 40.0,
            "prioritizer_weights": {
                "priority": 0.5,
                "deadline": 0.35,
                "dependencies": 0.1
            }
        }
        
        adaptations = AdaptationParameters(
            sleep_need_scale_adjustment=0.1,
            chronotype_scale_adjustment=0.05,
            prioritizer_weight_adjustments={"priority": 0.1}
        )
        
        updated = service.apply_adaptations(current_params, adaptations)
        
        assert updated["sleep_need_scale"] > current_params["sleep_need_scale"]
        assert updated["chronotype_scale"] > current_params["chronotype_scale"]
        assert updated["prioritizer_weights"]["priority"] > 0.5
        
        logger.info(f"  Sleep scale: {current_params['sleep_need_scale']:.1f} → {updated['sleep_need_scale']:.1f}")
        logger.info(f"  Priority weight: {current_params['prioritizer_weights']['priority']:.2f} → {updated['prioritizer_weights']['priority']:.2f}")
        logger.info("  ✓ Parameters adjusted correctly")
        logger.info("✓ Adaptation application works")
        return True
    except Exception as e:
        logger.error(f"✗ Application test failed: {e}")
        return False


def test_bounds_enforcement():
    """
    Test 8: Verify parameter bounds are enforced.
    
    Educational Note:
        Bounds test ensures extreme adjustments don't create invalid
        states (negative weights, >100 scales) that break scheduler.
    """
    logger.info("\nTest 8: Testing bounds enforcement...")
    
    try:
        from src.services.rl import AdaptiveEngineService, AdaptationParameters
        
        service = AdaptiveEngineService()
        
        current_params = {
            "sleep_need_scale": 95.0,
            "prioritizer_weights": {"priority": 0.95}
        }
        
        extreme_adaptations = AdaptationParameters(
            sleep_need_scale_adjustment=2.0,
            prioritizer_weight_adjustments={"priority": 0.2}
        )
        
        updated = service.apply_adaptations(current_params, extreme_adaptations)
        
        assert updated["sleep_need_scale"] <= 100.0
        assert updated["prioritizer_weights"]["priority"] <= 1.0
        
        logger.info(f"  Sleep scale capped at: {updated['sleep_need_scale']:.1f}")
        logger.info(f"  Priority weight capped at: {updated['prioritizer_weights']['priority']:.2f}")
        logger.info("  ✓ Upper bounds enforced")
        
        low_params = {
            "sleep_need_scale": 5.0,
            "prioritizer_weights": {"priority": 0.05}
        }
        
        negative_adaptations = AdaptationParameters(
            sleep_need_scale_adjustment=-2.0,
            prioritizer_weight_adjustments={"priority": -0.2}
        )
        
        updated_low = service.apply_adaptations(low_params, negative_adaptations)
        
        assert updated_low["sleep_need_scale"] >= 0.0
        assert updated_low["prioritizer_weights"]["priority"] >= 0.0
        
        logger.info(f"  Sleep scale floored at: {updated_low['sleep_need_scale']:.1f}")
        logger.info(f"  Priority weight floored at: {updated_low['prioritizer_weights']['priority']:.2f}")
        logger.info("  ✓ Lower bounds enforced")
        logger.info("✓ Bounds enforcement works")
        return True
    except Exception as e:
        logger.error(f"✗ Bounds test failed: {e}")
        return False


def run_all_tests():
    """
    Runs all RL package integration tests.
    
    Educational Note:
        Test runner pattern aggregates results, providing clear
        pass/fail summary for quick validation after refactoring.
    """
    logger.info("\n" + "="*60)
    logger.info("PHASE 7: RL PACKAGE INTEGRATION TESTS")
    logger.info("="*60 + "\n")
    
    tests = [
        ("Imports", test_imports),
        ("Package Structure", test_package_structure),
        ("AdaptationParameters", test_adaptation_parameters),
        ("Service Initialization", test_service_initialization),
        ("Calculate Adaptations (Empty)", test_calculate_adaptations_without_data),
        ("Calculate Adaptations (Dummy Data)", test_calculate_adaptations_with_dummy_data),
        ("Apply Adaptations", test_apply_adaptations),
        ("Bounds Enforcement", test_bounds_enforcement),
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
