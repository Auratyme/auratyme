"""
Constraint-Based Schedule Solver Package.

Provides intelligent task scheduling using Google OR-Tools CP-SAT solver.
The solver finds optimal arrangements of tasks respecting time constraints,
dependencies, fixed events, and user energy patterns.

Public API:
    ConstraintSchedulerSolver: Main solver class for generating schedules
    ScheduledTaskInfo: Output structure representing scheduled tasks
    SolverInput: Input bundle for solver execution
    SolverTask: Task representation for solver
    FixedEventInterval: Immovable time blocks

Educational Context:
    This package demonstrates separation of concerns in a complex system:
    - models.py: Data structures (what we work with)
    - variables.py: Decision variables (what solver decides)
    - constraints.py: Rules that must be satisfied
    - objective.py: What makes a solution "good"
    - solver.py: Orchestration (how it all fits together)

Example Usage:
    ```python
    from core.solver import ConstraintSchedulerSolver, SolverInput, SolverTask
    from datetime import date
    from uuid import uuid4

    tasks = [
        SolverTask(
            id=uuid4(),
            duration_minutes=120,
            priority=5,
            energy_level=3
        )
    ]

    solver_input = SolverInput(
        target_date=date.today(),
        tasks=tasks,
        fixed_events=[],
        user_energy_pattern={h: 0.7 for h in range(9, 17)}
    )

    solver = ConstraintSchedulerSolver()
    schedule = solver.solve(solver_input)
    ```
"""

from .models import (
    FixedEventInterval,
    ScheduledTaskInfo,
    SolverInput,
    SolverTask,
)
from .solver import ConstraintSchedulerSolver

__all__ = [
    "ConstraintSchedulerSolver",
    "FixedEventInterval",
    "ScheduledTaskInfo",
    "SolverInput",
    "SolverTask",
]
