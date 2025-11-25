"""
Core schedule processing and enrichment.

This module takes solver output and enriches it with meals, routines,
activities, and breaks to create a complete daily schedule.
"""

import logging
from typing import Any, Dict, List, TYPE_CHECKING

from src.core.scheduler.blocks import collect_all_schedule_blocks
from src.core.scheduler.conflicts import resolve_schedule_conflicts
from src.core.scheduler.gaps import fill_schedule_gaps_with_breaks

if TYPE_CHECKING:
    from src.core.solver import ScheduledTaskInfo
    from src.core.scheduler.models import ScheduleInputData
    from src.core.sleep import SleepMetrics

logger = logging.getLogger(__name__)


def process_core_schedule(
    core_schedule: List["ScheduledTaskInfo"],
    input_data: "ScheduleInputData",
    sleep_metrics: "SleepMetrics",
    prepare_solver_input_func,
    prepare_profile_func
) -> List[Dict[str, Any]]:
    """
    Formats core solver results and inserts breaks, meals, routines, activities.
    
    Educational Note:
        Converts constraint solver's skeleton (tasks + fixed events)
        into complete schedule by adding meals, routines, activities,
        and filling gaps with appropriate break types.
        
        Three-stage pipeline:
        1. Collect all blocks (tasks, events, meals, routines, activities)
        2. Resolve conflicts using priority system
        3. Fill gaps with appropriate breaks
    """
    blocks = collect_all_schedule_blocks(
        core_schedule, input_data, sleep_metrics,
        prepare_solver_input_func, prepare_profile_func
    )
    
    non_overlapping = resolve_schedule_conflicts(blocks)
    final_schedule = fill_schedule_gaps_with_breaks(non_overlapping)
    
    return final_schedule
