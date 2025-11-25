"""
CP-SAT Variable Creation Utilities.

Creates decision variables for the constraint satisfaction programming solver.
Variables represent the decisions the solver must make: when should each task
start and end?

Educational Context:
    In CP-SAT, variables represent unknowns that the solver must determine.
    Each task gets three related variables: start time, end time, and an
    interval connecting them. Proper variable bounds are critical for solver
    performance - tight bounds prune the search space dramatically.
"""

import logging
from typing import Dict
from uuid import UUID

try:
    from ortools.sat.python import cp_model
    ORTOOLS_AVAILABLE = True
except ImportError:
    ORTOOLS_AVAILABLE = False

from .models import SolverTask

logger = logging.getLogger(__name__)


def create_task_start_variable(
    model: cp_model.CpModel,
    task: SolverTask,
    earliest: int,
    latest: int
) -> cp_model.IntVar:
    """
    Creates variable representing when a task can start.

    Args:
        model: OR-Tools CP model instance
        task: Task requiring start time variable
        earliest: Earliest possible start minute
        latest: Latest possible start minute

    Returns:
        Integer variable bounded by feasible start times

    Educational Note:
        Variable bounds define the search space. Tighter bounds (smaller
        range) mean faster solving. We calculate the latest possible start
        as latest_end - duration, ensuring the task can actually fit.
    """
    return model.NewIntVar(earliest, latest, f'start_{task.id}')


def create_task_end_variable(
    model: cp_model.CpModel,
    task: SolverTask,
    earliest: int,
    latest: int
) -> cp_model.IntVar:
    """
    Creates variable representing when a task ends.

    Args:
        model: OR-Tools CP model instance
        task: Task requiring end time variable
        earliest: Earliest possible end minute
        latest: Latest possible end minute

    Returns:
        Integer variable bounded by feasible end times

    Educational Note:
        End time is constrained by both start time and duration. The
        earliest possible end is earliest_start + duration.
    """
    return model.NewIntVar(earliest, latest, f'end_{task.id}')


def create_task_interval_variable(
    model: cp_model.CpModel,
    task: SolverTask,
    start_var: cp_model.IntVar,
    end_var: cp_model.IntVar
) -> cp_model.IntervalVar:
    """
    Creates interval variable linking start and end.

    Args:
        model: OR-Tools CP model instance
        task: Task requiring interval variable
        start_var: Previously created start variable
        end_var: Previously created end variable

    Returns:
        Interval variable enforcing start + duration = end

    Educational Note:
        Interval variables in CP-SAT automatically enforce the relationship
        start + duration = end. This is more efficient than adding an
        explicit constraint, as the solver can use specialized algorithms.
    """
    return model.NewIntervalVar(
        start_var,
        task.duration_minutes,
        end_var,
        f'interval_{task.id}'
    )


def create_optional_task_interval(
    model: cp_model.CpModel,
    task: SolverTask,
    start_var: cp_model.IntVar,
    end_var: cp_model.IntVar,
    is_scheduled: cp_model.IntVar
) -> cp_model.IntervalVar:
    """
    Creates optional interval that can be excluded from schedule.

    Educational Note:
        Optional intervals allow solver to skip tasks when constraints
        make full scheduling impossible. The is_scheduled boolean controls
        whether this interval participates in NoOverlap constraint.
    """
    return model.NewOptionalIntervalVar(
        start_var,
        task.duration_minutes,
        end_var,
        is_scheduled,
        f'interval_{task.id}'
    )


def calculate_earliest_start(task: SolverTask, day_start: int) -> int:
    """
    Determines earliest feasible start time for a task.

    Educational Note:
        Takes maximum of day start and task's explicit earliest start
        constraint. This respects both global and task-specific boundaries.
    """
    return max(day_start, task.earliest_start_minutes or 0)


def calculate_latest_end(task: SolverTask, day_end: int) -> int:
    """
    Determines latest feasible end time for a task.

    Educational Note:
        Takes minimum of day end and task's explicit latest end constraint.
        This ensures tasks fit within both global and task-specific limits.
    """
    return min(day_end, task.latest_end_minutes or day_end)


def calculate_latest_start(latest_end: int, duration: int) -> int:
    """
    Calculates latest possible start given end constraint.

    Educational Note:
        Working backwards: if task must end by latest_end and takes
        duration minutes, it must start by latest_end - duration.
    """
    return latest_end - duration


def calculate_earliest_end(earliest_start: int, duration: int) -> int:
    """
    Calculates earliest possible end given start constraint.

    Educational Note:
        Working forwards: if task starts at earliest_start and takes
        duration minutes, it ends at earliest_start + duration.
    """
    return earliest_start + duration


def create_task_variables(
    model: cp_model.CpModel,
    task: SolverTask,
    day_start: int,
    day_end: int
) -> Dict[str, any]:
    """
    Creates all variables needed for one task including optional scheduling.

    Returns:
        Dictionary with keys 'start', 'end', 'interval', 'is_scheduled'

    Educational Note:
        Optional intervals allow solver to skip low-priority tasks when
        space is limited. Each task gets a boolean 'is_scheduled' variable
        that the solver can set to false to exclude the task.
    """
    earliest_start = calculate_earliest_start(task, day_start)
    latest_end = calculate_latest_end(task, day_end)
    latest_start = calculate_latest_start(latest_end, task.duration_minutes)
    earliest_end = calculate_earliest_end(earliest_start, task.duration_minutes)
    
    logger.info(f"🔍 TASK VARIABLE: {task.id}, duration={task.duration_minutes}min")
    logger.info(f"   Start bounds: [{earliest_start}, {latest_start}]")
    logger.info(f"   End bounds: [{earliest_end}, {latest_end}]")
    
    if latest_start < earliest_start:
        logger.error(f"❌ IMPOSSIBLE CONSTRAINT: Task {task.id} latest_start ({latest_start}) < earliest_start ({earliest_start})")
    
    is_scheduled = model.NewBoolVar(f'scheduled_{task.id}')
    start_var = create_task_start_variable(model, task, earliest_start, latest_start)
    end_var = create_task_end_variable(model, task, earliest_end, latest_end)
    interval_var = create_optional_task_interval(model, task, start_var, end_var, is_scheduled)
    
    return {
        'start': start_var,
        'end': end_var,
        'interval': interval_var,
        'is_scheduled': is_scheduled
    }
