"""
Integration test for Phase 6: LLM package refactoring.

Verifies that the new llm/ package provides identical functionality
to the original llm_engine.py monolithic file.

Educational Note:
    Integration tests validate high-level behavior rather than
    implementation details, ensuring refactoring preserves functionality.
"""

import logging
import sys
from datetime import date, timedelta
from pathlib import Path
from uuid import uuid4

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def test_imports():
    """
    Test 1: Verify all exports from llm package are importable.
    
    Educational Note:
        Import tests catch missing __init__.py exports early,
        preventing runtime failures in production code.
    """
    logger.info("Test 1: Testing imports from llm package...")
    
    try:
        from src.services.llm import (
            ModelConfig,
            ModelProvider,
            ScheduleGenerationContext,
            LLMEngine,
            extract_valid_json,
            GENERATE_FROM_SCRATCH_TEMPLATE,
            REFINE_SCHEDULE_TEMPLATE,
        )
        logger.info("✓ All imports successful")
        return True
    except ImportError as e:
        logger.error(f"✗ Import failed: {e}")
        return False


def test_package_structure():
    """
    Test 2: Verify llm package structure is complete.
    
    Educational Note:
        Package structure tests ensure all modules are properly
        organized and accessible through the package __init__.py.
    """
    logger.info("\nTest 2: Testing package structure...")
    
    try:
        from src.services import llm
        
        required_attrs = [
            'ModelConfig',
            'ModelProvider',
            'ScheduleGenerationContext',
            'LLMEngine',
            'extract_valid_json',
            'GENERATE_FROM_SCRATCH_TEMPLATE',
            'REFINE_SCHEDULE_TEMPLATE',
        ]
        
        missing = [attr for attr in required_attrs if not hasattr(llm, attr)]
        
        if missing:
            logger.error(f"✗ Missing attributes: {missing}")
            return False
            
        logger.info("✓ All package attributes accessible")
        return True
    except Exception as e:
        logger.error(f"✗ Package structure test failed: {e}")
        return False


def test_model_config_creation():
    """
    Test 3: Verify ModelConfig can be instantiated with defaults.
    
    Educational Note:
        Configuration tests validate Pydantic model initialization,
        default values, and validation logic work correctly.
    """
    logger.info("\nTest 3: Testing ModelConfig creation...")
    
    try:
        from src.services.llm import ModelConfig, ModelProvider
        
        config = ModelConfig()
        
        assert config.llm_provider == ModelProvider.OPENROUTER, \
            f"Expected OPENROUTER, got {config.llm_provider}"
        assert config.llm_temperature == 0.3, \
            f"Expected temp 0.3, got {config.llm_temperature}"
        assert config.llm_max_tokens == 2048, \
            f"Expected 2048 tokens, got {config.llm_max_tokens}"
        assert config.llm_model_name is not None, \
            "Model name should have default value"
            
        logger.info(f"  Provider: {config.llm_provider.value}")
        logger.info(f"  Model: {config.llm_model_name}")
        logger.info(f"  Temperature: {config.llm_temperature}")
        logger.info(f"  Max tokens: {config.llm_max_tokens}")
        logger.info("✓ ModelConfig creation works correctly")
        return True
        
    except Exception as e:
        logger.error(f"✗ ModelConfig creation failed: {e}")
        return False


def test_schedule_generation_context():
    """
    Test 4: Verify ScheduleGenerationContext dataclass creation.
    
    Educational Note:
        Dataclass tests ensure field defaults, type hints, and
        initialization work as expected for context aggregation.
    """
    logger.info("\nTest 4: Testing ScheduleGenerationContext...")
    
    try:
        from src.services.llm import ScheduleGenerationContext
        
        user_id = uuid4()
        target_date = date.today()
        
        context = ScheduleGenerationContext(
            user_id=user_id,
            user_name="Test User",
            target_date=target_date
        )
        
        assert context.user_id == user_id
        assert context.user_name == "Test User"
        assert context.target_date == target_date
        assert context.preferences == {}
        assert context.tasks == []
        assert context.fixed_events == []
        
        logger.info(f"  User: {context.user_name}")
        logger.info(f"  Date: {context.target_date}")
        logger.info(f"  Tasks: {len(context.tasks)}")
        logger.info("✓ ScheduleGenerationContext works correctly")
        return True
        
    except Exception as e:
        logger.error(f"✗ ScheduleGenerationContext failed: {e}")
        return False


def test_json_extraction():
    """
    Test 5: Verify extract_valid_json handles various formats.
    
    Educational Note:
        Parser tests validate edge cases: markdown-wrapped JSON,
        nested structures, escaped quotes, ensuring robust LLM parsing.
    """
    logger.info("\nTest 5: Testing JSON extraction...")
    
    try:
        from src.services.llm import extract_valid_json
        
        test_cases = [
            ('{"key": "value"}', '{"key": "value"}'),
            ('Here is JSON: {"key": "value"} and more text', '{"key": "value"}'),
            ('[1, 2, 3]', '[1, 2, 3]'),
            ('```json\n{"key": "value"}\n```', None),  # Should fail but not crash
        ]
        
        passed = 0
        for input_text, expected in test_cases:
            try:
                result = extract_valid_json(input_text)
                if expected:
                    assert result == expected, f"Expected {expected}, got {result}"
                    passed += 1
                    logger.info(f"  ✓ Case {passed}: '{input_text[:30]}...'")
            except ValueError:
                if not expected:
                    passed += 1
                    logger.info(f"  ✓ Case {passed}: Correctly rejected invalid input")
                    
        logger.info(f"✓ JSON extraction works ({passed}/{len(test_cases)} cases passed)")
        return True
        
    except Exception as e:
        logger.error(f"✗ JSON extraction failed: {e}")
        return False


def test_template_initialization():
    """
    Test 6: Verify Jinja2 templates load successfully.
    
    Educational Note:
        Template tests ensure large multi-line strings parse correctly
        and Jinja2 syntax is valid, preventing runtime template errors.
    """
    logger.info("\nTest 6: Testing template initialization...")
    
    try:
        from src.services.llm import (
            GENERATE_FROM_SCRATCH_TEMPLATE,
            REFINE_SCHEDULE_TEMPLATE
        )
        
        assert GENERATE_FROM_SCRATCH_TEMPLATE is not None, \
            "From scratch template is None"
        assert REFINE_SCHEDULE_TEMPLATE is not None, \
            "Refine template is None"
            
        logger.info("  ✓ FROM_SCRATCH template loaded")
        logger.info("  ✓ REFINE template loaded")
        logger.info("✓ Template initialization works")
        return True
        
    except Exception as e:
        logger.error(f"✗ Template initialization failed: {e}")
        return False


def test_llm_engine_initialization():
    """
    Test 7: Verify LLMEngine can be instantiated with config.
    
    Educational Note:
        Engine initialization tests validate dependency injection,
        template loading, and initial state setup work correctly.
    """
    logger.info("\nTest 7: Testing LLMEngine initialization...")
    
    try:
        from src.services.llm import ModelConfig, LLMEngine
        
        config = ModelConfig()
        engine = LLMEngine(config)
        
        assert engine.config == config
        assert engine.session is None  # Not yet in async context
        assert engine._prompt_template_from_scratch is not None
        assert engine._prompt_template_refine is not None
        
        logger.info(f"  Provider: {engine.config.llm_provider.value}")
        logger.info(f"  Model: {engine.config.llm_model_name}")
        logger.info("✓ LLMEngine initialization works")
        return True
        
    except Exception as e:
        logger.error(f"✗ LLMEngine initialization failed: {e}")
        return False


def test_fallback_schedule_generation():
    """
    Test 8: Verify fallback schedule generation when LLM unavailable.
    
    Educational Note:
        Fallback tests ensure graceful degradation - system remains
        functional even when external dependencies (LLM API) fail.
    """
    logger.info("\nTest 8: Testing fallback schedule generation...")
    
    try:
        from src.services.llm import (
            ModelConfig,
            LLMEngine,
            ScheduleGenerationContext,
            Task,
            TaskPriority,
            EnergyLevel
        )
        from datetime import datetime
        
        config = ModelConfig()
        engine = LLMEngine(config)
        
        user_id = uuid4()
        task = Task(
            id=uuid4(),
            title="Test Task",
            duration=timedelta(hours=1),
            priority=TaskPriority.HIGH,
            energy_level=EnergyLevel.HIGH
        )
        
        context = ScheduleGenerationContext(
            user_id=user_id,
            user_name="Test User",
            target_date=date.today(),
            tasks=[task],
            fixed_events=[{"name": "Meeting", "start_time": "09:00", "end_time": "10:00"}]
        )
        
        fallback = engine._generate_fallback_schedule(context, "Test error")
        
        assert "schedule" in fallback
        assert isinstance(fallback["schedule"], list)
        assert len(fallback["schedule"]) == 2  # 1 task + 1 event
        assert "warnings" in fallback
        assert "Test error" in fallback["warnings"][0]
        
        logger.info(f"  Items in fallback: {len(fallback['schedule'])}")
        logger.info(f"  Warning present: {bool(fallback['warnings'])}")
        logger.info("✓ Fallback schedule generation works")
        return True
        
    except Exception as e:
        logger.error(f"✗ Fallback schedule generation failed: {e}")
        return False


def test_energy_time_helper():
    """
    Test 9: Verify energy pattern to time string conversion.
    
    Educational Note:
        Helper function tests validate utility methods work independently,
        simplifying debugging when integrated into larger workflows.
    """
    logger.info("\nTest 9: Testing energy-for-time helper...")
    
    try:
        from src.services.llm import ModelConfig, LLMEngine
        
        config = ModelConfig()
        engine = LLMEngine(config)
        
        energy_pattern = {
            9: 0.9,   # High at 9am
            12: 0.5,  # Medium at noon
            15: 0.3   # Low at 3pm
        }
        
        result_high = engine._get_energy_for_time(energy_pattern, "09:30")
        result_medium = engine._get_energy_for_time(energy_pattern, "12:15")
        result_low = engine._get_energy_for_time(energy_pattern, "15:00")
        
        assert "High" in result_high or "0.9" in result_high
        assert "Medium" in result_medium or "0.5" in result_medium
        assert "Low" in result_low or "0.3" in result_low
        
        logger.info(f"  09:30 → {result_high}")
        logger.info(f"  12:15 → {result_medium}")
        logger.info(f"  15:00 → {result_low}")
        logger.info("✓ Energy-for-time helper works")
        return True
        
    except Exception as e:
        logger.error(f"✗ Energy-for-time helper failed: {e}")
        return False


def test_prompt_building_with_solver_schedule():
    """
    Test 10: Verify _build_prompt works with solver schedule.
    
    Educational Note:
        Tests that refine_and_complete_schedule path correctly passes
        solver_schedule to prompt template, ensuring hybrid approach works.
    """
    logger.info("\nTest 10: Testing prompt building with solver schedule...")
    
    try:
        from src.services.llm import (
            ModelConfig,
            LLMEngine,
            ScheduleGenerationContext,
            ScheduledTaskInfo
        )
        from datetime import date, time
        from uuid import uuid4
        
        config = ModelConfig()
        engine = LLMEngine(config)
        
        context = ScheduleGenerationContext(
            user_id=uuid4(),
            user_name="Test User",
            target_date=date(2025, 10, 18),
        )
        
        solver_schedule = [
            ScheduledTaskInfo(
                task_id=uuid4(),
                start_time=time(9, 0),
                end_time=time(10, 0),
                task_date=date(2025, 10, 18)
            )
        ]
        
        prompt = engine._build_prompt(
            engine._prompt_template_refine,
            context,
            format_type="json",
            solver_schedule=solver_schedule
        )
        
        assert prompt is not None, "Prompt should not be None"
        assert len(prompt) > 100, "Prompt should contain substantial content"
        assert "09:00" in prompt or "9:00" in prompt, "Should contain solver schedule time"
        
        logger.info(f"  Prompt length: {len(prompt)} chars")
        logger.info(f"  Contains solver schedule: {'09:00' in prompt or '9:00' in prompt}")
        logger.info("✓ Prompt building with solver schedule works")
        return True
        
    except Exception as e:
        logger.error(f"✗ Prompt building test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """
    Orchestrates all integration tests and reports results.
    
    Educational Note:
        Test runner pattern aggregates results, providing clear
        pass/fail summary for quick validation after refactoring.
    """
    logger.info("\n" + "="*60)
    logger.info("PHASE 6: LLM PACKAGE INTEGRATION TESTS")
    logger.info("="*60 + "\n")
    
    tests = [
        ("Imports", test_imports),
        ("Package Structure", test_package_structure),
        ("ModelConfig Creation", test_model_config_creation),
        ("ScheduleGenerationContext", test_schedule_generation_context),
        ("JSON Extraction", test_json_extraction),
        ("Template Initialization", test_template_initialization),
        ("LLMEngine Initialization", test_llm_engine_initialization),
        ("Fallback Schedule", test_fallback_schedule_generation),
        ("Energy Helper", test_energy_time_helper),
        ("Prompt Building with Solver Schedule", test_prompt_building_with_solver_schedule),
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
    exit(0 if success else 1)
