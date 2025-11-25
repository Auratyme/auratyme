"""
Solution Parsing Utilities.

Converts CP-SAT solver results into domain objects that the application
understands. Extracts variable assignments and transforms them into
scheduled task information.

Educational Context:
    Parsing is separated from solving to maintain single responsibility.
    The solver focuses on finding solutions; the parser focuses on
    transforming those solutions into usable formats. This separation
    makes both easier to test and understand.
"""

import logging
from typing import Dict, List, Optional
from uuid import UUID

try:
    from ortools.sat.python import cp_model
except ImportError:
    pass

try:
    from src.utils.time_utils import total_minutes_to_time
except ImportError:
    from datetime import time
    def total_minutes_to_time(minutes: int) -> time:
        minutes = max(0, min(1439, int(minutes)))
        hours, mins = divmod(minutes, 60)
        return time(hour=hours % 24, minute=mins)

from .models import ScheduledTaskInfo

logger = logging.getLogger(__name__)


def has_solution(status: int) -> bool:
    """
    Checks if solver found a usable solution.

    Educational Note:
        OPTIMAL means best possible solution. FEASIBLE means a good
        solution but maybe not the best (time limit reached). Both
        are usable; only difference is optimality guarantee.
    """
    return status == cp_model.OPTIMAL or status == cp_model.FEASIBLE


def extract_task_start_time(
    solver: cp_model.CpSolver,
    vars_dict: Dict
) -> int:
    """
    Gets the scheduled start time in minutes.

    Educational Note:
        solver.Value() returns the assignment the solver made for a variable.
        This is how we extract the solver's decisions.
    """
    return solver.Value(vars_dict['start'])


def extract_task_end_time(
    solver: cp_model.CpSolver,
    vars_dict: Dict
) -> int:
    """
    Gets the scheduled end time in minutes.

    Educational Note:
        End time is derived from start + duration, but we extract it
        directly for clarity and to verify solver consistency.
    """
    return solver.Value(vars_dict['end'])


def create_scheduled_task(
    task_id: UUID,
    start_minutes: int,
    end_minutes: int,
    target_date
) -> ScheduledTaskInfo:
    """
    Constructs scheduled task info from solver results.

    Educational Note:
        Converting minutes to time objects makes the data usable by the
        rest of the application. Minute-based internal representation is
        for solver efficiency; time objects are for human readability.
    """
    return ScheduledTaskInfo(
        task_id=task_id,
        start_time=total_minutes_to_time(start_minutes),
        end_time=total_minutes_to_time(end_minutes),
        task_date=target_date
    )


def try_parse_single_task(
    task_id: UUID,
    solver: cp_model.CpSolver,
    vars_dict: Dict,
    target_date
) -> Optional[ScheduledTaskInfo]:
    """
    Attempts to parse one task from solver solution.

    Returns:
        Scheduled task info or None if parsing fails

    Educational Note:
        Try-except isolates parsing errors. One bad task shouldn't crash
        the entire parsing process. We log the error and continue.
    """
    try:
        start = extract_task_start_time(solver, vars_dict)
        end = extract_task_end_time(solver, vars_dict)
        return create_scheduled_task(task_id, start, end, target_date)
    except Exception as e:
        logger.error(f"Failed to parse task {task_id}: {e}")
        return None


def extract_all_scheduled_tasks(
    solver: cp_model.CpSolver,
    task_vars: Dict[UUID, Dict],
    target_date
) -> List[ScheduledTaskInfo]:
    """
    Extracts all scheduled tasks from solver solution.

    Educational Note:
        With optional tasks, we check is_scheduled boolean before parsing.
        Tasks where is_scheduled=False are skipped (solver decided not to
        include them due to space/priority constraints).
    """
    schedule = []
    skipped_count = 0
    
    for task_id, vars_dict in task_vars.items():
        is_scheduled_var = vars_dict.get('is_scheduled')
        
        if is_scheduled_var is not None:
            if not solver.Value(is_scheduled_var):
                skipped_count += 1
                logger.info(f"⏭️ Task {task_id} not scheduled (solver decision)")
                continue
        
        scheduled_task = try_parse_single_task(
            task_id,
            solver,
            vars_dict,
            target_date
        )
        
        if scheduled_task:
            schedule.append(scheduled_task)
    
    if skipped_count > 0:
        logger.warning(f"⚠️ {skipped_count} tasks skipped due to insufficient space")
    
    return schedule


def sort_schedule_by_time(
    schedule: List[ScheduledTaskInfo]
) -> List[ScheduledTaskInfo]:
    """
    Orders tasks by start time for chronological presentation.

    Educational Note:
        Sorting makes the schedule easier to read and present to users.
        The solver doesn't care about order, but humans do.
    """
    schedule.sort(key=lambda x: x.start_time)
    return schedule


def parse_solution(
    status: int,
    solver: cp_model.CpSolver,
    task_vars: Dict[UUID, Dict],
    target_date
) -> Optional[List[ScheduledTaskInfo]]:
    """
    Converts solver result into scheduled task objects.

    Returns:
        Sorted list of scheduled tasks, or None if no solution

    Educational Note:
        This is the main entry point for parsing. It orchestrates the
        entire parsing process: check status → extract tasks → sort.
        Each step is delegated to a focused helper function.
    """
    if not has_solution(status):
        logger.warning(f"No solution found (status: {status})")
        return None
    
    schedule = extract_all_scheduled_tasks(solver, task_vars, target_date)
    schedule = sort_schedule_by_time(schedule)
    
    logger.info(f"Parsed solution: {len(schedule)} tasks scheduled")
    return schedule
