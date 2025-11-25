"""
Test integration between simplified chronotype system and scheduler.

This test verifies that scheduler correctly uses the new ScheduleChronotypeContext
instead of the old ChronotypeProfile.
"""

from datetime import date
from uuid import uuid4

from src.core.scheduler.models import ScheduleInputData, ScheduleChronotypeContext
from src.core.scheduler.profile_prep import prepare_chronotype_context
from src.core.chronotype import ChronotypeAnalyzer, Chronotype


def test_scheduler_chronotype_integration():
    """
    Test that scheduler can create chronotype context from input data.
    
    Educational Note:
        Integration test verifies that refactored scheduler components
        work together correctly with simplified chronotype system.
    """
    print("\n🧪 TESTING SCHEDULER-CHRONOTYPE INTEGRATION")
    print("=" * 70)
    
    analyzer = ChronotypeAnalyzer()
    
    # Test 1: With MEQ score
    print("\n📋 TEST 1: Input with MEQ score")
    print("-" * 70)
    
    input_data = ScheduleInputData(
        user_id=uuid4(),
        target_date=date(2025, 11, 6),
        tasks=[],
        user_profile_data={"meq_score": 70}  # Early bird
    )
    
    context = prepare_chronotype_context(input_data, analyzer)
    
    assert isinstance(context, ScheduleChronotypeContext)
    assert context.chronotype == Chronotype.EARLY_BIRD
    assert context.prime_window.start.hour == 7
    assert context.prime_window.end.hour == 11
    assert context.source == "meq"
    
    print(f"✓ User ID: {context.user_id}")
    print(f"✓ Chronotype: {context.chronotype.value}")
    print(f"✓ Prime Window: {context.prime_window.start.strftime('%H:%M')}-{context.prime_window.end.strftime('%H:%M')}")
    print(f"✓ Duration: {context.prime_window.duration_hours()}h")
    print(f"✓ Source: {context.source}")
    
    # Test 2: With MEQ in preferences
    print("\n📋 TEST 2: Input with MEQ in preferences")
    print("-" * 70)
    
    input_data2 = ScheduleInputData(
        user_id=uuid4(),
        target_date=date(2025, 11, 6),
        tasks=[],
        preferences={"meq_score": 25}  # Night owl
    )
    
    context2 = prepare_chronotype_context(input_data2, analyzer)
    
    assert context2.chronotype == Chronotype.NIGHT_OWL
    assert context2.prime_window.start.hour == 17
    assert context2.prime_window.end.hour == 22
    
    print(f"✓ Chronotype: {context2.chronotype.value}")
    print(f"✓ Prime Window: {context2.prime_window.start.strftime('%H:%M')}-{context2.prime_window.end.strftime('%H:%M')}")
    print(f"✓ Duration: {context2.prime_window.duration_hours()}h")
    
    # Test 3: Without MEQ (default)
    print("\n📋 TEST 3: Input without MEQ (default UNKNOWN)")
    print("-" * 70)
    
    input_data3 = ScheduleInputData(
        user_id=uuid4(),
        target_date=date(2025, 11, 6),
        tasks=[]
    )
    
    context3 = prepare_chronotype_context(input_data3, analyzer)
    
    assert context3.chronotype == Chronotype.UNKNOWN
    assert context3.prime_window.start.hour == 10
    assert context3.prime_window.end.hour == 14
    assert context3.source == "default"
    
    print(f"✓ Chronotype: {context3.chronotype.value}")
    print(f"✓ Prime Window: {context3.prime_window.start.strftime('%H:%M')}-{context3.prime_window.end.strftime('%H:%M')}")
    print(f"✓ Duration: {context3.prime_window.duration_hours()}h")
    print(f"✓ Source: {context3.source}")
    
    print("\n" + "=" * 70)
    print("✅ ALL SCHEDULER-CHRONOTYPE INTEGRATION TESTS PASSED!")
    print("\nKEY VALIDATIONS:")
    print("  • ScheduleChronotypeContext created successfully")
    print("  • MEQ extraction works from user_profile_data and preferences")
    print("  • Chronotype classification correct")
    print("  • Prime windows assigned correctly")
    print("  • Default UNKNOWN fallback works")
    print("  • Source tracking works (meq vs default)")
    print("=" * 70)


if __name__ == "__main__":
    test_scheduler_chronotype_integration()
