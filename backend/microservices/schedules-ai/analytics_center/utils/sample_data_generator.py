"""
Sample data generator for Analytics Center components.

This module provides realistic sample data for all Analytics Center sections,
enabling users to quickly populate forms with believable test data for
demonstration and development purposes.

Educational Note:
    Sample data generation teaches data modeling patterns and helps users
    understand expected input formats without manual data entry overhead.
"""

from datetime import datetime, time, timedelta
import random
from typing import List, Dict, Any
from models.enhanced_ui import TaskForSchedule, UserProfileData, WearableData, ComputedAlgorithmData


def _round_to_5_minutes(minutes: int) -> int:
    """
    Rounds duration to nearest 5 minutes (ends with 0 or 5).
    
    Args:
        minutes: Original duration in minutes
        
    Returns:
        int: Duration rounded to 5-minute increments
        
    Educational Note:
        Ensures clean time slots that are easier to schedule and display.
        Users prefer times like 30min, 45min over 33min, 47min.
    """
    return max(5, round(minutes / 5) * 5)


def generate_sample_user_profile() -> UserProfileData:
    """
    Generates realistic user profile data with varied demographics and preferences.
    
    Returns:
        UserProfileData: Complete user profile with randomized realistic values
        
    Educational Note:
        Demonstrates how to create varied test data that reflects real user
        diversity while maintaining data consistency and logical relationships.
    """
    names = ["Alex Johnson", "Maria Garcia", "David Chen", "Sarah Williams", "James Brown"]
    industries = ["Tech", "Healthcare", "Finance", "Education", "Marketing"]
    roles = ["Software Engineer", "Data Scientist", "Project Manager", "Designer", "Analyst"]
    sleep_needs = ["low", "medium", "high"]
    
    start_time_obj = time(hour=random.randint(7, 10), minute=random.choice([0, 30]))
    end_time_obj = time(hour=random.randint(16, 19), minute=random.choice([0, 30]))
    
    return UserProfileData(
        name=random.choice(names),
        age=random.randint(22, 55),
        role=random.choice(roles),
        industry=random.choice(industries),
        meq_score=random.randint(15, 85),
        sleep_need=random.choice(sleep_needs),
        start_time=start_time_obj.strftime("%H:%M"),
        end_time=end_time_obj.strftime("%H:%M"),
        location=random.choice(["Office", "Remote", "Hybrid"]),
        type=random.choice(["office", "remote", "hybrid"]),
        commute_minutes=random.randint(15, 60) if random.random() > 0.3 else 0,
        lunch_duration_minutes=random.randint(30, 90),
        morning_duration_minutes=random.randint(15, 60),
        evening_duration_minutes=random.randint(20, 90)
    )


def generate_sample_tasks() -> List[TaskForSchedule]:
    """
    Creates diverse realistic tasks with varied priorities and durations.
    Ensures fixed-time tasks do not overlap.
    
    Returns:
        List[TaskForSchedule]: Collection of tasks representing typical work scenarios
        
    Educational Note:
        Shows how to generate varied task data that reflects real work patterns,
        including different task types, priorities, and time requirements.
        Fixed tasks are scheduled sequentially to prevent overlaps.
    """
    task_templates = [
        ("Code Review", 2, 45, False),
        ("Team Meeting", 3, 60, True),
        ("Documentation", 2, 90, False),
        ("Bug Fix", 4, 30, False),
        ("Client Presentation", 1, 45, True),
        ("Research & Analysis", 3, 120, False),
        ("Email Processing", 5, 25, False),
        ("Project Planning", 3, 75, False),
        ("Training Session", 2, 90, True),
        ("1:1 with Manager", 1, 30, True),
    ]
    
    selected_tasks = random.sample(task_templates, k=random.randint(5, 8))
    tasks = []
    fixed_tasks = []
    flexible_tasks = []
    
    for title, priority, base_duration, is_fixed in selected_tasks:
        duration_variance = random.randint(-10, 20)
        proposed_duration = max(15, base_duration + duration_variance)
        final_duration = _round_to_5_minutes(proposed_duration)
        
        task = TaskForSchedule(
            title=title,
            priority=priority,
            duration_hours=final_duration / 60,
            is_fixed_time=is_fixed
        )
        
        if is_fixed:
            fixed_tasks.append((task, final_duration))
        else:
            flexible_tasks.append(task)
    
    current_time = datetime.strptime("09:00", "%H:%M")
    
    for task, duration_minutes in fixed_tasks:
        task.start_time = current_time.strftime("%H:%M")
        end_time = current_time + timedelta(minutes=duration_minutes)
        task.end_time = end_time.strftime("%H:%M")
        
        gap_duration = _round_to_5_minutes(random.choice([15, 30]))
        current_time = end_time + timedelta(minutes=gap_duration)
        
        if current_time.hour >= 17:
            break
        
        tasks.append(task)
    
    tasks.extend(flexible_tasks)
    
    return tasks


def generate_sample_wearable_data() -> WearableData:
    """
    Generates realistic wearable device metrics based on health patterns.
    
    Returns:
        WearableData: Comprehensive health metrics with logical relationships
        
    Educational Note:
        Demonstrates how biometric data correlates and how to generate
        realistic health metrics that maintain physiological consistency.
    """
    # Base sleep quality affects other metrics
    sleep_quality_options = ["Poor", "Fair", "Good", "Excellent"]
    sleep_quality = random.choice(sleep_quality_options)
    
    # Sleep duration correlates with quality
    if sleep_quality == "Poor":
        sleep_duration = random.uniform(4.5, 6.0)
        deep_sleep_pct = random.randint(10, 18)
        rem_sleep_pct = random.randint(8, 15)
    elif sleep_quality == "Fair":
        sleep_duration = random.uniform(6.0, 7.0)
        deep_sleep_pct = random.randint(15, 22)
        rem_sleep_pct = random.randint(12, 20)
    elif sleep_quality == "Good":
        sleep_duration = random.uniform(7.0, 8.5)
        deep_sleep_pct = random.randint(20, 28)
        rem_sleep_pct = random.randint(18, 25)
    else:  # Excellent
        sleep_duration = random.uniform(8.0, 9.0)
        deep_sleep_pct = random.randint(25, 35)
        rem_sleep_pct = random.randint(22, 30)
    
    # Activity metrics correlate with sleep and stress
    steps_yesterday = random.randint(3000, 15000)
    avg_heart_rate = random.randint(60, 85)
    
    # Stress and readiness correlate with sleep quality
    stress_levels = ["Very Low", "Low", "Moderate", "High", "Very High"]
    if sleep_quality in ["Good", "Excellent"]:
        stress_level = random.choice(["Very Low", "Low", "Moderate"])
        readiness_score = random.uniform(0.7, 1.0)
        recovery_index = random.randint(70, 95)
    else:
        stress_level = random.choice(["Moderate", "High", "Very High"])
        readiness_score = random.uniform(0.3, 0.7)
        recovery_index = random.randint(30, 70)
    
    return WearableData(
        sleep_quality=sleep_quality,
        sleep_duration_hours=round(sleep_duration, 1),
        deep_sleep_percentage=deep_sleep_pct,
        rem_sleep_percentage=rem_sleep_pct,
        steps_yesterday=steps_yesterday,
        avg_heart_rate=avg_heart_rate,
        stress_level=stress_level,
        readiness_score=round(readiness_score, 2),
        recovery_index=recovery_index
    )


def generate_sample_algorithm_results() -> ComputedAlgorithmData:
    """
    Creates realistic algorithm computation results with logical correlations.
    
    Returns:
        ComputedAlgorithmData: Algorithm outputs showing computed insights
        
    Educational Note:
        Shows how algorithm results should correlate with input data and
        demonstrate realistic ranges for performance metrics.
    """
    # Generate correlated energy and performance metrics
    energy_level = random.uniform(0.4, 0.95)
    
    # Fatigue inversely correlates with energy
    fatigue_level = max(0.1, 1.0 - energy_level + random.uniform(-0.2, 0.2))
    
    # Motivation correlates with energy but has its own variance
    motivation_level = energy_level * random.uniform(0.8, 1.2)
    motivation_level = min(1.0, max(0.1, motivation_level))
    
    # Detected chronotype based on energy patterns
    chronotypes = ["Morning Lark", "Evening Owl", "Intermediate"]
    detected_chronotype = random.choice(chronotypes)
    
    # Confidence correlates with data quality
    confidence = random.uniform(0.6, 0.95)
    
    # Schedule optimization metrics
    optimal_bedtime = time(hour=random.randint(21, 23), minute=random.choice([0, 15, 30, 45]))
    optimal_wake_time = time(hour=random.randint(6, 8), minute=random.choice([0, 15, 30, 45]))
    
    sleep_quality_score = random.uniform(0.5, 0.95)
    schedule_efficiency = random.uniform(0.6, 0.9)
    energy_alignment = random.uniform(0.4, 0.85)
    
    return ComputedAlgorithmData(
        energy_level=random.randint(1, 5),
        fatigue_level=random.randint(1, 5),
        motivation_level=random.randint(1, 5),
        detected_chronotype=detected_chronotype,
        chronotype_confidence=round(confidence, 2),
        recommended_bedtime=optimal_bedtime.strftime("%H:%M"),
        recommended_wake_time=optimal_wake_time.strftime("%H:%M"),
        sleep_quality_score=round(sleep_quality_score * 100, 1),
        schedule_efficiency=round(schedule_efficiency, 2),
        energy_alignment_score=round(energy_alignment, 2)
    )


def compute_algorithm_results_from_data(user_profile: UserProfileData, wearable_data: WearableData, tasks: List[TaskForSchedule]) -> ComputedAlgorithmData:
    """
    Computes algorithm results based on actual user input data.
    
    Args:
        user_profile: User profile and preferences
        wearable_data: Wearable device metrics
        tasks: List of tasks to be scheduled
        
    Returns:
        ComputedAlgorithmData with computed insights based on input data
        
    Educational Note:
        Shows how to derive meaningful algorithm results from user inputs,
        demonstrating the relationship between chronotype, sleep data, and optimization.
    """
    # Compute energy level from chronotype and sleep quality
    chronotype_energy_map = {
        "Poor": 1, "Fair": 2, "Good": 4, "Excellent": 5
    }
    base_energy = chronotype_energy_map.get(wearable_data.sleep_quality, 3)
    
    # Adjust based on MEQ score (chronotype)
    if user_profile.meq_score < 31:  # Night owl
        energy_adjustment = -1 if datetime.now().hour < 10 else 1
    elif user_profile.meq_score > 69:  # Early bird  
        energy_adjustment = 1 if datetime.now().hour < 12 else -1
    else:  # Intermediate
        energy_adjustment = 0
    
    energy_level = max(1, min(5, base_energy + energy_adjustment))
    
    # Compute fatigue inversely related to energy and readiness
    fatigue_level = max(1, min(5, 6 - energy_level + (1 if wearable_data.readiness_score < 0.6 else 0)))
    
    # Motivation based on energy and stress
    stress_penalty = {"Low": 0, "Moderate": -1, "High": -2, "Very High": -3}
    motivation_level = max(1, min(5, energy_level + stress_penalty.get(wearable_data.stress_level, 0)))
    
    # Detect chronotype from MEQ score
    if user_profile.meq_score < 31:
        chronotype = "Night Owl"
    elif user_profile.meq_score > 69:
        chronotype = "Morning Lark"
    else:
        chronotype = "Intermediate"
    
    # Confidence based on data completeness
    confidence = 0.7 + (0.1 if len(tasks) > 3 else 0) + (0.1 if wearable_data.sleep_duration_hours > 6 else 0) + (0.1 if user_profile.meq_score != 50 else 0)
    confidence = min(1.0, confidence)
    
    # Optimal sleep times based on chronotype
    if chronotype == "Night Owl":
        bedtime = time(hour=23, minute=30)
        wake_time = time(hour=8, minute=0)
    elif chronotype == "Morning Lark":
        bedtime = time(hour=22, minute=0)
        wake_time = time(hour=6, minute=30)
    else:  # Intermediate
        bedtime = time(hour=22, minute=45)
        wake_time = time(hour=7, minute=15)
    
    # Schedule efficiency based on task variety and energy alignment
    task_variety = len(set(t.title for t in tasks)) / max(1, len(tasks))
    energy_task_alignment = 0.8 if energy_level >= 4 else 0.6 if energy_level >= 3 else 0.4
    schedule_efficiency = (task_variety + energy_task_alignment) / 2
    
    # Sleep quality score from wearable data
    sleep_quality_score = (wearable_data.deep_sleep_percentage + wearable_data.rem_sleep_percentage) * 1.5
    sleep_quality_score = min(100.0, sleep_quality_score)
    
    return ComputedAlgorithmData(
        energy_level=energy_level,
        fatigue_level=fatigue_level,
        motivation_level=motivation_level,
        detected_chronotype=chronotype,
        chronotype_confidence=confidence,
        recommended_bedtime=bedtime.strftime("%H:%M"),
        recommended_wake_time=wake_time.strftime("%H:%M"),
        sleep_quality_score=sleep_quality_score,
        schedule_efficiency=schedule_efficiency,
        energy_alignment_score=energy_task_alignment
    )


def generate_complete_sample_data() -> Dict[str, Any]:
    """
    Generates complete sample dataset for all Analytics Center components.
    
    Returns:
        Dict containing all sample data components with logical relationships
        
    Educational Note:
        Demonstrates how to create comprehensive test data sets that maintain
        consistency across related data components and reflect real-world scenarios.
    """
    return {
        "user_profile": generate_sample_user_profile(),
        "tasks": generate_sample_tasks(),
        "wearable_data": generate_sample_wearable_data(),
        "algorithm_results": generate_sample_algorithm_results()
    }
