"""Quick comparison test: old vs new solver."""

from datetime import date, time
from uuid import UUID
from src.core.solver import (
    ConstraintSchedulerSolver,
    FixedEventInterval,
    SolverInput,
    SolverTask,
)

def time_to_minutes(t):
    return t.hour * 60 + t.minute

task1 = SolverTask(
    id=UUID('a0000001-e89b-12d3-a456-426614174000'),
    duration_minutes=120,
    priority=4,
    energy_level=3
)
task2 = SolverTask(
    id=UUID('a0000002-e89b-12d3-a456-426614174000'),
    duration_minutes=45,
    priority=3,
    energy_level=2,
    dependencies=[task1.id]
)
task3 = SolverTask(
    id=UUID('a0000003-e89b-12d3-a456-426614174000'),
    duration_minutes=60,
    priority=4,
    energy_level=1
)
task4 = SolverTask(
    id=UUID('a0000004-e89b-12d3-a456-426614174000'),
    duration_minutes=30,
    priority=2,
    energy_level=2,
    earliest_start_minutes=time_to_minutes(time(16, 30))
)

fixed_events = [
    FixedEventInterval(
        id="lunch",
        start_minutes=time_to_minutes(time(12, 30)),
        end_minutes=time_to_minutes(time(13, 15))
    ),
    FixedEventInterval(
        id="meeting",
        start_minutes=time_to_minutes(time(15, 0)),
        end_minutes=time_to_minutes(time(16, 0))
    ),
]

energy = {h: 0.5 for h in range(24)}
energy.update({8: 0.7, 9: 0.8, 10: 0.9, 11: 0.8, 12: 0.6, 13: 0.5, 14: 0.7, 15: 0.6, 16: 0.5, 17: 0.4})

solver_input = SolverInput(
    target_date=date.today(),
    tasks=[task1, task2, task3, task4],
    fixed_events=fixed_events,
    day_start_minutes=time_to_minutes(time(8, 0)),
    day_end_minutes=time_to_minutes(time(18, 0)),
    user_energy_pattern=energy
)

solver = ConstraintSchedulerSolver(config={"solver_time_limit_seconds": 10.0})
solution = solver.solve(solver_input)

print("\n--- New Solver Results ---")
print(f"Schedule for {solver_input.target_date}:")
print("  Fixed Events:")
for event in fixed_events:
    print(f"    {event.start_minutes//60:02d}:{event.start_minutes%60:02d} - {event.end_minutes//60:02d}:{event.end_minutes%60:02d}: {event.id}")
print("  Scheduled Tasks:")
for item in solution:
    print(f"    {item.start_time.strftime('%H:%M')} - {item.end_time.strftime('%H:%M')}: Task {str(item.task_id)[:4]}...")
