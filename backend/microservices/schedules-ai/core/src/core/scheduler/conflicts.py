"""
Schedule conflict resolution.

This module handles overlapping blocks by applying priority rules
to determine which items should be kept in the final schedule.
"""

import logging
from typing import Any, Dict, List, Tuple

logger = logging.getLogger(__name__)


def resolve_schedule_conflicts(
    blocks: List[Tuple[int, int, Dict[str, Any]]]
) -> List[Tuple[int, int, Dict[str, Any]]]:
    """
    Resolves overlapping blocks using priority system.
    
    Educational Note:
        Priority order: fixed_event > task > meal > routine > activity > break.
        Higher priority items replace lower priority ones when overlapping.
    """
    priority_order = {
        "sleep": 6,
        "fixed_event": 5,
        "task": 4,
        "meal": 3,
        "routine": 2,
        "activity": 1,
        "break": 0
    }
    
    non_overlapping = []
    
    for start, end, meta in blocks:
        add_or_replace_conflicting_block(
            non_overlapping, start, end, meta, priority_order
        )
    
    non_overlapping.sort(key=lambda x: x[0])
    return non_overlapping


def add_or_replace_conflicting_block(
    non_overlapping: List[Tuple[int, int, Dict[str, Any]]],
    start: int,
    end: int,
    meta: Dict[str, Any],
    priority_order: Dict[str, int]
) -> None:
    """
    Adds block or replaces existing lower-priority overlapping block.
    
    Educational Note:
        Checks each existing block for overlap. If overlap found,
        compares priorities and keeps higher-priority item.
    """
    current_priority = priority_order.get(meta.get("type", "break"), 0)
    
    for idx, (existing_start, existing_end, existing_meta) in enumerate(non_overlapping):
        if blocks_overlap(start, end, existing_start, existing_end):
            existing_priority = priority_order.get(
                existing_meta.get("type", "break"), 0
            )
            
            if current_priority > existing_priority:
                non_overlapping[idx] = (start, end, meta)
            
            return
    
    non_overlapping.append((start, end, meta))


def blocks_overlap(
    start1: int,
    end1: int,
    start2: int,
    end2: int
) -> bool:
    """
    Checks if two time blocks overlap.
    
    Educational Note:
        Two blocks overlap if their ranges intersect.
        max(starts) < min(ends) is efficient overlap detection.
    """
    return max(start1, start2) < min(end1, end2)
