"""
Constraint Definitions for Schedule Solver.

Encodes scheduling business rules as mathematical constraints that the CP-SAT
solver must satisfy. Constraints transform human scheduling rules into formal
logic the solver can reason about.

Educational Context:
    Constraints encode "business rules" in mathematical form. In scheduling:
    - No overlap = physical impossibility (can't do two things at once)
    - Dependencies = logical ordering (must finish A before starting B)
    - Time windows = user preferences (only work certain hours)
    - Fixed events = hard commitments (unmovable meetings)
    
    Well-designed constraints make problems easier to solve by pruning the
    search space early.
"""

import logging
from typing import Dict, List
from uuid import UUID

try:
    from ortools.sat.python import cp_model
except ImportError:
    pass

from .models import FixedEventInterval, SolverTask

logger = logging.getLogger(__name__)


def add_no_overlap_constraint(
    model: cp_model.CpModel,
    interval_vars: List[cp_model.IntervalVar]
) -> None:
    """
    Ensures no two tasks occur simultaneously.

    Args:
        model: OR-Tools CP model to add constraint to
        interval_vars: List of task interval variables

    Educational Note:
        NoOverlap is a global constraint in CP-SAT - it's more efficient
        than creating pairwise constraints (O(n) vs O(n²)). The solver
        uses specialized algorithms for this common pattern.
    """
    model.AddNoOverlap(interval_vars)


def create_fixed_event_interval(
    model: cp_model.CpModel,
    event: FixedEventInterval
) -> cp_model.IntervalVar:
    """
    Converts fixed event to solver interval variable.

    Educational Note:
        Fixed events become interval variables with no degrees of freedom.
        The start and duration are constants, making them immovable anchors
        in the schedule that other tasks must work around.
    """
    duration = event.end_minutes - event.start_minutes
    return model.NewFixedSizeIntervalVar(
        event.start_minutes,
        duration,
        f'fixed_{event.id}'
    )


def clip_event_to_day(
    event: FixedEventInterval,
    day_start: int,
    day_end: int
) -> tuple:
    """
    Adjusts event boundaries to fit within scheduling day.

    Returns:
        Tuple of (clipped_start, clipped_end)

    Educational Note:
        Events might extend beyond the scheduling window (e.g., overnight
        shift ending at 2am). Clipping ensures we only model the portion
        within our scheduling horizon.
    """
    clipped_start = max(day_start, event.start_minutes)
    clipped_end = min(day_end, event.end_minutes)
    return clipped_start, clipped_end


def calculate_event_duration(start: int, end: int) -> int:
    """
    Computes duration of clipped event.

    Educational Note:
        After clipping to day boundaries, duration might be zero (event
        entirely outside window) or reduced (event partially overlaps).
    """
    return end - start


def should_include_event(duration: int) -> bool:
    """
    Determines if event has meaningful duration.

    Educational Note:
        Zero-duration events are mathematical artifacts from clipping and
        should be excluded to keep the model clean.
    """
    return duration > 0


def add_fixed_events_constraint(
    model: cp_model.CpModel,
    task_intervals: List[cp_model.IntervalVar],
    fixed_events: List[FixedEventInterval],
    day_start: int,
    day_end: int
) -> None:
    """
    Prevents tasks from overlapping with fixed events.

    Educational Note:
        We convert fixed events to interval variables, then use the same
        NoOverlap constraint. OR-Tools CP-SAT handles touching intervals
        (event1.end == event2.start) correctly without overlap detection.
        Buffer caused more problems than it solved by creating artificial overlaps.
    """
    all_intervals = task_intervals.copy()
    
    for event in fixed_events:
        clipped_start, clipped_end = clip_event_to_day(event, day_start, day_end)
        duration = calculate_event_duration(clipped_start, clipped_end)
        
        if should_include_event(duration):
            fixed_interval = create_fixed_event_interval_with_duration(
                model,
                event.id,
                clipped_start,
                duration
            )
            all_intervals.append(fixed_interval)
    
    model.AddNoOverlap(all_intervals)


def create_fixed_event_interval_with_duration(
    model: cp_model.CpModel,
    event_id: str,
    start: int,
    duration: int
) -> cp_model.IntervalVar:
    """
    Creates fixed interval with explicit duration.

    Educational Note:
        This helper exists to keep add_fixed_events_constraint under 5 lines.
        Small focused functions improve testability and readability.
    """
    return model.NewFixedSizeIntervalVar(start, duration, f'fixed_{event_id}')


def add_dependency_constraint(
    model: cp_model.CpModel,
    task_start: cp_model.IntVar,
    dependency_end: cp_model.IntVar
) -> None:
    """
    Enforces one task must finish before another starts.

    Educational Note:
        Dependency constraints encode logical ordering. If task B depends
        on task A, then start_B >= end_A. This is a simple linear constraint
        that CP-SAT handles efficiently.
    """
    model.Add(task_start >= dependency_end)


def task_has_dependencies(task: SolverTask) -> bool:
    """
    Checks if task has any dependencies defined.

    Educational Note:
        Guarding against empty dependency lists avoids unnecessary work
        and keeps the model smaller.
    """
    return len(task.dependencies) > 0


def dependency_is_valid(
    dependency_id: UUID,
    task_ends: Dict[UUID, cp_model.IntVar]
) -> bool:
    """
    Verifies dependency task exists in the schedule.

    Educational Note:
        Dependencies might reference tasks not in current scheduling batch
        (e.g., completed yesterday). We skip invalid references rather than
        fail, logging a warning for debugging.
    """
    return dependency_id in task_ends


def add_task_dependencies(
    model: cp_model.CpModel,
    task: SolverTask,
    task_start: cp_model.IntVar,
    task_ends: Dict[UUID, cp_model.IntVar]
) -> None:
    """
    Adds all dependency constraints for one task.

    Educational Note:
        Iterating through dependencies and adding individual constraints
        keeps the code simple. CP-SAT will internally optimize how it
        handles these constraints.
    """
    if not task_has_dependencies(task):
        return
        
    for dep_id in task.dependencies:
        if dependency_is_valid(dep_id, task_ends):
            add_dependency_constraint(model, task_start, task_ends[dep_id])
        else:
            logger.warning(f"Dependency {dep_id} not found for task {task.id}")


def add_all_dependencies(
    model: cp_model.CpModel,
    tasks: List[SolverTask],
    task_starts: Dict[UUID, cp_model.IntVar],
    task_ends: Dict[UUID, cp_model.IntVar]
) -> None:
    """
    Processes dependencies for all tasks in the schedule.

    Educational Note:
        Batch processing keeps constraint addition organized. Each task's
        dependencies are added independently, making the code easier to
        understand and debug.
    """
    for task in tasks:
        if task.id in task_starts:
            add_task_dependencies(model, task, task_starts[task.id], task_ends)
