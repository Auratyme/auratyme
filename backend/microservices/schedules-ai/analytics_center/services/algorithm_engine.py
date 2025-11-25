"""Algorithm service for computing derived data from user inputs.

Educational Rationale:
This service encapsulates the business logic for transforming user-provided
data into computed insights. Each function has a single responsibility and
can be easily tested and extended with new algorithms.
"""
from __future__ import annotations
import sys
import os
from typing import Optional, List, Dict, Any
from datetime import datetime, time, timedelta

# Add analytics_center to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from models.enhanced_ui import UserProfileData, WearableData, ComputedAlgorithmData

def compute_algorithm_results(
    user_profile: UserProfileData,
    wearable_data: Optional[WearableData] = None
) -> ComputedAlgorithmData:
    """
    Compute all algorithm-derived data from user inputs.
    
    This is the main orchestration function that calls all individual
    algorithm functions to generate computed insights.
    """
    results = ComputedAlgorithmData()
    
    # Chronotype analysis from MEQ score
    chronotype_info = _analyze_chronotype(user_profile.meq_score)
    results.detected_chronotype = chronotype_info['type']
    results.chronotype_confidence = chronotype_info['confidence']
    
    # Sleep analysis
    sleep_info = _calculate_optimal_sleep(user_profile, chronotype_info['type'])
    results.recommended_bedtime = sleep_info['bedtime']
    results.recommended_wake_time = sleep_info['wake_time']
    
    # Energy and performance analysis
    if wearable_data:
        energy_info = _analyze_energy_levels(user_profile, wearable_data, chronotype_info['type'])
        results.energy_level = energy_info['energy_level']
        results.fatigue_level = energy_info['fatigue_level']
        results.motivation_level = energy_info['motivation_level']
        results.sleep_quality_score = energy_info['sleep_score']
    
    # Work optimization
    work_info = _calculate_optimal_work_windows(user_profile, chronotype_info['type'])
    results.optimal_work_windows = work_info['windows']
    results.optimal_break_times = work_info['breaks']
    
    # Placeholder metrics (will be computed after schedule generation)
    results.schedule_efficiency = None
    results.energy_alignment_score = None 
    results.break_density = None
    
    return results

def _analyze_chronotype(meq_score: int) -> Dict[str, Any]:
    """
    Analyze chronotype from MEQ score.
    
    Uses the standard MEQ ranges to determine chronotype classification
    and confidence based on how extreme the score is.
    """
    if meq_score <= 30:
        chronotype = "Night Owl"
        # Higher confidence for more extreme scores
        confidence = min(0.9, 0.5 + (30 - meq_score) * 0.02)
    elif meq_score >= 70:
        chronotype = "Early Bird"
        confidence = min(0.9, 0.5 + (meq_score - 70) * 0.02)
    else:
        chronotype = "Intermediate"
        # Lower confidence for intermediate scores
        distance_from_center = abs(meq_score - 50)
        confidence = max(0.3, 0.8 - distance_from_center * 0.01)
    
    return {
        'type': chronotype,
        'confidence': confidence
    }

def _calculate_optimal_sleep(user_profile: UserProfileData, chronotype: str) -> Dict[str, str]:
    """
    Calculate optimal sleep times based on work schedule and chronotype.
    
    Uses work start time and chronotype to determine ideal sleep window.
    """
    # Parse work start time
    work_start = datetime.strptime(user_profile.start_time, '%H:%M').time()
    
    # Account for commute
    commute_buffer = timedelta(minutes=user_profile.commute_minutes + user_profile.morning_duration_minutes)
    
    # Calculate required wake time
    work_start_dt = datetime.combine(datetime.today(), work_start)
    wake_time_dt = work_start_dt - commute_buffer
    
    # Adjust based on chronotype
    if chronotype == "Early Bird":
        # Early birds can wake up slightly earlier
        wake_time_dt -= timedelta(minutes=15)
        sleep_duration = 7.5  # Slightly less sleep needed
    elif chronotype == "Night Owl":
        # Night owls need later wake times when possible
        wake_time_dt += timedelta(minutes=15)
        sleep_duration = 8.5  # More sleep needed
    else:
        sleep_duration = 8.0  # Standard 8 hours
    
    # Calculate bedtime (8 hours before wake time)
    bedtime_dt = wake_time_dt - timedelta(hours=sleep_duration)
    
    return {
        'bedtime': bedtime_dt.strftime('%H:%M'),
        'wake_time': wake_time_dt.strftime('%H:%M')
    }

def _analyze_energy_levels(user_profile: UserProfileData, wearable_data: WearableData, chronotype: str) -> Dict[str, Any]:
    """
    Analyze energy and fatigue levels from wearable data.
    
    Combines sleep quality, stress, readiness score, and chronotype
    to determine current energy and fatigue levels.
    """
    # Base energy from readiness score (0.0-1.0 -> 1-5)
    base_energy = max(1, min(5, int(wearable_data.readiness_score * 4) + 1))
    
    # Adjust for sleep quality
    sleep_adjustments = {
        "Poor": -1,
        "Fair": 0,
        "Good": 1,
        "Excellent": 2
    }
    energy_level = base_energy + sleep_adjustments.get(wearable_data.sleep_quality, 0)
    
    # Adjust for stress
    stress_adjustments = {
        "Low": 1,
        "Moderate": 0,
        "High": -1,
        "Very High": -2
    }
    energy_level += stress_adjustments.get(wearable_data.stress_level, 0)
    
    # Clamp to valid range
    energy_level = max(1, min(5, energy_level))
    
    # Fatigue is inverse of energy, adjusted for sleep duration
    base_fatigue = 6 - energy_level
    if wearable_data.sleep_duration_hours < 6:
        base_fatigue += 2
    elif wearable_data.sleep_duration_hours > 9:
        base_fatigue += 1
    
    fatigue_level = max(1, min(5, base_fatigue))
    
    # Motivation based on recovery index and recent performance
    motivation_base = max(1, min(5, int(wearable_data.recovery_index / 20) + 1))
    
    # Adjust motivation for activity level (steps)
    if wearable_data.steps_yesterday > 10000:
        motivation_level = min(5, motivation_base + 1)
    elif wearable_data.steps_yesterday < 5000:
        motivation_level = max(1, motivation_base - 1)
    else:
        motivation_level = motivation_base
    
    # Sleep quality score (0-100 based on multiple factors)
    sleep_score = _calculate_sleep_quality_score(wearable_data)
    
    return {
        'energy_level': energy_level,
        'fatigue_level': fatigue_level,
        'motivation_level': motivation_level,
        'sleep_score': sleep_score
    }

def _calculate_sleep_quality_score(wearable_data: WearableData) -> float:
    """Calculate comprehensive sleep quality score from wearable metrics."""
    # Base score from subjective quality
    quality_scores = {
        "Poor": 25.0,
        "Fair": 50.0,
        "Good": 75.0,
        "Excellent": 95.0
    }
    base_score = quality_scores.get(wearable_data.sleep_quality, 50.0)
    
    # Duration component (optimal around 7-8 hours)
    duration = wearable_data.sleep_duration_hours
    if 7.0 <= duration <= 8.5:
        duration_score = 100.0
    elif 6.0 <= duration < 7.0 or 8.5 < duration <= 9.0:
        duration_score = 80.0
    elif 5.0 <= duration < 6.0 or 9.0 < duration <= 10.0:
        duration_score = 60.0
    else:
        duration_score = 40.0
    
    # Sleep stage quality (deep + REM should be reasonable)
    total_quality_sleep = wearable_data.deep_sleep_percentage + wearable_data.rem_sleep_percentage
    if total_quality_sleep >= 35:
        stage_score = 100.0
    elif total_quality_sleep >= 25:
        stage_score = 80.0
    elif total_quality_sleep >= 15:
        stage_score = 60.0
    else:
        stage_score = 40.0
    
    # Weighted combination
    final_score = (base_score * 0.4) + (duration_score * 0.3) + (stage_score * 0.3)
    return round(final_score, 1)

def _calculate_optimal_work_windows(user_profile: UserProfileData, chronotype: str) -> Dict[str, Any]:
    """
    Calculate optimal work windows based on chronotype and preferences.
    
    Returns suggested high-focus work periods and break times.
    """
    work_start = datetime.strptime(user_profile.start_time, '%H:%M')
    work_end = datetime.strptime(user_profile.end_time, '%H:%M')
    
    if chronotype == "Early Bird":
        # Early birds peak in the morning
        morning_window = f"{work_start.strftime('%H:%M')}-{(work_start + timedelta(hours=3)).strftime('%H:%M')}"
        afternoon_window = f"{(work_end - timedelta(hours=2)).strftime('%H:%M')}-{work_end.strftime('%H:%M')}"
        
        break_times = ["10:30", "14:30"]
        
    elif chronotype == "Night Owl":
        # Night owls peak later in the day
        late_morning = work_start + timedelta(hours=2)
        morning_window = f"{late_morning.strftime('%H:%M')}-{(late_morning + timedelta(hours=2.5)).strftime('%H:%M')}"
        afternoon_window = f"{(work_end - timedelta(hours=2.5)).strftime('%H:%M')}-{work_end.strftime('%H:%M')}"
        
        break_times = ["11:00", "15:00"]
        
    else:  # Intermediate
        # Balanced schedule with mid-morning and mid-afternoon peaks
        morning_peak = work_start + timedelta(hours=1.5)
        morning_window = f"{morning_peak.strftime('%H:%M')}-{(morning_peak + timedelta(hours=2)).strftime('%H:%M')}"
        
        afternoon_peak = work_start + timedelta(hours=6)
        afternoon_window = f"{afternoon_peak.strftime('%H:%M')}-{(afternoon_peak + timedelta(hours=1.5)).strftime('%H:%M')}"
        
        break_times = ["10:45", "15:15"]
    
    return {
        'windows': [morning_window, afternoon_window],
        'breaks': break_times
    }
