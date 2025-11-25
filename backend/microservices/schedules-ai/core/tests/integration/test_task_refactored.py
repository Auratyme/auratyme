"""
Integration test comparing old task_prioritizer with new task package.

Verifies refactored modules produce identical results to original implementation.
"""

import logging
from datetime import datetime, timedelta, timezone
from uuid import uuid4

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_old_module():
    """Test old task_prioritizer module."""
    logger.info("=" * 60)
    logger.info("Testing OLD task_prioritizer.py module")
    logger.info("=" * 60)
    
    from src.core.task_prioritizer import (
        Task, TaskPriority, EnergyLevel, TaskPrioritizer
    )
    
    now = datetime.now(timezone.utc)
    
    task1 = Task(
        title="Critical Report",
        priority=TaskPriority.CRITICAL,
        energy_level=EnergyLevel.HIGH,
        duration=timedelta(hours=2),
        deadline=now + timedelta(hours=4)
    )
    
    task2 = Task(
        title="Code Review",
        priority=TaskPriority.HIGH,
        energy_level=EnergyLevel.MEDIUM,
        duration=timedelta(hours=1),
        dependencies={task1.id}
    )
    
    task3 = Task(
        title="Emails",
        priority=TaskPriority.MEDIUM,
        energy_level=EnergyLevel.LOW,
        duration=timedelta(minutes=30)
    )
    
    tasks = [task3, task1, task2]  # Deliberately unsorted
    
    prioritizer = TaskPrioritizer()
    prioritized = prioritizer.prioritize(tasks, now)
    
    logger.info(f"✅ Old module: {len(prioritized)} tasks prioritized")
    for i, task in enumerate(prioritized):
        urgency = task.time_urgency_factor(now)
        logger.info(f"  {i+1}. {task.title} (prio={task.priority.name}, urgency={urgency:.2f})")
    
    return prioritized, task1, task2, task3


def test_new_module():
    """Test new task package modules."""
    logger.info("\n" + "=" * 60)
    logger.info("Testing NEW task package modules")
    logger.info("=" * 60)
    
    from src.core.task import (
        Task, TaskPriority, EnergyLevel, TaskPrioritizer
    )
    
    now = datetime.now(timezone.utc)
    
    task1 = Task(
        title="Critical Report",
        priority=TaskPriority.CRITICAL,
        energy_level=EnergyLevel.HIGH,
        duration=timedelta(hours=2),
        deadline=now + timedelta(hours=4)
    )
    
    task2 = Task(
        title="Code Review",
        priority=TaskPriority.HIGH,
        energy_level=EnergyLevel.MEDIUM,
        duration=timedelta(hours=1),
        dependencies={task1.id}
    )
    
    task3 = Task(
        title="Emails",
        priority=TaskPriority.MEDIUM,
        energy_level=EnergyLevel.LOW,
        duration=timedelta(minutes=30)
    )
    
    tasks = [task3, task1, task2]  # Same order as old test
    
    prioritizer = TaskPrioritizer()
    prioritized = prioritizer.prioritize(tasks, now)
    
    logger.info(f"✅ New module: {len(prioritized)} tasks prioritized")
    for i, task in enumerate(prioritized):
        from src.core.task.urgency import calculate_time_urgency_factor
        urgency = calculate_time_urgency_factor(task, now)
        logger.info(f"  {i+1}. {task.title} (prio={task.priority.name}, urgency={urgency:.2f})")
    
    return prioritized, task1, task2, task3


def compare_results(old_result, new_result):
    """Compare prioritization results."""
    logger.info("\n" + "=" * 60)
    logger.info("COMPARISON")
    logger.info("=" * 60)
    
    old_tasks, old_t1, old_t2, old_t3 = old_result
    new_tasks, new_t1, new_t2, new_t3 = new_result
    
    if len(old_tasks) != len(new_tasks):
        logger.error(f"❌ Different lengths: old={len(old_tasks)}, new={len(new_tasks)}")
        return False
    
    logger.info(f"✅ Same length: {len(old_tasks)} tasks")
    
    # Compare order
    old_titles = [t.title for t in old_tasks]
    new_titles = [t.title for t in new_tasks]
    
    if old_titles != new_titles:
        logger.error(f"❌ Different order!")
        logger.error(f"  Old: {old_titles}")
        logger.error(f"  New: {new_titles}")
        return False
    
    logger.info(f"✅ Same order: {old_titles}")
    
    # Compare urgency calculations
    from src.core.task.urgency import calculate_time_urgency_factor
    now = datetime.now(timezone.utc)
    
    for old_task, new_task in zip(old_tasks, new_tasks):
        old_urgency = old_task.time_urgency_factor(now)
        new_urgency = calculate_time_urgency_factor(new_task, now)
        
        if abs(old_urgency - new_urgency) > 0.001:
            logger.error(f"❌ Urgency mismatch for '{old_task.title}'")
            logger.error(f"  Old: {old_urgency:.4f}, New: {new_urgency:.4f}")
            return False
    
    logger.info("✅ Urgency calculations match")
    
    # Test Task properties
    if (old_t1.title != new_t1.title or 
        old_t1.priority.value != new_t1.priority.value or
        old_t1.energy_level.value != new_t1.energy_level.value or
        old_t1.duration != new_t1.duration):
        logger.error("❌ Task properties differ")
        return False
    
    logger.info("✅ Task properties match")
    
    # Test mark_complete
    new_t3.mark_complete()
    if not new_t3.completed or new_t3.completion_date is None:
        logger.error("❌ mark_complete() failed")
        return False
    
    logger.info("✅ mark_complete() works")
    
    return True


def test_energy_pattern():
    """Test energy pattern functionality."""
    logger.info("\n" + "=" * 60)
    logger.info("Testing energy pattern")
    logger.info("=" * 60)
    
    from src.core.task import TaskPrioritizer
    
    pattern = {h: 0.5 for h in range(24)}
    pattern.update({9: 0.8, 10: 0.9, 11: 0.8})
    
    prioritizer = TaskPrioritizer(user_energy_pattern=pattern)
    retrieved = prioritizer.get_energy_pattern()
    
    if retrieved[9] != 0.8 or retrieved[10] != 0.9:
        logger.error("❌ Energy pattern mismatch")
        return False
    
    logger.info("✅ Energy pattern works correctly")
    return True


def run_all_tests():
    """Run complete test suite."""
    logger.info("\n" + "=" * 70)
    logger.info("PHASE 2 INTEGRATION TEST: Task Modules Comparison")
    logger.info("=" * 70 + "\n")
    
    try:
        old_result = test_old_module()
        new_result = test_new_module()
        
        if not compare_results(old_result, new_result):
            logger.error("\n❌ TESTS FAILED - Results differ!")
            return False
        
        if not test_energy_pattern():
            logger.error("\n❌ TESTS FAILED - Energy pattern broken!")
            return False
        
        logger.info("\n" + "=" * 70)
        logger.info("✅ ALL TESTS PASSED - Refactored task modules work identically!")
        logger.info("=" * 70)
        return True
        
    except Exception as e:
        logger.error(f"\n❌ TEST FAILED with exception: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    import sys
    success = run_all_tests()
    sys.exit(0 if success else 1)
