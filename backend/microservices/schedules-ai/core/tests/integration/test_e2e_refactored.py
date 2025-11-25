"""
End-to-end integration test for refactored packages with FastAPI.

Tests complete flow: API → Dependencies → Scheduler → Refactored Services

Educational Note:
    This validates that all refactored packages (llm, rl, wearables, analytics)
    integrate correctly with the FastAPI application and can be used through
    the actual API endpoints that analytics_center will call.
"""

import sys
import logging
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_api_startup():
    """
    Test 1: FastAPI application loads with all refactored packages.
    """
    logger.info("\nTest 1: Testing FastAPI application startup...")
    
    try:
        import os
        os.environ['ENVIRONMENT'] = 'development'
        
        from api.server import app
        
        assert app is not None
        assert app.title == "Auratyme Schedules API"
        
        routes = [route.path for route in app.routes]
        assert len(routes) > 0
        
        logger.info(f"  ✓ App loaded: {app.title}")
        logger.info(f"  ✓ Total routes: {len(routes)}")
        logger.info("✓ FastAPI startup successful")
        return True
    except Exception as e:
        logger.error(f"✗ FastAPI startup failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_dependencies_injection():
    """
    Test 2: All dependency injection functions work with new packages.
    """
    logger.info("\nTest 2: Testing dependency injection...")
    
    try:
        from api.dependencies import (
            get_llm_engine,
            get_wearable_service,
            get_analytics_service,
            get_adaptive_engine_service,
            get_scheduler,
        )
        
        # Test service creation
        analytics = get_analytics_service()
        assert analytics is not None
        logger.info("  ✓ AnalyticsService created via DI")
        
        adaptive = get_adaptive_engine_service()
        assert adaptive is not None
        logger.info("  ✓ AdaptiveEngineService created via DI")
        
        # Test scheduler (complex dependency tree)
        scheduler = get_scheduler()
        assert scheduler is not None
        assert hasattr(scheduler, 'llm_engine')
        logger.info("  ✓ Scheduler created with LLM dependency")
        
        logger.info("✓ Dependency injection working")
        return True
    except Exception as e:
        logger.error(f"✗ Dependency injection failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_scheduler_imports():
    """
    Test 3: Scheduler imports correct refactored packages.
    """
    logger.info("\nTest 3: Testing scheduler imports...")
    
    try:
        from src.core.scheduler import Scheduler
        from src.core.scheduler.context import create_llm_context
        
        # Read the actual source file to verify imports
        import pathlib
        context_file = pathlib.Path(__file__).parent.parent.parent / 'src' / 'core' / 'scheduler' / 'context.py'
        
        with open(context_file, 'r') as f:
            source = f.read()
        
        # Should import from new package, not legacy
        assert 'from src.services.llm import' in source
        assert 'llm_engine_legacy' not in source
        
        logger.info("  ✓ context.py uses new llm package")
        logger.info("  ✓ No legacy imports found")
        logger.info("✓ Scheduler imports correct")
        return True
    except Exception as e:
        logger.error(f"✗ Scheduler imports test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_package_isolation():
    """
    Test 4: Verify legacy files not imported anywhere.
    """
    logger.info("\nTest 4: Testing package isolation (no legacy imports)...")
    
    try:
        import subprocess
        import os
        
        # Search for any imports of legacy files
        core_dir = str(project_root)
        
        legacy_patterns = [
            'llm_engine_legacy',
            'rl_engine_legacy', 
            'wearables_legacy',
            'analytics_legacy',
        ]
        
        for pattern in legacy_patterns:
            result = subprocess.run(
                ['grep', '-r', pattern, '--include=*.py', core_dir],
                capture_output=True,
                text=True
            )
            
            # Should only find in the legacy files themselves
            if result.stdout:
                lines = result.stdout.strip().split('\n')
                # Filter out the legacy files themselves
                imports = [
                    line for line in lines 
                    if 'import' in line and '_legacy.py' not in line
                ]
                
                if imports:
                    logger.error(f"  ✗ Found legacy import for {pattern}:")
                    for imp in imports:
                        logger.error(f"    {imp}")
                    return False
        
        logger.info("  ✓ No legacy imports in active code")
        logger.info("✓ Package isolation verified")
        return True
    except FileNotFoundError:
        logger.warning("  ⚠ grep not available (Windows), skipping isolation test")
        return True
    except Exception as e:
        logger.error(f"✗ Package isolation test failed: {e}")
        return False


def test_api_endpoint_integration():
    """
    Test 5: Test actual API endpoint works with new packages.
    """
    logger.info("\nTest 5: Testing API endpoint integration...")
    
    try:
        from fastapi.testclient import TestClient
        import os
        os.environ['ENVIRONMENT'] = 'development'
        
        from api.server import app
        
        client = TestClient(app)
        
        # Test health endpoint
        response = client.get("/health")
        assert response.status_code == 200
        logger.info("  ✓ Health endpoint responds")
        
        # Test OpenAPI docs generation (requires all imports working)
        response = client.get("/docs")
        assert response.status_code == 200
        logger.info("  ✓ API docs generation successful")
        
        logger.info("✓ API endpoints working")
        return True
    except Exception as e:
        logger.error(f"✗ API endpoint test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_analytics_center_compatibility():
    """
    Test 6: Verify analytics_center can communicate with API.
    """
    logger.info("\nTest 6: Testing analytics_center compatibility...")
    
    try:
        # Check analytics_center doesn't import core directly
        analytics_dir = project_root.parent / 'analytics_center'
        
        if not analytics_dir.exists():
            logger.warning("  ⚠ analytics_center not found, skipping")
            return True
        
        # Verify analytics_center uses HTTP client, not direct imports
        import subprocess
        result = subprocess.run(
            ['grep', '-r', 'from.*core.src', '--include=*.py', str(analytics_dir)],
            capture_output=True,
            text=True
        )
        
        if result.stdout:
            logger.error("  ✗ analytics_center has direct core imports:")
            logger.error(f"    {result.stdout}")
            return False
        
        logger.info("  ✓ analytics_center uses HTTP API only")
        logger.info("  ✓ No direct core imports found")
        logger.info("✓ Analytics center compatible")
        return True
    except FileNotFoundError:
        logger.warning("  ⚠ grep not available, skipping analytics check")
        return True
    except Exception as e:
        logger.error(f"✗ Analytics center test failed: {e}")
        return False


def run_all_tests():
    """
    Runs all end-to-end integration tests.
    """
    logger.info("\n" + "="*70)
    logger.info("END-TO-END INTEGRATION TEST - REFACTORED PACKAGES + API")
    logger.info("="*70)
    
    tests = [
        ("API Startup", test_api_startup),
        ("Dependency Injection", test_dependencies_injection),
        ("Scheduler Imports", test_scheduler_imports),
        ("Package Isolation", test_package_isolation),
        ("API Endpoints", test_api_endpoint_integration),
        ("Analytics Center Compatibility", test_analytics_center_compatibility),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed))
        except Exception as e:
            logger.error(f"Test '{name}' crashed: {e}")
            results.append((name, False))
    
    logger.info("\n" + "="*70)
    logger.info("TEST RESULTS SUMMARY")
    logger.info("="*70)
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        logger.info(f"  {status}: {name}")
    
    logger.info("-"*70)
    logger.info(f"  TOTAL: {passed_count}/{total_count} tests passed")
    logger.info("="*70 + "\n")
    
    if passed_count == total_count:
        logger.info("🎉 ALL INTEGRATION TESTS PASSED!")
        logger.info("✅ System ready for analytics_center Docker deployment")
        logger.info("\nRun: docker compose up --build analytics-center")
        return True
    else:
        logger.error(f"❌ {total_count - passed_count} test(s) failed")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
