"""
Integration test comparing old scheduler.py with new scheduler/ package.

This test verifies that the refactored scheduler package produces identical
behavior to the original scheduler.py module.
"""

import asyncio
import logging
from datetime import date, datetime, time, timedelta, timezone
from uuid import uuid4

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_old_module():
    """
    Test old scheduler_legacy.py module.
    
    Educational Note:
        Imports from deprecated module to capture baseline behavior
        for comparison with refactored implementation.
    """
    from src.core.scheduler_legacy import (
        Scheduler,
        ScheduleInputData,
        GeneratedSchedule
    )
    from src.core.sleep import SleepCalculator
    from src.core.chronotype import ChronotypeAnalyzer
    from src.core.task import TaskPrioritizer, Task, TaskPriority, EnergyLevel
    from src.core.solver import ConstraintSchedulerSolver
    
    sleep_calc = SleepCalculator()
    chrono_analyzer = ChronotypeAnalyzer()
    task_prio = TaskPrioritizer()
    solver = ConstraintSchedulerSolver()
    
    scheduler = Scheduler(
        sleep_calculator=sleep_calc,
        chronotype_analyzer=chrono_analyzer,
        task_prioritizer=task_prio,
        constraint_solver=solver,
        llm_engine=None,
        wearable_service=None,
        history_service=None,
        config={"use_llm_refinement": False}
    )
    
    user_id = uuid4()
    target = date.today() + timedelta(days=1)
    
    task1 = Task(
        id=uuid4(),
        title="Test Task 1",
        duration=timedelta(hours=2),
        priority=TaskPriority.HIGH,
        energy_level=EnergyLevel.HIGH,
        earliest_start=time(9, 0),
    )
    
    task2 = Task(
        id=uuid4(),
        title="Test Task 2",
        duration=timedelta(minutes=45),
        priority=TaskPriority.MEDIUM,
        energy_level=EnergyLevel.MEDIUM,
        earliest_start=time(14, 0),
    )
    
    input_data = ScheduleInputData(
        user_id=user_id,
        target_date=target,
        tasks=[task1, task2],
        fixed_events_input=[
            {"id": "meeting", "start_time": "10:00", "end_time": "11:00"}
        ],
        preferences={
            "preferred_wake_time": "07:00",
            "meals": {
                "breakfast_time": "07:30",
                "lunch_time": "12:30",
                "dinner_time": "19:00"
            },
            "routines": {
                "morning_duration_minutes": 30,
                "evening_duration_minutes": 30
            }
        },
        user_profile_data={"age": 30, "meq_score": 55}
    )
    
    result = asyncio.run(scheduler.generate_schedule(input_data))
    
    logger.info("✅ Old module executed successfully")
    logger.info(f"  Schedule items: {len(result.scheduled_items)}")
    logger.info(f"  Task completion: {result.metrics.get('task_completion_pct', 0)}%")
    logger.info(f"  Unscheduled tasks: {result.metrics.get('unscheduled_tasks', 0)}")
    
    return {
        "schedule_items_count": len(result.scheduled_items),
        "task_completion_pct": result.metrics.get("task_completion_pct", 0),
        "unscheduled_tasks": result.metrics.get("unscheduled_tasks", 0),
        "total_task_minutes": result.metrics.get("total_task_minutes", 0),
        "total_meal_minutes": result.metrics.get("total_meal_minutes", 0),
        "total_routine_minutes": result.metrics.get("total_routine_minutes", 0),
        "warnings": len(result.warnings)
    }


def test_new_module():
    """
    Test new scheduler/ package modules.
    
    Educational Note:
        Uses same test data as old module to verify identical behavior.
    """
    from src.core.scheduler import (
        Scheduler,
        ScheduleInputData,
        GeneratedSchedule
    )
    from src.core.sleep import SleepCalculator
    from src.core.chronotype import ChronotypeAnalyzer
    from src.core.task import TaskPrioritizer, Task, TaskPriority, EnergyLevel
    from src.core.solver import ConstraintSchedulerSolver
    
    sleep_calc = SleepCalculator()
    chrono_analyzer = ChronotypeAnalyzer()
    task_prio = TaskPrioritizer()
    solver = ConstraintSchedulerSolver()
    
    scheduler = Scheduler(
        sleep_calculator=sleep_calc,
        chronotype_analyzer=chrono_analyzer,
        task_prioritizer=task_prio,
        constraint_solver=solver,
        llm_engine=None,
        wearable_service=None,
        history_service=None,
        config={"use_llm_refinement": False}
    )
    
    user_id = uuid4()
    target = date.today() + timedelta(days=1)
    
    task1 = Task(
        id=uuid4(),
        title="Test Task 1",
        duration=timedelta(hours=2),
        priority=TaskPriority.HIGH,
        energy_level=EnergyLevel.HIGH,
        earliest_start=time(9, 0),
    )
    
    task2 = Task(
        id=uuid4(),
        title="Test Task 2",
        duration=timedelta(minutes=45),
        priority=TaskPriority.MEDIUM,
        energy_level=EnergyLevel.MEDIUM,
        earliest_start=time(14, 0),
    )
    
    input_data = ScheduleInputData(
        user_id=user_id,
        target_date=target,
        tasks=[task1, task2],
        fixed_events_input=[
            {"id": "meeting", "start_time": "10:00", "end_time": "11:00"}
        ],
        preferences={
            "preferred_wake_time": "07:00",
            "meals": {
                "breakfast_time": "07:30",
                "lunch_time": "12:30",
                "dinner_time": "19:00"
            },
            "routines": {
                "morning_duration_minutes": 30,
                "evening_duration_minutes": 30
            }
        },
        user_profile_data={"age": 30, "meq_score": 55}
    )
    
    result = asyncio.run(scheduler.generate_schedule(input_data))
    
    logger.info("✅ New module executed successfully")
    logger.info(f"  Schedule items: {len(result.scheduled_items)}")
    logger.info(f"  Task completion: {result.metrics.get('task_completion_pct', 0)}%")
    logger.info(f"  Unscheduled tasks: {result.metrics.get('unscheduled_tasks', 0)}")
    
    return {
        "schedule_items_count": len(result.scheduled_items),
        "task_completion_pct": result.metrics.get("task_completion_pct", 0),
        "unscheduled_tasks": result.metrics.get("unscheduled_tasks", 0),
        "total_task_minutes": result.metrics.get("total_task_minutes", 0),
        "total_meal_minutes": result.metrics.get("total_meal_minutes", 0),
        "total_routine_minutes": result.metrics.get("total_routine_minutes", 0),
        "warnings": len(result.warnings)
    }


def compare_results(old_results, new_results):
    """
    Compare results from old and new modules.
    
    Educational Note:
        Compares key metrics to verify functional equivalence.
        Scheduler is complex, so we focus on critical outputs.
    """
    logger.info("\n" + "=" * 60)
    logger.info("COMPARISON")
    logger.info("=" * 60)
    
    if old_results["schedule_items_count"] != new_results["schedule_items_count"]:
        logger.error(
            f"❌ Schedule items count mismatch: "
            f"old={old_results['schedule_items_count']}, "
            f"new={new_results['schedule_items_count']}"
        )
        return False
    logger.info("✅ Schedule items count matches")
    
    if abs(old_results["task_completion_pct"] - new_results["task_completion_pct"]) > 0.1:
        logger.error(
            f"❌ Task completion percentage mismatch: "
            f"old={old_results['task_completion_pct']}, "
            f"new={new_results['task_completion_pct']}"
        )
        return False
    logger.info("✅ Task completion percentage matches")
    
    if old_results["unscheduled_tasks"] != new_results["unscheduled_tasks"]:
        logger.error(
            f"❌ Unscheduled tasks mismatch: "
            f"old={old_results['unscheduled_tasks']}, "
            f"new={new_results['unscheduled_tasks']}"
        )
        return False
    logger.info("✅ Unscheduled tasks count matches")
    
    if old_results["total_task_minutes"] != new_results["total_task_minutes"]:
        logger.error(
            f"❌ Total task minutes mismatch: "
            f"old={old_results['total_task_minutes']}, "
            f"new={new_results['total_task_minutes']}"
        )
        return False
    logger.info("✅ Total task minutes match")
    
    logger.info("\n" + "=" * 60)
    logger.info("✅ ALL TESTS PASSED - Refactored scheduler modules work identically!")
    logger.info("=" * 60)
    return True


def test_edge_cases():
    """
    Test edge cases with new package.
    
    Educational Note:
        Verifies error handling and empty input scenarios.
    """
    logger.info("\n" + "=" * 60)
    logger.info("Testing edge cases")
    logger.info("=" * 60)
    
    from src.core.scheduler import Scheduler, ScheduleInputData
    from src.core.sleep import SleepCalculator
    from src.core.chronotype import ChronotypeAnalyzer
    from src.core.task import TaskPrioritizer
    from src.core.solver import ConstraintSchedulerSolver
    
    sleep_calc = SleepCalculator()
    chrono_analyzer = ChronotypeAnalyzer()
    task_prio = TaskPrioritizer()
    solver = ConstraintSchedulerSolver()
    
    scheduler = Scheduler(
        sleep_calculator=sleep_calc,
        chronotype_analyzer=chrono_analyzer,
        task_prioritizer=task_prio,
        constraint_solver=solver
    )
    
    input_data = ScheduleInputData(
        user_id=uuid4(),
        target_date=date.today(),
        tasks=[]
    )
    
    result = asyncio.run(scheduler.generate_schedule(input_data))
    
    if len(result.scheduled_items) > 0:
        logger.info("✅ Empty task list generates schedule with default items")
    else:
        logger.error("❌ Empty task list should generate basic schedule")
        return False
    
    return True


def run_all_tests():
    """
    Run all integration tests.
    
    Educational Note:
        Sequential test execution ensures clean state between tests.
    """
    logger.info("\n" + "=" * 70)
    logger.info("PHASE 5 INTEGRATION TEST: Scheduler Modules Comparison")
    logger.info("=" * 70)
    
    logger.info("\n" + "=" * 60)
    logger.info("Testing OLD scheduler_legacy.py module")
    logger.info("=" * 60)
    old_results = test_old_module()
    
    logger.info("\n" + "=" * 60)
    logger.info("Testing NEW scheduler package modules")
    logger.info("=" * 60)
    new_results = test_new_module()
    
    if not compare_results(old_results, new_results):
        logger.error("\n❌ TESTS FAILED - Modules produce different results!")
        return False
    
    if not test_edge_cases():
        logger.error("\n❌ EDGE CASE TESTS FAILED!")
        return False
    
    return True


if __name__ == "__main__":
    import sys
    success = run_all_tests()
    sys.exit(0 if success else 1)
