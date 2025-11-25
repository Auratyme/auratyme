"""
Main Constraint Scheduler Solver.

Orchestrates the constraint satisfaction programming (CSP) solver to find
optimal schedules. This is the entry point that coordinates variable creation,
constraint addition, objective function setup, solving, and result parsing.

Educational Context:
    This module demonstrates the orchestrator pattern. Instead of one giant
    function, we break solving into discrete phases, each handled by specialized
    functions. This makes the code testable, maintainable, and easier to
    understand. Each phase has a single clear responsibility.
"""

import logging
from typing import Any, Dict, List, Optional
from uuid import UUID

try:
    from ortools.sat.python import cp_model
    ORTOOLS_AVAILABLE = True
except ImportError:
    ORTOOLS_AVAILABLE = False
    logging.getLogger(__name__).warning("OR-Tools not available")

try:
    from src.utils.time_utils import total_minutes_to_time
except ImportError:
    from datetime import time
    def total_minutes_to_time(minutes: int) -> time:
        minutes = max(0, min(1439, int(minutes)))
        hours, mins = divmod(minutes, 60)
        return time(hour=hours % 24, minute=mins)

from .models import SolverInput, ScheduledTaskInfo, SolverTask
from .variables import create_task_variables
from .constraints import (
    add_no_overlap_constraint,
    add_fixed_events_constraint,
    add_all_dependencies
)
from .objective import build_objective_function
from .parser import parse_solution
from .config import (
    extract_time_limit,
    extract_objective_weights,
    log_configuration
)
from .var_utils import (
    extract_interval_variables,
    extract_start_variables,
    extract_end_variables
)

logger = logging.getLogger(__name__)


class ConstraintSchedulerSolver:
    """
    CP-SAT scheduler for optimal task arrangements.

    Educational Note:
        Encapsulates configuration and execution in a reusable class.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """
        Initializes solver with configuration via dependency injection.
        """
        self._validate_ortools_available()
        config_dict = config or {}
        self._time_limit = extract_time_limit(config_dict)
        self._weights = extract_objective_weights(config_dict)
        log_configuration(self._time_limit, self._weights)

    def _validate_ortools_available(self) -> None:
        """
        Validates OR-Tools is available (fail-fast).
        """
        if not ORTOOLS_AVAILABLE:
            logger.error("OR-Tools library required but not available")

    def solve(self, solver_input: SolverInput) -> Optional[List[ScheduledTaskInfo]]:
        """
        Finds optimal schedule via orchestrated pipeline.

        Returns list of scheduled tasks or None if no solution.
        Pipeline: validate → model → variables → constraints → objective → solve → parse.
        """
        if not self._can_solve(solver_input):
            return self._handle_unsolvable_input(solver_input)
        
        model, solver = self._create_model_and_solver()
        task_vars = self._create_all_variables(model, solver_input)
        
        if not task_vars:
            return []
        
        self._add_all_constraints(model, task_vars, solver_input)
        self._set_objective(model, task_vars, solver_input)
        
        status = self._run_solver(solver, model)
        return self._parse_solution(status, solver, task_vars, solver_input)

    def _can_solve(self, solver_input: SolverInput) -> bool:
        """
        Validates solver can attempt this problem.

        Educational Note:
            Pre-flight checks prevent wasted computation. If we know solving
            will fail (e.g., OR-Tools missing), fail fast with clear error.
        """
        return ORTOOLS_AVAILABLE and isinstance(solver_input, SolverInput)

    def _handle_unsolvable_input(
        self,
        solver_input: SolverInput
    ) -> Optional[List[ScheduledTaskInfo]]:
        """
        Handles cases where solving is impossible.

        Educational Note:
            Graceful degradation: return empty schedule for no tasks, None
            for errors. Callers can distinguish "no solution" from "no tasks".
        """
        if not solver_input.tasks:
            logger.warning("No tasks to schedule")
            return []
        logger.error("Cannot solve: invalid input or OR-Tools unavailable")
        return None

    def _create_model_and_solver(self) -> tuple:
        """
        Instantiates CP-SAT model and solver.

        Educational Note:
            Separating instantiation makes testing easier. We can mock
            model/solver in tests without complex setup.
        """
        model = cp_model.CpModel()
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = self._time_limit
        return model, solver

    def _create_all_variables(
        self,
        model: cp_model.CpModel,
        solver_input: SolverInput
    ) -> Dict[UUID, Dict]:
        """
        Creates variables for all schedulable tasks.

        Educational Note:
            We collect variables in a dictionary indexed by task ID. This
            makes it easy to look up variables later when adding constraints.
        """
        task_vars = {}
        
        for task in solver_input.tasks:
            try:
                vars_dict = create_task_variables(
                    model,
                    task,
                    solver_input.day_start_minutes,
                    solver_input.day_end_minutes
                )
                task_vars[task.id] = vars_dict
            except Exception as e:
                logger.error(f"Failed to create variables for task {task.id}: {e}")
        
        logger.debug(f"Created variables for {len(task_vars)} tasks")
        return task_vars

    def _add_all_constraints(
        self,
        model: cp_model.CpModel,
        task_vars: Dict[UUID, Dict],
        solver_input: SolverInput
    ) -> None:
        """
        Adds all scheduling constraints to model.

        Educational Note:
            Three independent constraint phases: no overlap, fixed events,
            dependencies. Separation enables independent testing.
        """
        intervals = extract_interval_variables(task_vars)
        add_no_overlap_constraint(model, intervals)
        
        add_fixed_events_constraint(
            model,
            intervals,
            solver_input.fixed_events,
            solver_input.day_start_minutes,
            solver_input.day_end_minutes
        )
        
        starts = extract_start_variables(task_vars)
        ends = extract_end_variables(task_vars)
        add_all_dependencies(model, solver_input.tasks, starts, ends)
        
        logger.debug("All constraints added")

    def _create_task_lookup(
        self,
        tasks: List[SolverTask]
    ) -> Dict[UUID, SolverTask]:
        """
        Creates dictionary for fast task lookup by ID.

        Educational Note:
            Converting list to dict trades memory for speed. O(1) lookup
            instead of O(n) search, crucial when building objective function.
        """
        return {task.id: task for task in tasks}

    def _set_objective(
        self,
        model: cp_model.CpModel,
        task_vars: Dict[UUID, Dict],
        solver_input: SolverInput
    ) -> None:
        """
        Configures what the solver should optimize for.

        Educational Note:
            The objective function defines "goodness." Without it, CP-SAT
            would just find any feasible solution. With it, CP-SAT seeks
            the best solution according to our criteria.
        """
        tasks_by_id = self._create_task_lookup(solver_input.tasks)
        
        build_objective_function(
            model,
            task_vars,
            tasks_by_id,
            solver_input.user_energy_pattern,
            self._weights
        )
        
        logger.debug("Objective function set")

    def _run_solver(
        self,
        solver: cp_model.CpSolver,
        model: cp_model.CpModel
    ) -> int:
        """
        Executes the CP-SAT solver.

        Returns:
            Status code indicating result (OPTIMAL, FEASIBLE, etc.)

        Educational Note:
            Solving is the computationally intensive part. The time limit
            we set earlier caps how long this takes. Status tells us if
            solver found the best solution or just a good one.
        """
        logger.info(f"Starting solver (limit: {self._time_limit}s)...")
        status = solver.Solve(model)
        self._log_solver_result(solver, status)
        return status

    def _log_solver_result(
        self,
        solver: cp_model.CpSolver,
        status: int
    ) -> None:
        """
        Logs solver execution statistics.

        Educational Note:
            Metrics like wall time and objective value help evaluate solver
            performance. If solving is too slow, we can adjust time limits
            or simplify the model.
        """
        logger.info(f"Status: {solver.StatusName(status)}")
        logger.info(f"Objective: {solver.ObjectiveValue()}")
        logger.info(f"Time: {solver.WallTime():.2f}s")

    def _parse_solution(
        self,
        status: int,
        solver: cp_model.CpSolver,
        task_vars: Dict[UUID, Dict],
        solver_input: SolverInput
    ) -> Optional[List[ScheduledTaskInfo]]:
        """
        Delegates solution parsing to parser module.

        Educational Note:
            Delegating to specialized parser keeps this class focused on
            orchestration. Parser handles all extraction and transformation.
        """
        return parse_solution(status, solver, task_vars, solver_input.target_date)
