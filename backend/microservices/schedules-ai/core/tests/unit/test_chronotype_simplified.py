"""
Test simplified chronotype system.

Educational Note:
    Tests verify:
    1. MEQ score → Chronotype conversion
    2. Chronotype → Prime window mapping
    3. Complete MEQ analysis flow
"""

from datetime import time

from src.core.chronotype import ChronotypeAnalyzer, Chronotype


def test_meq_to_chronotype():
    """Test MEQ score classification."""
    analyzer = ChronotypeAnalyzer()
    
    print("\n" + "="*70)
    print("MEQ SCORE TO CHRONOTYPE CLASSIFICATION")
    print("="*70)
    print("\nMEQ Score | Chronotype")
    print("-" * 30)
    
    test_cases = [
        (20, Chronotype.NIGHT_OWL, "Definite Evening"),
        (40, Chronotype.NIGHT_OWL, "Moderate Evening"),
        (45, Chronotype.INTERMEDIATE, "Neither"),
        (55, Chronotype.INTERMEDIATE, "Neither"),
        (60, Chronotype.EARLY_BIRD, "Moderate Morning"),
        (75, Chronotype.EARLY_BIRD, "Definite Morning"),
    ]
    
    for meq, expected, desc in test_cases:
        result = analyzer.determine_chronotype_from_meq(meq)
        status = "✓" if result == expected else "✗"
        print(f"{meq:3d}       | {result.value:14s} {status} ({desc})")
        assert result == expected, f"MEQ {meq} should be {expected.value}"
    
    print("="*70 + "\n")


def test_prime_windows():
    """Test prime window retrieval."""
    analyzer = ChronotypeAnalyzer()
    
    print("\n" + "="*70)
    print("CHRONOTYPE PRIME WINDOWS")
    print("="*70)
    print("\nChronotype     | Prime Window      | Duration")
    print("-" * 55)
    
    for chronotype in [Chronotype.EARLY_BIRD, Chronotype.INTERMEDIATE, Chronotype.NIGHT_OWL]:
        window = analyzer.get_prime_window(chronotype)
        duration = window.duration_hours()
        start_str = window.start.strftime("%H:%M")
        end_str = window.end.strftime("%H:%M")
        
        print(f"{chronotype.value:14s} | {start_str}-{end_str}     | {duration:.1f}h")
        
        # Verify window characteristics
        assert window.chronotype == chronotype
        assert 3.0 <= duration <= 6.0, "Prime window should be 3-6h"
    
    print("="*70 + "\n")


def test_complete_analysis():
    """Test complete MEQ analysis flow."""
    analyzer = ChronotypeAnalyzer()
    
    print("\n" + "="*70)
    print("COMPLETE MEQ ANALYSIS")
    print("="*70)
    print("\nMEQ | Chronotype     | Prime Window      | Duration")
    print("-" * 60)
    
    test_meq_scores = [25, 50, 70, None]
    
    for meq in test_meq_scores:
        chronotype, prime_window = analyzer.analyze_meq(meq)
        duration = prime_window.duration_hours()
        start_str = prime_window.start.strftime("%H:%M")
        end_str = prime_window.end.strftime("%H:%M")
        meq_str = str(meq) if meq is not None else "None"
        
        print(f"{meq_str:3s} | {chronotype.value:14s} | {start_str}-{end_str}     | {duration:.1f}h")
    
    print("\n" + "="*70)
    print("KEY INSIGHTS:")
    print("• EARLY_BIRD (MEQ 59-86): Peak 07:00-11:00 (4h morning)")
    print("• INTERMEDIATE (MEQ 42-58): Peak 10:00-16:00 (6h mid-day)")
    print("• NIGHT_OWL (MEQ 16-41): Peak 17:00-22:00 (5h evening)")
    print("• UNKNOWN (no MEQ): Default 10:00-14:00 (4h safe window)")
    print("="*70 + "\n")


def test_expected_windows():
    """Verify specific window times match requirements."""
    analyzer = ChronotypeAnalyzer()
    
    print("\n" + "="*70)
    print("VERIFY REQUIRED PRIME WINDOWS")
    print("="*70 + "\n")
    
    # Early Bird: 7:00-11:00
    window = analyzer.get_prime_window(Chronotype.EARLY_BIRD)
    assert window.start == time(7, 0), "Early bird should start at 07:00"
    assert window.end == time(11, 0), "Early bird should end at 11:00"
    print("✓ EARLY_BIRD: 07:00-11:00 (4h)")
    
    # Intermediate: 10:00-16:00
    window = analyzer.get_prime_window(Chronotype.INTERMEDIATE)
    assert window.start == time(10, 0), "Intermediate should start at 10:00"
    assert window.end == time(16, 0), "Intermediate should end at 16:00"
    print("✓ INTERMEDIATE: 10:00-16:00 (6h)")
    
    # Night Owl: 17:00-22:00
    window = analyzer.get_prime_window(Chronotype.NIGHT_OWL)
    assert window.start == time(17, 0), "Night owl should start at 17:00"
    assert window.end == time(22, 0), "Night owl should end at 22:00"
    print("✓ NIGHT_OWL: 17:00-22:00 (5h)")
    
    print("\n✅ All prime windows match requirements!")
    print("="*70 + "\n")


if __name__ == "__main__":
    print("\n🧪 TESTING SIMPLIFIED CHRONOTYPE SYSTEM\n")
    
    test_meq_to_chronotype()
    test_prime_windows()
    test_expected_windows()
    test_complete_analysis()
    
    print("\n✅ ALL TESTS PASSED!")
    print("   • MEQ → Chronotype classification working")
    print("   • Prime windows correctly configured")
    print("   • Complete analysis flow functional\n")
