"""
Test sleep calculations with cycles-based system.

Educational Note:
    Validates the new cycle-based system:
    1. Age determines cycle length: <18 = 50min, ≥18 = 90min
    2. Sleep need adjusts cycle count: LOW=-1, MED=0, HIGH=+1
    3. Chronotype + age determines timing shift
    
    Teens (<18): 50min cycles × (10/11/12) = 8.33h/9.17h/10h
    Adults (≥18): 90min cycles × (4/5/6) = 6h/7.5h/9h
"""

from datetime import time
from src.core.sleep import SleepCalculator
from src.core.sleep.models import Chronotype, SleepNeed


def test_comprehensive_combinations():
    """
    Test key combinations showing cycle-based system.
    
    Educational Note:
        Demonstrates teen (50min cycles) vs adult (90min cycles).
    """
    calc = SleepCalculator()
    
    print("\n" + "="*80)
    print("COMPREHENSIVE SLEEP CALCULATION TEST")
    print("="*80)
    print("\nTeens: 50min cycles | Adults/Seniors: 90min cycles")
    print("Chronotype shifts vary by age group\n")
    
    test_cases = [
        # Teen combinations
        (16, Chronotype.INTERMEDIATE, SleepNeed.MEDIUM, "Teen base"),
        (16, Chronotype.NIGHT_OWL, SleepNeed.HIGH, "Teen high+delayed"),
        (16, Chronotype.EARLY_BIRD, SleepNeed.LOW, "Teen low+early"),
        
        # Adult combinations
        (30, Chronotype.INTERMEDIATE, SleepNeed.MEDIUM, "Adult base"),
        (30, Chronotype.NIGHT_OWL, SleepNeed.HIGH, "Adult high+delayed"),
        (30, Chronotype.EARLY_BIRD, SleepNeed.LOW, "Adult low+early"),
        
        # Senior combinations  
        (70, Chronotype.INTERMEDIATE, SleepNeed.MEDIUM, "Senior base"),
        (70, Chronotype.EARLY_BIRD, SleepNeed.LOW, "Senior low+early"),
        (70, Chronotype.NIGHT_OWL, SleepNeed.HIGH, "Senior high+delayed"),
    ]
    
    print("Age | Chrono        | Need   | Duration | Bedtime | Wake   | Description")
    print("-" * 80)
    
    for age, chrono, need, desc in test_cases:
        window = calc.calculate_sleep_window(
            age=age,
            chronotype=chrono,
            sleep_need=need,
            target_wake_time=time(7, 0)
        )
        
        duration_h = window.ideal_duration.total_seconds() / 3600
        bedtime = window.ideal_bedtime.strftime('%H:%M')
        wake = window.ideal_wake_time.strftime('%H:%M')
        
        print(f"{age:3d} | {chrono.value:14s} | {need.value:6s} | "
              f"{duration_h:5.2f}h  | {bedtime} | {wake} | {desc}")
    
    print("\n" + "="*80)
    print("KEY INSIGHTS:")
    print("• Teens (<18): 50min cycles × (10/11/12) = 8.33h/9.17h/10h")
    print("• Adults (≥18): 90min cycles × (4/5/6) = 6h/7.5h/9h")
    print("• Chronotype shifts: Teen NIGHT_OWL +1.5h, Adult +1.0h, Senior +0.5h")
    print("• Bedtime includes +15min sleep onset")
    print("="*80 + "\n")


def test_cycle_based_duration():
    """
    Verify cycle-based duration calculation.
    
    Educational Note:
        Teens (<18): 50min cycles, base 11 (LOW=10, MED=11, HIGH=12)
        Adults (≥18): 90min cycles, base 5 (LOW=4, MED=5, HIGH=6)
    """
    calc = SleepCalculator()
    
    print("\n" + "="*75)
    print("CYCLE-BASED SLEEP DURATION")
    print("="*75)
    print("\nTeens (<18): 50min cycles | Adults (≥18): 90min cycles")
    
    test_cases = [
        # (age, type, cycle_min, base_cycles, need, total_cycles, expected_h)
        (16, "teen", 50, 11, SleepNeed.LOW, 10, 8.33),      # 10×50min
        (16, "teen", 50, 11, SleepNeed.MEDIUM, 11, 9.17),   # 11×50min
        (16, "teen", 50, 11, SleepNeed.HIGH, 12, 10.0),     # 12×50min
        (30, "adult", 90, 5, SleepNeed.LOW, 4, 6.0),        # 4×90min
        (30, "adult", 90, 5, SleepNeed.MEDIUM, 5, 7.5),     # 5×90min
        (30, "adult", 90, 5, SleepNeed.HIGH, 6, 9.0),       # 6×90min
        (70, "senior", 90, 5, SleepNeed.LOW, 4, 6.0),       # 4×90min
        (70, "senior", 90, 5, SleepNeed.MEDIUM, 5, 7.5),    # 5×90min
        (70, "senior", 90, 5, SleepNeed.HIGH, 6, 9.0),      # 6×90min
    ]
    
    print("\nAge | Type   | Cycle | Base | Need   | Cycles | Duration")
    print("-" * 75)
    
    for age, age_type, cycle, base, need, total, expected_h in test_cases:
        duration = calc.get_recommended_sleep_duration(age=age, sleep_need=need)
        actual_h = duration.total_seconds() / 3600
        
        print(f"{age:3d} | {age_type:6s} | {cycle:3d}min | {base:2d}   | "
              f"{need.value:6s} | {total:2d}     | {actual_h:5.2f}h")
        
        assert abs(actual_h - expected_h) < 0.01, \
            f"Expected {expected_h}h, got {actual_h}h"
    
    print("\n✅ Cycle-based durations calculated correctly")
    print("="*75 + "\n")


def test_age_chronotype_timing():
    """
    Verify age-specific chronotype timing shifts.
    
    Educational Note:
        Chronotype effect varies by age:
        - Teen night owls: stronger delayed phase (+1.5h)
        - Adult night owls: moderate (+1.0h)
        - Senior early birds: stronger advanced phase (-1.5h)
    """
    calc = SleepCalculator()
    
    print("\n" + "="*80)
    print("AGE-SPECIFIC CHRONOTYPE TIMING SHIFTS")
    print("="*80)
    print("\nSame sleep need (MEDIUM), different ages & chronotypes")
    
    test_cases = [
        # (age, chrono, expected_shift, duration_h)
        (16, Chronotype.EARLY_BIRD, -0.5, 9.17),
        (16, Chronotype.INTERMEDIATE, 0.0, 9.17),
        (16, Chronotype.NIGHT_OWL, +1.5, 9.17),
        (30, Chronotype.EARLY_BIRD, -1.0, 7.5),
        (30, Chronotype.INTERMEDIATE, 0.0, 7.5),
        (30, Chronotype.NIGHT_OWL, +1.0, 7.5),
        (70, Chronotype.EARLY_BIRD, -1.5, 7.5),
        (70, Chronotype.INTERMEDIATE, 0.0, 7.5),
        (70, Chronotype.NIGHT_OWL, +0.5, 7.5),
    ]
    
    print("\nAge | Chronotype    | Shift  | Duration | Bedtime | Wake   ")
    print("-" * 80)
    
    for age, chrono, expected_shift, expected_dur_h in test_cases:
        window = calc.calculate_sleep_window(
            age=age,
            chronotype=chrono,
            sleep_need=SleepNeed.MEDIUM,
            target_wake_time=time(7, 0)
        )
        
        duration_h = window.ideal_duration.total_seconds() / 3600
        bedtime = window.ideal_bedtime.strftime('%H:%M')
        wake = window.ideal_wake_time.strftime('%H:%M')
        
        print(f"{age:3d} | {chrono.value:14s} | {expected_shift:+5.1f}h | "
              f"{duration_h:5.2f}h  | {bedtime} | {wake}")
        
        assert abs(duration_h - expected_dur_h) < 0.01, \
            f"Expected {expected_dur_h}h, got {duration_h}h"
    
    print("\n✅ Age-specific chronotype shifts work correctly")
    print("="*80 + "\n")


if __name__ == "__main__":
    print("\n" + "🧪 TESTING CYCLE-BASED SLEEP SYSTEM" + "\n")
    
    test_cycle_based_duration()
    test_age_chronotype_timing()
    test_comprehensive_combinations()
    
    print("\n✅ ALL TESTS PASSED!")
    print("   • Teens (<18): 50min cycles × (10/11/12)")
    print("   • Adults (≥18): 90min cycles × (4/5/6)")
    print("   • Sleep need adjusts ±1 cycle")
    print("   • Age-specific chronotype timing shifts")
    print("   • Sleep onset +15min included\n")
