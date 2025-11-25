"""
Main Scheduling Orchestration Module.

Coordinates the generation of personalized daily schedules using:
1. SleepCalculator - calculates recommended sleep windows
2. ChronotypeAnalyzer - creates user chronotype profiles
3. TaskPrioritizer - generates daily energy patterns
4. ConstraintSchedulerSolver - creates schedule skeletons without overlapping blocks
5. LLMEngine - refines the skeleton (adds meals, routines, breaks, fills gaps)

Educational Note:
    This module demonstrates the Facade pattern, providing a simple interface
    to complex subsystems. The Scheduler class coordinates multiple specialized
    components to generate personalized schedules.
"""

import logging
from typing import Any, Dict, List, Optional
from uuid import UUID

from src.core.scheduler.models import GeneratedSchedule, ScheduleInputData
from src.core.scheduler.profile_prep import prepare_chronotype_context, add_energy_pattern_to_context
from src.core.scheduler.sleep_prep import calculate_sleep_window
from src.core.scheduler.solver_prep import prepare_solver_input
from src.core.scheduler.context import create_llm_context
from src.core.scheduler.processor import process_core_schedule
from src.core.scheduler.metrics import calculate_schedule_metrics

logger = logging.getLogger(__name__)
CORE_IMPORTS_OK: bool = True


class Scheduler:
    """
    Orchestrates the generation of personalized daily schedules.
    
    Educational Note:
        Uses dependency injection for all components, enabling
        flexible configuration and easy testing through mocking.
    """

    def __init__(
        self,
        sleep_calculator,
        chronotype_analyzer,
        task_prioritizer,
        constraint_solver,
        llm_engine: Optional[Any] = None,
        wearable_service: Optional[Any] = None,
        history_service: Optional[Any] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Initializes the Scheduler with necessary components.
        
        Educational Note:
            Configuration dictionary allows runtime customization
            without changing code, supporting different deployment
            environments (development, production, testing).
        """
        if not CORE_IMPORTS_OK:
            raise ImportError(
                "Missing required core dependencies for Scheduler initialization."
            )
        
        self.sleep_calculator = sleep_calculator
        self.chronotype_analyzer = chronotype_analyzer
        self.task_prioritizer = task_prioritizer
        self.constraint_solver = constraint_solver
        self.llm_engine = llm_engine
        self.wearable_service = wearable_service
        self.history_service = history_service
        self.config = config or {}
        
        self._llm_refinement_enabled = (
            llm_engine is not None and self.config.get("use_llm_refinement", True)
        )
        
        logger.info(
            f"Scheduler initialized (LLM refinement: {self._llm_refinement_enabled})"
        )

    async def generate_schedule(
        self, input_data: ScheduleInputData
    ) -> GeneratedSchedule:
        """
        Main method for generating a daily schedule.
        
        Educational Note:
            Async method supports non-blocking LLM API calls.
            Error handling ensures partial failures don't break entire system.
        """
        warnings: List[str] = []
        
        try:
            chronotype_context = self._prepare_profile(input_data)
            sleep_metrics = self._calculate_sleep(chronotype_context, input_data)
            chronotype_context = add_energy_pattern_to_context(chronotype_context, sleep_metrics)
            
            solver_result = self._prepare_solver_input(
                input_data, chronotype_context, sleep_metrics
            )
            
            if solver_result is None:
                return self._create_empty(
                    input_data,
                    warnings,
                    "Error preparing data for solver.",
                )
            
            solver_input, adjusted_sleep_metrics, all_fixed_events = solver_result
            
            logger.debug("Running ConstraintSchedulerSolver...")
            core_schedule = self.constraint_solver.solve(solver_input)
            
            if core_schedule is None:
                logger.warning("Solver could not find any solution.")
                return self._create_empty(
                    input_data,
                    warnings + ["No possible core schedule."],
                    "Constraint solver failed.",
                )
            
            logger.info(f"🔧 Solver returned {len(core_schedule)} items")
            for idx, item in enumerate(core_schedule, 1):
                task_name = self._get_task_name_by_id(item.task_id, input_data.tasks)
                logger.info(f"   {idx}. {item.start_time.strftime('%H:%M')}-{item.end_time.strftime('%H:%M')}: {task_name}")
            
            if self._llm_refinement_enabled and self.llm_engine:
                final_items, metrics, explanations = await self._refine_with_llm(
                    core_schedule, input_data, chronotype_context, adjusted_sleep_metrics, all_fixed_events
                )
            else:
                final_items = self._process_core_schedule(
                    core_schedule, input_data, adjusted_sleep_metrics
                )
                metrics = self._calculate_metrics(final_items, input_data.tasks)
                explanations = {}
            
            routine_prefs = input_data.preferences.get("routines", {})
            
            return GeneratedSchedule(
                user_id=input_data.user_id,
                target_date=input_data.target_date,
                scheduled_items=final_items,
                metrics=metrics,
                explanations=explanations,
                warnings=warnings,
                sleep_recommendation=adjusted_sleep_metrics,
                routine_preferences=routine_prefs,
            )
        
        except Exception as e:
            logger.exception("Unexpected error during schedule generation.")
            return self._create_empty(
                input_data,
                warnings,
                f"Internal error: {e}",
            )

    def _prepare_profile(self, input_data: ScheduleInputData):
        """
        Creates chronotype context with prime window.
        
        Educational Note:
            Simplified to use chronotype context instead of complex
            profile, focusing on essential scheduling data.
        """
        return prepare_chronotype_context(input_data, self.chronotype_analyzer)

    def _calculate_sleep(self, chronotype_context, input_data: ScheduleInputData):
        """
        Calculates the recommended sleep window.
        
        Educational Note:
            Separates sleep calculation from schedule generation
            for easier testing and reuse.
        """
        return calculate_sleep_window(
            self.sleep_calculator, chronotype_context, input_data
        )

    def _prepare_solver_input(
        self, input_data: ScheduleInputData, chronotype_context, sleep_metrics
    ):
        """
        Converts input data to SolverInput.
        
        Educational Note:
            Conversion layer decouples user-facing API from
            internal solver representation.
        """
        return prepare_solver_input(
            input_data, chronotype_context, sleep_metrics, self.task_prioritizer
        )

    async def _refine_with_llm(
        self, core_schedule, input_data, chronotype_context, sleep_metrics, all_fixed_events
    ):
        """
        Refines schedule using LLM with validation fallback.
        
        Educational Note:
            LLM adds natural language understanding for complex
            constraints (e.g., "I'm most creative in the morning").
            
            Validation layer ensures LLM output quality:
            1. Try LLM refinement
            2. Validate output (overlaps, sleep blocks, task times)
            3. If validation fails → fallback to deterministic schedule
            4. This ensures users ALWAYS get correct schedules
        """
        logger.debug("Refining schedule using LLM...")
        
        context = create_llm_context(
            input_data, chronotype_context, sleep_metrics,
            self.task_prioritizer,
            self.wearable_service,
            self.history_service,
            all_fixed_events
        )
        
        try:
            llm_output = await self.llm_engine.refine_and_complete_schedule(
                core_schedule, context
            )
            
            from src.services.llm.validator import validate_llm_schedule
            
            validation_errors = validate_llm_schedule(
                llm_output,
                core_schedule,
                sleep_metrics,
                input_data
            )
            
            if validation_errors:
                logger.warning(
                    "⚠️ LLM schedule validation failed, using deterministic fallback"
                )
                return self._generate_deterministic_schedule(
                    core_schedule, input_data, sleep_metrics
                )
            
            logger.info("✅ LLM schedule validated successfully")
            final_items = llm_output.get("schedule", [])
            metrics = llm_output.get("metrics", {})
            explanations = llm_output.get("explanations", {})
            
            return final_items, metrics, explanations
            
        except Exception as e:
            logger.error(f"❌ LLM refinement error: {e}", exc_info=True)
            logger.info("Using deterministic fallback due to LLM error")
            return self._generate_deterministic_schedule(
                core_schedule, input_data, sleep_metrics
            )
    
    def _generate_deterministic_schedule(
        self, core_schedule, input_data, sleep_metrics
    ):
        """
        Generates schedule using deterministic pipeline (no LLM).
        
        Educational Note:
            This is the fallback when LLM fails validation.
            Uses process_core_schedule which:
            - Adds meals, routines, activities deterministically
            - Merges sleep blocks into one
            - Fills ALL gaps with appropriate breaks
            - Guarantees no overlaps, continuous coverage
        """
        logger.info("🔧 Generating deterministic schedule...")
        
        final_items = self._process_core_schedule(
            core_schedule, input_data, sleep_metrics
        )
        metrics = self._calculate_metrics(final_items, input_data.tasks)
        explanations = {
            "key_decisions": [
                "Used deterministic schedule generation",
                "Meals placed at preferred times",
                "Gaps filled with appropriate breaks",
                "Sleep merged into continuous blocks"
            ],
            "optimization_focus": "Deterministic placement ensuring no overlaps"
        }
        
        return final_items, metrics, explanations

    def _process_core_schedule(
        self, core_schedule, input_data: ScheduleInputData, sleep_metrics
    ):
        """
        Formats core solver results and adds meals, routines, breaks.
        
        Educational Note:
            Non-LLM path ensures system works without AI dependency,
            important for reliability and cost control.
        """
        return process_core_schedule(
            core_schedule,
            input_data,
            sleep_metrics,
            self._prepare_solver_input,
            self._prepare_profile
        )

    def _calculate_metrics(self, items, tasks):
        """
        Calculates metrics for the completed schedule.
        
        Educational Note:
            Metrics provide transparency and enable schedule
            quality assessment.
        """
        return calculate_schedule_metrics(items, tasks)

    def _get_task_name_by_id(
        self, task_id: UUID, tasks: List[Any]
    ) -> str:
        """
        Retrieves task name by matching task_id.
        
        Educational Note:
            Helper method encapsulates lookup logic, making main
            code cleaner and more maintainable.
        """
        for task in tasks:
            if hasattr(task, 'id') and task.id == task_id:
                return getattr(task, 'title', getattr(task, 'name', 'Unknown Task'))
            elif isinstance(task, dict):
                dict_id = task.get('id')
                if dict_id == task_id or (isinstance(dict_id, str) and dict_id == str(task_id)):
                    return task.get('title', task.get('name', 'Unknown Task'))
        return f"Task {str(task_id)[:8]}..."

    def _create_empty(
        self,
        input_data: ScheduleInputData,
        warnings: List[str],
        error_msg: str,
    ) -> GeneratedSchedule:
        """
        Creates an empty schedule in case of error.
        
        Educational Note:
            Graceful degradation pattern - system returns structured
            error rather than crashing, enabling better error handling.
        """
        logger.error(f"Generating empty schedule: {error_msg}")
        
        routine_prefs = input_data.preferences.get("routines", {})
        
        return GeneratedSchedule(
            user_id=input_data.user_id,
            target_date=input_data.target_date,
            scheduled_items=[],
            metrics={"status": "failed"},
            explanations={"error": error_msg},
            warnings=warnings + [error_msg],
            sleep_recommendation=None,
            routine_preferences=routine_prefs,
        )


def save_schedule_to_json(schedule_result, file_path):
    """
    Saves the generated schedule to a JSON file in a format compatible with APIdog.
    
    Educational Note:
        Separate function for file I/O keeps Scheduler class focused
        on business logic, following Single Responsibility Principle.
    """
    import json
    import os

    tasks = []
    for item in schedule_result.scheduled_items:
        tasks.append({
            "start_time": item['start_time'],
            "end_time": item['end_time'],
            "task": item['name']
        })

    schedule_json = {
        "tasks": tasks
    }

    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(schedule_json, f, indent=2, ensure_ascii=False)

    print(f"\n💾 Schedule saved to file: {file_path}")
