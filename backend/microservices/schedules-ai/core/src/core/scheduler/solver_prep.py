"""
Solver input preparation for constraint-based scheduling.

This module converts high-level schedule requests into constraint solver format,
handling task conversion, fixed event processing, and sleep window integration.
"""

import logging
from datetime import datetime, time, timedelta, timezone
from typing import TYPE_CHECKING, List, Optional
from uuid import UUID

from src.core.solver import FixedEventInterval, SolverInput, SolverTask
from src.utils.time_utils import (
    parse_duration_string,
    time_to_total_minutes,
    total_minutes_to_time,
)
from src.core.scheduler.adaptive_sleep import calculate_adaptive_sleep_window

if TYPE_CHECKING:
    from src.core.scheduler.models import ScheduleInputData, ScheduleChronotypeContext
    from src.core.sleep import SleepMetrics
    from src.core.task import TaskPrioritizer

logger = logging.getLogger(__name__)


def prepare_solver_input(
    input_data: "ScheduleInputData",
    chronotype_context: "ScheduleChronotypeContext",
    sleep_metrics: "SleepMetrics",
    task_prioritizer: "TaskPrioritizer"
) -> Optional[tuple]:
    """
    Converts input data to SolverInput with adaptive sleep calculation.
    
    ADAPTIVE SLEEP STRATEGY:
    1. Convert tasks and events to solver format
    2. IF fixed events exist: Calculate ADAPTIVE wake/bedtime FROM commitments
    3. IF no fixed events: Use ideal sleep_metrics from SleepCalculator
    4. Add routines based on calculated wake/bedtime
    5. Add lunch block after work
    6. Add sleep windows based on calculated wake/bedtime
    7. Return solver input + adjusted sleep metrics + fixed events
    
    Returns:
        Tuple of (SolverInput, adjusted_sleep_metrics, all_fixed_events_dict) or None on error
    
    Educational Note:
        Adaptive sleep mirrors human planning: "I have work at 8am, so I must
        wake at 6:30" rather than "I want to wake at 7am, fit work somehow".
        
        Sleep onset (15min) is handled in BOTH paths:
        - SleepCalculator includes it in bedtime calculation
        - Adaptive sleep includes it when working backwards from wake time
        
        This ensures consistent sleep_onset handling regardless of whether
        schedule has fixed commitments or is completely flexible.
    """
    try:
        solver_tasks = _convert_tasks_to_solver_format(input_data)
        solver_events, earliest_event = _convert_events_to_solver_format(input_data)
        
        if solver_events:
            sleep_metrics_adjusted = _calculate_adaptive_sleep_metrics(
                solver_events, input_data, chronotype_context, sleep_metrics
            )
            logger.info(f"✅ Using ADAPTIVE sleep (adjusted for fixed events)")
        else:
            sleep_metrics_adjusted = sleep_metrics
            logger.info(f"✅ Using IDEAL sleep (no fixed events to adapt to)")
        
        _add_routine_blocks_as_fixed_events(
            solver_events, sleep_metrics_adjusted, input_data.preferences, earliest_event
        )
        
        _add_lunch_block_as_fixed_event(
            solver_events, sleep_metrics_adjusted, input_data.preferences
        )
        
        _add_sleep_windows_to_events(
            solver_events, sleep_metrics_adjusted, earliest_event
        )
        
        all_fixed_events_for_llm = _convert_solver_events_to_dicts(solver_events)
        
        energy_pattern = chronotype_context.energy_pattern
        
        if not energy_pattern:
            logger.warning("⚠️ No energy pattern in context, using flat 0.5 (fallback)")
            energy_pattern = {h: 0.5 for h in range(24)}
        else:
            logger.info(f"✅ Using chronotype-based energy pattern with {len([e for e in energy_pattern.values() if e >= 0.9])} peak hours")
        
        solver_input = SolverInput(
            target_date=input_data.target_date,
            day_start_minutes=0,
            day_end_minutes=1440,
            tasks=solver_tasks,
            fixed_events=solver_events,
            user_energy_pattern=energy_pattern,
        )
        
        return (solver_input, sleep_metrics_adjusted, all_fixed_events_for_llm)
        
    except Exception:
        logger.exception("Error preparing SolverInput.")
        return None


def _calculate_adaptive_sleep_metrics(
    solver_events: List[FixedEventInterval],
    input_data: "ScheduleInputData",
    chronotype_context: "ScheduleChronotypeContext",
    original_sleep_metrics: "SleepMetrics"
) -> "SleepMetrics":
    """
    Calculates adaptive sleep metrics based on fixed events.
    
    Educational Note:
        When user has commitments (work, meetings), sleep must adapt
        to fit around those constraints. This function uses the
        adaptive_sleep module to calculate realistic wake/bedtime
        that respects both commitments and sleep needs.
        
        Original sleep_metrics from SleepCalculator provides ideal
        sleep duration, which adaptive_sleep uses as target to
        maintain whenever possible.
    """
    user_profile = input_data.user_profile_data or {}
    
    sleep_duration_hours = original_sleep_metrics.ideal_duration.total_seconds() / 3600
    
    wake_min, bed_min = calculate_adaptive_sleep_window(
        fixed_events=solver_events,
        preferences=input_data.preferences,
        chronotype=chronotype_context.chronotype,
        sleep_need_hours=sleep_duration_hours,
        user_profile=user_profile
    )
    
    adjusted_metrics = _create_adjusted_sleep_metrics(
        original_sleep_metrics,
        wake_min,
        bed_min
    )
    
    logger.info(f"")
    logger.info(f"🔄 SLEEP ADAPTATION SUMMARY:")
    logger.info(f"   IDEAL (from chronotype):  {original_sleep_metrics.ideal_bedtime.strftime('%H:%M')} → {original_sleep_metrics.ideal_wake_time.strftime('%H:%M')}")
    logger.info(f"   ADAPTED (for commitments): {adjusted_metrics.ideal_bedtime.strftime('%H:%M')} → {adjusted_metrics.ideal_wake_time.strftime('%H:%M')}")
    
    if (original_sleep_metrics.ideal_bedtime != adjusted_metrics.ideal_bedtime or 
        original_sleep_metrics.ideal_wake_time != adjusted_metrics.ideal_wake_time):
        logger.info(f"   ⚠️  Sleep times adjusted to fit fixed events")
    else:
        logger.info(f"   ✅ No adjustment needed - ideal times work with schedule")
    logger.info(f"")
    
    return adjusted_metrics


def _convert_tasks_to_solver_format(
    input_data: "ScheduleInputData"
) -> List[SolverTask]:
    """
    Converts Task objects to SolverTask format.
    
    Educational Note:
        Skips completed tasks and validates duration/timing constraints.
        Invalid tasks are logged but don't block schedule generation.
    """
    solver_tasks = []
    
    for task in input_data.tasks:
        if task.completed:
            continue
        
        solver_task = _create_solver_task(task, input_data.target_date)
        if solver_task:
            solver_tasks.append(solver_task)
    
    return solver_tasks


def _create_solver_task(
    task, target_date
) -> Optional[SolverTask]:
    """
    Creates a single SolverTask from Task object.
    
    Educational Note:
        Handles multiple duration formats (timedelta, string, numeric)
        for API flexibility across different client implementations.
    """
    dur_min = _parse_task_duration(task)
    if not dur_min or dur_min <= 0:
        logger.warning(f"Invalid task duration for {task.id}: {task.duration}")
        return None
    
    earliest_start = _parse_earliest_start(task)
    latest_end = _parse_latest_end(task, target_date)
    dependencies = _extract_dependencies(task)
    
    return SolverTask(
        id=task.id,
        duration_minutes=dur_min,
        priority=task.priority.value,
        energy_level=task.energy_level.value,
        earliest_start_minutes=earliest_start,
        latest_end_minutes=latest_end,
        dependencies=dependencies,
    )


def _parse_task_duration(task) -> Optional[int]:
    """
    Parses task duration to minutes.
    
    Educational Note:
        Supports timedelta objects (precise), strings (human-readable),
        and numeric values (legacy compatibility).
    """
    if isinstance(task.duration, timedelta):
        return int(task.duration.total_seconds() // 60)
    
    if isinstance(task.duration, str):
        parsed = parse_duration_string(task.duration)
        if parsed:
            return int(parsed.total_seconds() // 60)
    
    if isinstance(task.duration, (int, float)):
        return int(task.duration)
    
    return None


def _parse_earliest_start(task) -> Optional[int]:
    """
    Parses earliest start time to minutes from midnight.
    
    Educational Note:
        Converts time objects to minute offsets for constraint solver.
        None value means no constraint on start time.
    """
    if isinstance(task.earliest_start, time):
        return time_to_total_minutes(task.earliest_start)
    return None


def _parse_latest_end(task, target_date) -> Optional[int]:
    """
    Parses latest end time (deadline) to minutes from day start.
    
    Educational Note:
        Handles datetime deadlines by converting to minutes offset
        within the target day, supporting multi-day task scheduling.
    """
    if not isinstance(task.deadline, datetime):
        return None
    
    deadline_utc = task.deadline.astimezone(timezone.utc)
    day_start = datetime.combine(
        target_date, time(0), tzinfo=timezone.utc
    )
    
    return int((deadline_utc - day_start).total_seconds() // 60)


def _extract_dependencies(task) -> List[UUID]:
    """
    Extracts task dependencies as UUID list.
    
    Educational Note:
        Validates dependency types to ensure solver receives
        only valid task references.
    """
    deps = getattr(task, "dependencies", set())
    return [d for d in deps if isinstance(d, UUID)]


def _convert_events_to_solver_format(
    input_data: "ScheduleInputData"
) -> tuple[List[FixedEventInterval], Optional[int]]:
    """
    Converts fixed events to solver format and tracks earliest event.
    
    Educational Note:
        Tracks earliest event to avoid scheduling sleep conflicts.
        Midnight (00:00) as end time maps to 1440 minutes.
    """
    solver_events = []
    earliest_start = None
    
    for event in input_data.fixed_events_input:
        interval, start_min = _create_fixed_event(event)
        solver_events.append(interval)
        
        if earliest_start is None or start_min < earliest_start:
            earliest_start = start_min
    
    _check_fixed_events_overlaps(solver_events)
    
    return solver_events, earliest_start


def _create_fixed_event(
    event: dict
) -> tuple[FixedEventInterval, int]:
    """
    Creates a fixed event interval from dictionary.
    
    Educational Note:
        Handles midnight edge case where end time equals start time
        by adding 1 minute to prevent zero-duration events.
    """
    start_time = time.fromisoformat(event.get("start_time"))
    end_time = time.fromisoformat(event.get("end_time"))
    
    start_min = time_to_total_minutes(start_time)
    end_min = 1440 if end_time == time(0, 0) else time_to_total_minutes(end_time)
    
    if end_min <= start_min:
        end_min = start_min + 1
    
    return (
        FixedEventInterval(
            id=event.get("id"),
            start_minutes=start_min,
            end_minutes=end_min,
            name=event.get("name")
        ),
        start_min
    )


def _add_routine_blocks_as_fixed_events(
    solver_events: List[FixedEventInterval],
    sleep_metrics: "SleepMetrics",
    preferences: dict,
    earliest_fixed_event: Optional[int] = None
) -> None:
    """
    Adds morning and evening routines as fixed events.
    
    Routines are CRITICAL user requirements:
    - Morning routine: Starts at wake time, ends before earliest fixed event
    - Evening routine: ALWAYS present, fixed duration, directly before sleep
    
    Both routines are non-negotiable fixed events that solver must respect.
    
    Educational Note:
        Evening routine is a mandatory pre-sleep activity (dinner, hygiene, wind-down).
        Cannot be skipped or moved - it's part of user's daily structure.
        Bedtime calculation must account for this by placing sleep AFTER evening routine,
        not trying to squeeze evening routine into already-constrained time.
    """
    if not preferences:
        return
    
    routines = preferences.get("routines", {})
    morning_duration = routines.get("morning_duration_minutes", 30)
    evening_duration = routines.get("evening_duration_minutes", 45)
    
    wake_min = time_to_total_minutes(sleep_metrics.ideal_wake_time)
    bed_min = time_to_total_minutes(sleep_metrics.ideal_bedtime)
    
    logger.info(f"🔍 ROUTINE TIMING DEBUG:")
    logger.info(f"   bed_min: {bed_min} ({total_minutes_to_time(bed_min).strftime('%H:%M')})")
    logger.info(f"   evening_duration: {evening_duration}min")
    
    morning_start = wake_min
    ideal_morning_end = wake_min + morning_duration
    
    if earliest_fixed_event is not None and ideal_morning_end > earliest_fixed_event:
        morning_end = earliest_fixed_event
        actual_morning_duration = morning_end - morning_start
        if actual_morning_duration < 5:
            logger.warning(f"⚠️ Morning routine would be too short ({actual_morning_duration}min) due to early fixed event at {total_minutes_to_time(earliest_fixed_event).strftime('%H:%M')}. Skipping morning routine.")
            morning_end = None
        else:
            logger.info(f"⚠️ Morning routine truncated: {morning_duration}min → {actual_morning_duration}min to avoid overlap with fixed event at {total_minutes_to_time(earliest_fixed_event).strftime('%H:%M')}.")
    else:
        morning_end = ideal_morning_end
    
    evening_end = bed_min
    evening_start = evening_end - evening_duration
    
    logger.info(f"   evening_start: {evening_start} ({total_minutes_to_time(evening_start).strftime('%H:%M')})")
    logger.info(f"   evening_end: {evening_end} ({total_minutes_to_time(evening_end).strftime('%H:%M')})")
    
    if morning_end is not None:
        solver_events.append(
            FixedEventInterval(
                id="morning_routine",
                start_minutes=morning_start,
                end_minutes=morning_end,
                name="Morning Routine"
            )
        )
        logger.info(f"✅ Added Morning Routine: {total_minutes_to_time(morning_start).strftime('%H:%M')}-{total_minutes_to_time(morning_end).strftime('%H:%M')}")
    
    if evening_start < 0:
        evening_start_previous_day = evening_start + 1440
        logger.info(f"ℹ️ Evening routine crosses midnight: splits into two blocks")
        logger.info(f"   Block 1 (today): {total_minutes_to_time(evening_start_previous_day).strftime('%H:%M')}-24:00")
        logger.info(f"   Block 2 (tomorrow morning): 00:00-{total_minutes_to_time(evening_end).strftime('%H:%M')}")
        
        solver_events.append(
            FixedEventInterval(
                id="evening_routine_today",
                start_minutes=evening_start_previous_day,
                end_minutes=1440,
                name="Evening Routine"
            )
        )
        logger.info(f"✅ Added Evening Routine (today): {total_minutes_to_time(evening_start_previous_day).strftime('%H:%M')}-24:00")
        
        solver_events.append(
            FixedEventInterval(
                id="evening_routine_tomorrow",
                start_minutes=0,
                end_minutes=evening_end,
                name="Evening Routine"
            )
        )
        logger.info(f"✅ Added Evening Routine (tomorrow): 00:00-{total_minutes_to_time(evening_end).strftime('%H:%M')}")
    else:
        solver_events.append(
            FixedEventInterval(
                id="evening_routine",
                start_minutes=evening_start,
                end_minutes=evening_end,
                name="Evening Routine"
            )
        )
        logger.info(f"✅ Added Evening Routine: {total_minutes_to_time(evening_start).strftime('%H:%M')}-{total_minutes_to_time(evening_end).strftime('%H:%M')}")


def _add_lunch_block_as_fixed_event(
    solver_events: List[FixedEventInterval],
    sleep_metrics: "SleepMetrics",
    preferences: dict
) -> None:
    """
    Adds lunch as fixed event using work-aware intelligent placement.
    
    SMART PRIORITY SYSTEM:
    1. Right before work/commute (if within 2h and slot is free)
    2. Ideal window (12:00-15:00 adjusted by wake time)
    3. After earliest afternoon event (realistic fallback)
    4. Best available gap (12:00-18:00)
    
    Educational Note:
        Work-aware scheduling: Lunch timing adapts to work schedule.
        - Work 09:00 → Lunch 12:00 (ideal window, work is early)
        - Work 14:00 → Lunch 13:00 (right before, optimal timing)
        - Work 18:00 → Lunch 12:00 (ideal window, work is late)
        
        Maximum 2-hour gap between lunch and work ensures energy levels.
        This prevents both too-early lunches (11:30 when work is 14:00)
        and maintains health-conscious eating patterns.
    """
    if not preferences:
        return
    
    meals = preferences.get("meals", {})
    lunch_duration = meals.get("lunch_duration_minutes", 30)
    wake_min = time_to_total_minutes(sleep_metrics.ideal_wake_time)
    
    lunch_start = _find_lunch_start_for_solver(
        solver_events, lunch_duration, wake_min
    )
    lunch_end = lunch_start + lunch_duration
    
    solver_events.append(
        FixedEventInterval(
            id="lunch",
            start_minutes=lunch_start,
            end_minutes=lunch_end,
            name="Lunch"
        )
    )
    logger.info(f"🍽️ Added lunch: {total_minutes_to_time(lunch_start).strftime('%H:%M')}-{total_minutes_to_time(lunch_end).strftime('%H:%M')}")


def _find_lunch_start_for_solver(events, duration: int, wake_time: int) -> int:
    """
    Finds optimal lunch start time with intelligent work-aware placement.
    
    SMART STRATEGY:
    1. If work/commute exists: Check if lunch fits RIGHT BEFORE (within 2h window)
    2. If yes: Place lunch immediately before commute/work
    3. If no: Use ideal window 12:00-15:00
    4. Fallback: Best available gap 12:00-18:00
    
    Educational Note:
        TIMING MATTERS: Lunch at 13:00 before 14:00 work is better than 11:30.
        System detects work commitments and places lunch optimally:
        - Work at 09:00 → Lunch 12:00-13:00 (ideal window)
        - Work at 14:00 → Lunch 13:00-13:45 (right before work)
        Maximum gap: 2 hours between lunch and work for practical eating.
    """
    ideal_start, ideal_end = _calculate_ideal_lunch_window_solver(wake_time)
    
    logger.info(f"🍽️ Finding lunch placement (duration: {duration}min)")
    logger.info(f"   Wake time: {wake_time}min → Ideal window: {ideal_start}-{ideal_end}min")
    
    work_start = _find_work_start_in_events(events)
    
    if work_start:
        lunch_before_work = work_start - duration
        time_gap = work_start - lunch_before_work
        max_gap_before_work = 120
        
        logger.info(f"   Work starts at: {work_start}min ({total_minutes_to_time(work_start).strftime('%H:%M')})")
        logger.info(f"   Potential lunch slot: {lunch_before_work}min ({total_minutes_to_time(lunch_before_work).strftime('%H:%M')})")
        
        if lunch_before_work >= 720 and lunch_before_work <= 1080:
            if _is_slot_free_solver(events, lunch_before_work, work_start):
                if time_gap <= max_gap_before_work:
                    logger.info(f"✅ PRIORITY 1: Lunch right before work → {lunch_before_work}min ({total_minutes_to_time(lunch_before_work).strftime('%H:%M')})")
                    return lunch_before_work
                else:
                    logger.info(f"⚠️ Gap to work too large ({time_gap}min > {max_gap_before_work}min), checking ideal window...")
    
    lunch_slot = _find_gap_in_window_solver(events, ideal_start, ideal_end, duration)
    if lunch_slot is not None:
        logger.info(f"✅ PRIORITY 2: Lunch in ideal window → {lunch_slot}min ({total_minutes_to_time(lunch_slot).strftime('%H:%M')})")
        return lunch_slot
    
    logger.info("⚠️ PRIORITY 2 failed: Finding gap after earliest afternoon event...")
    lunch_slot = _find_gap_after_noon_event(events, duration)
    if lunch_slot and lunch_slot <= 1080:
        logger.info(f"✅ PRIORITY 3: Lunch after afternoon event → {lunch_slot}min ({total_minutes_to_time(lunch_slot).strftime('%H:%M')})")
        return lunch_slot
    
    logger.info("⚠️ PRIORITY 3 failed: Using best available gap (12:00-18:00)...")
    best_gap = _find_best_gap_in_range_solver(events, duration, 720, 1080)
    logger.info(f"✅ FALLBACK: Lunch in best gap → {best_gap}min ({total_minutes_to_time(best_gap).strftime('%H:%M')})")
    return best_gap


def _calculate_ideal_lunch_window_solver(wake_time: int) -> tuple:
    """Calculates ideal lunch window based on wake time."""
    if wake_time < 7 * 60:
        return (690, 870)
    elif wake_time > 10 * 60:
        return (750, 930)
    return (720, 900)


def _find_gap_in_window_solver(events, window_start: int, window_end: int, duration: int):
    """Finds suitable gap within time window."""
    gaps = _extract_gaps_solver(events, window_start, window_end)
    for gap_start, gap_end in gaps:
        if (gap_end - gap_start) >= duration:
            return gap_start
    return None


def _extract_gaps_solver(events, range_start: int, range_end: int) -> list:
    """Extracts available gaps in time range."""
    sorted_events = sorted(
        [(e.start_minutes, e.end_minutes) for e in events if e.start_minutes < range_end and e.end_minutes > range_start],
        key=lambda x: x[0]
    )
    
    gaps = []
    current_time = range_start
    
    for event_start, event_end in sorted_events:
        if event_start > current_time:
            gaps.append((current_time, event_start))
        current_time = max(current_time, event_end)
    
    if current_time < range_end:
        gaps.append((current_time, range_end))
    
    return gaps


def _find_work_end_in_events(events) -> Optional[int]:
    """
    Finds work block end time (latest work/commute event).
    
    Returns end time of LAST work-related event (e.g., "commute from work").
    This ensures lunch is placed AFTER work, not during commute to work.
    """
    work_events = [e for e in events if "work" in e.name.lower() or "commute" in e.name.lower()]
    if not work_events:
        return None
    latest_event = max(work_events, key=lambda e: e.end_minutes)
    return latest_event.end_minutes


def _find_work_start_in_events(events) -> Optional[int]:
    """
    Finds work block start time (earliest work/commute event).
    
    Educational Note:
        Detects when work starts late (after 15:00) to trigger
        lunch-before-work strategy for health-conscious scheduling.
    """
    work_events = [e for e in events if "work" in e.name.lower() or "commute" in e.name.lower()]
    if not work_events:
        return None
    earliest_event = min(work_events, key=lambda e: e.start_minutes)
    return earliest_event.start_minutes


def _find_gap_after_noon_event(events, duration: int) -> Optional[int]:
    """
    Finds gap after first major event ending after 12:00.
    
    Educational Note:
        For schedules with afternoon commitments, places lunch
        immediately after first event (e.g., morning meeting ends
        at 13:00, lunch 13:00-13:45).
    """
    afternoon_events = [
        e for e in events 
        if e.end_minutes >= 720 and e.end_minutes <= 1080
        and "sleep" not in e.id.lower()
        and "evening" not in e.id.lower()
    ]
    
    if not afternoon_events:
        return None
    
    earliest_afternoon = min(afternoon_events, key=lambda e: e.end_minutes)
    potential_start = earliest_afternoon.end_minutes
    
    if _is_slot_free_solver(events, potential_start, potential_start + duration):
        return potential_start
    
    return None


def _find_best_gap_in_range_solver(
    events, duration: int, range_start: int, range_end: int
) -> int:
    """
    Finds best available gap for lunch within specific time range.
    
    Educational Note:
        Constrains search to healthy eating window (12:00-18:00).
        Prefers gaps closest to noon (12:00) for optimal digestion.
    """
    all_gaps = _extract_gaps_solver(events, range_start, range_end)
    suitable_gaps = [(s, e) for s, e in all_gaps if (e - s) >= duration]
    
    if not suitable_gaps:
        return range_start
    
    noon = 720
    best_gap = min(suitable_gaps, key=lambda g: abs((g[0] + g[1]) // 2 - noon))
    return best_gap[0]


def _is_slot_free_solver(events, slot_start: int, slot_end: int) -> bool:
    """Checks if time slot is free."""
    for event in events:
        if not (slot_end <= event.start_minutes or slot_start >= event.end_minutes):
            return False
    return True


def _add_sleep_windows_to_events(
    solver_events: List[FixedEventInterval],
    sleep_metrics: "SleepMetrics",
    earliest_event_start: Optional[int]
) -> None:
    """
    Adds BOTH sleep windows (previous night + upcoming night) as fixed events.
    
    CRITICAL SLEEP ONSET HANDLING:
        sleep_metrics.ideal_duration = ACTUAL SLEEP TIME (without 15min onset)
        sleep_metrics.ideal_bedtime = ALREADY INCLUDES 15min onset in calculation
        
        Example for 9h sleep need:
        - ideal_duration = 540min (9h actual sleep)
        - bedtime 20:45 → wake 06:00 = 555min total time in bed
        - 555min = 540min sleep + 15min onset
        
        To calculate correct sleep windows, we must ADD 15min onset to duration:
        - total_time_in_bed = 540min + 15min = 555min
        - previous_night = 555min - 195min = 360min (ends at 06:00) ✅
        - NOT 540min - 195min = 345min (ends at 05:45) ❌
    
    Educational Note:
        Schedule must account for TWO sleep periods:
        1. Previous night: Can extend BEFORE 00:00 (e.g., 22:00 yesterday → 07:00 today)
        2. Upcoming night: Can extend AFTER 24:00 (e.g., 23:00 today → 07:00 tomorrow)
        
        Sleep windows are NOT constrained to 00:00-24:00 boundary, allowing
        realistic sleep patterns that span across days.
    """
    sleep_bed_min = time_to_total_minutes(sleep_metrics.ideal_bedtime)
    sleep_wake_min = time_to_total_minutes(sleep_metrics.ideal_wake_time)
    actual_sleep_duration_min = int(sleep_metrics.ideal_duration.total_seconds() / 60)
    sleep_onset_min = 15
    total_time_in_bed_min = actual_sleep_duration_min + sleep_onset_min
    
    logger.info(f"🛏️ SLEEP WINDOW CALCULATION:")
    logger.info(f"   Actual sleep duration: {actual_sleep_duration_min}min ({actual_sleep_duration_min/60:.1f}h)")
    logger.info(f"   Sleep onset time: {sleep_onset_min}min")
    logger.info(f"   Total time in bed: {total_time_in_bed_min}min ({total_time_in_bed_min/60:.2f}h)")
    logger.info(f"   Bedtime: {total_minutes_to_time(sleep_bed_min).strftime('%H:%M')}")
    logger.info(f"   Wake time: {total_minutes_to_time(sleep_wake_min).strftime('%H:%M')}")
    
    _validate_sleep_duration_after_adjustments(
        sleep_bed_min, sleep_wake_min, total_time_in_bed_min
    )
    
    _add_previous_night_sleep_window(
        solver_events, sleep_bed_min, sleep_wake_min, total_time_in_bed_min
    )
    _add_upcoming_night_sleep_window(
        solver_events, sleep_bed_min, sleep_wake_min, total_time_in_bed_min
    )
    
    logger.info(f"🔍 SOLVER_PREP DEBUG: Total solver_events after sleep windows: {len(solver_events)}")
    for event in solver_events:
        if "sleep" in event.id:
            logger.info(f"   Sleep event: {event.id}, start={event.start_minutes}, end={event.end_minutes}")


def _validate_sleep_duration_after_adjustments(
    bed_min: int,
    wake_min: int,
    required_duration: int
) -> None:
    """
    Validates that sleep window provides sufficient duration.
    
    Educational Note:
        This validates total time in bed INCLUDING sleep onset.
        required_duration already includes onset (actual_sleep + 15min).
        
        Calculation handles day wraparound:
        - Normal: bed 22:15 (1335) → wake 06:00 (360)
          Duration = (1440-1335) + 360 = 465min actual sleep
          Total in bed = 465 + 15 onset = 480min
        
        Minimum acceptable: 5 hours (300min) actual sleep
        Warning threshold: 30min deficit from required
    """
    actual_sleep_duration = (1440 - bed_min) + wake_min if bed_min >= wake_min else wake_min - bed_min
    required_sleep_only = required_duration - 15
    
    if actual_sleep_duration < required_sleep_only:
        deficit = required_sleep_only - actual_sleep_duration
        deficit_hours = deficit / 60
        
        logger.error(
            f"❌ CRITICAL SLEEP DEFICIT: After adjusting for conflicts, "
            f"actual sleep is {actual_sleep_duration} minutes ({actual_sleep_duration/60:.1f}h), "
            f"but {required_sleep_only} minutes ({required_sleep_only/60:.1f}h) required. "
            f"Deficit: {deficit} minutes ({deficit_hours:.1f}h)!"
        )
        
        if actual_sleep_duration < 300:
            logger.error(
                f"❌ DANGEROUS: Sleep duration below 5 hours! "
                f"User needs to reschedule fixed events or adjust sleep preferences."
            )
    
    elif actual_sleep_duration < required_sleep_only - 30:
        deficit = required_sleep_only - actual_sleep_duration
        logger.warning(
            f"⚠️ SLEEP WARNING: Sleep duration reduced by {deficit} minutes "
            f"({deficit/60:.1f}h) due to conflicts with fixed events."
        )


def _add_previous_night_sleep_window(
    solver_events: List[FixedEventInterval],
    bed_min: int,
    wake_min: int,
    duration_min: int
) -> None:
    """
    Adds previous night sleep window (can extend before 00:00).
    
    Educational Note:
        Schedule ALWAYS needs previous night sleep block ending at wake time.
        
        Two critical cases:
        1. Normal: bed 23:00 → wake 07:00
           Previous night: 00:00-07:00 (morning portion)
           Upcoming night: 23:00-24:00 (evening portion)
           
        2. Late bedtime: bed 01:15 → wake 07:15 (SAME DAY)
           Previous night: 01:15-07:15 (STARTS at bedtime, not 00:00)
           Upcoming night: SKIPPED (to avoid overlap)
           Evening routine: 00:30-01:15 (before sleep, separate block)
           
        CRITICAL: When bed_min < wake_min, sleep MUST start FROM bed_min
        to avoid overlap with evening routine which ends AT bed_min.
    """
    if bed_min < wake_min:
        sleep_start = bed_min
        sleep_end = wake_min
        logger.info(f"⏰ Previous night sleep: {total_minutes_to_time(bed_min).strftime('%H:%M')}-{total_minutes_to_time(wake_min).strftime('%H:%M')} (late bedtime, starts at bedtime not 00:00)")
    else:
        sleep_start = 0
        sleep_end = wake_min
        logger.info(f"⏰ Previous night sleep: 00:00-{total_minutes_to_time(sleep_end).strftime('%H:%M')} ({sleep_end}min morning portion)")
    
    solver_events.append(
        FixedEventInterval(
            id="sleep_previous_night",
            start_minutes=sleep_start,
            end_minutes=sleep_end
        )
    )


def _add_upcoming_night_sleep_window(
    solver_events: List[FixedEventInterval],
    bed_min: int,
    wake_min: int,
    duration_min: int
) -> None:
    """
    Adds upcoming night sleep window (can extend after 24:00).
    
    Educational Note:
        Schedule ALWAYS needs upcoming night sleep block for today's evening.
        This reserves time for tonight's sleep preparation and sleep itself.
        
        Critical distinction:
        1. Normal: bed 23:00 → wake 07:00 next day
           Upcoming night: 23:00-24:00 (end of today)
           
        2. Late bedtime: bed 01:15 → wake 07:15
           Upcoming night: DO NOT ADD for today (would conflict with previous_night)
           Instead, tonight's evening routine (00:30-01:15) is already added as fixed event
           Tomorrow's schedule will have its own previous_night sleep block
    """
    if bed_min >= wake_min:
        logger.info(f"⏰ Upcoming night sleep: {total_minutes_to_time(bed_min).strftime('%H:%M')}-24:00")
        solver_events.append(
            FixedEventInterval(
                id="sleep_upcoming_night",
                start_minutes=bed_min,
                end_minutes=1440
            )
        )
    else:
        logger.info(f"⏰ Bedtime after midnight (bed={total_minutes_to_time(bed_min).strftime('%H:%M')} < wake={total_minutes_to_time(wake_min).strftime('%H:%M')}), skipping upcoming_night to avoid overlap with previous_night")


def _check_fixed_events_overlaps(
    events: List[FixedEventInterval]
) -> None:
    """
    Checks if any fixed events overlap with each other.
    
    Educational Note:
        Overlapping fixed events indicate scheduling conflicts that
        are physically impossible to resolve. User must modify their
        commitments before schedule can be generated.
        
        Example conflict: Meeting 14:00-15:00 + Gym 14:30-16:00
        → User must reschedule one of these events
    """
    sorted_events = sorted(events, key=lambda x: x.start_minutes)
    
    for i in range(len(sorted_events) - 1):
        current = sorted_events[i]
        next_event = sorted_events[i + 1]
        
        if current.end_minutes > next_event.start_minutes:
            overlap_minutes = current.end_minutes - next_event.start_minutes
            
            logger.error(
                f"❌ FIXED EVENT OVERLAP: '{current.name or current.id}' "
                f"({total_minutes_to_time(current.start_minutes).strftime('%H:%M')}-"
                f"{total_minutes_to_time(current.end_minutes).strftime('%H:%M')}) "
                f"overlaps with '{next_event.name or next_event.id}' "
                f"({total_minutes_to_time(next_event.start_minutes).strftime('%H:%M')}-"
                f"{total_minutes_to_time(next_event.end_minutes).strftime('%H:%M')}) "
                f"by {overlap_minutes} minutes. Please reschedule one of these events!"
            )


def _convert_solver_events_to_dicts(
    solver_events: List[FixedEventInterval]
) -> List[dict]:
    """
    Converts solver FixedEventInterval objects to dict format for LLM.
    
    Educational Note:
        LLM needs to see ALL fixed events including routines, lunch,
        and sleep windows that solver added as constraints.
        
        Excludes sleep windows (handled separately by sleep_corrector).
    """
    result = []
    for event in solver_events:
        if "sleep" in event.id.lower():
            continue
        
        result.append({
            "id": event.id,
            "name": event.name or event.id,
            "start_time": total_minutes_to_time(event.start_minutes).strftime("%H:%M:%S"),
            "end_time": total_minutes_to_time(event.end_minutes).strftime("%H:%M:%S")
        })
    
    return result


def _create_adjusted_sleep_metrics(
    original_metrics: "SleepMetrics",
    wake_minutes: int,
    bedtime_minutes: int
) -> "SleepMetrics":
    """
    Creates new SleepMetrics with adjusted wake and bedtime.
    
    Educational Note:
        Preserves original sleep need/duration but updates actual
        wake/bed times based on adaptive calculation.
    """
    from src.core.sleep import SleepMetrics
    
    wake_time = total_minutes_to_time(wake_minutes)
    bedtime_time = total_minutes_to_time(bedtime_minutes)
    
    if bedtime_minutes > wake_minutes:
        duration_minutes = (wake_minutes + 1440) - bedtime_minutes
    else:
        duration_minutes = wake_minutes - bedtime_minutes
    
    duration = timedelta(minutes=duration_minutes)
    
    return SleepMetrics(
        ideal_bedtime=bedtime_time,
        ideal_wake_time=wake_time,
        ideal_duration=duration
    )







