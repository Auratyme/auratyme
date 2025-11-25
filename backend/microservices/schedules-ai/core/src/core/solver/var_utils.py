"""
Variable Dictionary Utilities.

Helper functions for extracting specific variable types from the nested
dictionary structure returned by variable creation.

Educational Context:
    The variable creation process returns a dictionary mapping task IDs to
    dictionaries containing 'start', 'end', and 'interval' variables. These
    helpers make it easy to extract just the type you need for different
    constraint types.
"""

from typing import Dict, List
from uuid import UUID

try:
    from ortools.sat.python import cp_model
except ImportError:
    pass


def extract_interval_variables(
    task_vars: Dict[UUID, Dict]
) -> List[cp_model.IntervalVar]:
    """
    Extracts interval variables for NoOverlap constraints.

    Educational Note:
        NoOverlap constraint needs only interval variables. This helper
        extracts them from the full dictionary, discarding start/end vars.
    """
    return [vars_dict['interval'] for vars_dict in task_vars.values()]


def extract_start_variables(
    task_vars: Dict[UUID, Dict]
) -> Dict[UUID, cp_model.IntVar]:
    """
    Extracts start time variables indexed by task ID.

    Educational Note:
        Dependencies need to reference specific task start times. This
        dictionary makes it O(1) to look up any task's start variable.
    """
    return {task_id: vars_dict['start'] for task_id, vars_dict in task_vars.items()}


def extract_end_variables(
    task_vars: Dict[UUID, Dict]
) -> Dict[UUID, cp_model.IntVar]:
    """
    Extracts end time variables indexed by task ID.

    Educational Note:
        Dependencies reference when tasks end. Parallel structure to
        extract_start_variables maintains consistency.
    """
    return {task_id: vars_dict['end'] for task_id, vars_dict in task_vars.items()}
