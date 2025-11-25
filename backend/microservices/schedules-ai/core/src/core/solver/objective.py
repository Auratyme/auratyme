"""
Objective Function Construction for Schedule Optimization.

Defines what makes a schedule "good" by combining multiple scoring criteria
into a single objective function the solver attempts to maximize.

Educational Context:
    The objective function is how we tell the solver what we want. In
    scheduling, "goodness" is multi-dimensional:
    - High priority tasks should be scheduled (priority weight)
    - Tasks should match user's energy levels (energy matching)
    - Earlier is often better (start time penalty)
    
    We combine these by weighted sum. Weights determine trade-offs: a high
    priority weight means "priority matters more than energy matching."
"""

import logging
from typing import Dict, List
from uuid import UUID

try:
    from ortools.sat.python import cp_model
except ImportError:
    pass

logger = logging.getLogger(__name__)


def create_priority_term(priority: int, weight: int) -> int:
    """
    Creates objective term rewarding task priority.

    Educational Note:
        Constant terms in the objective function represent fixed rewards.
        Higher priority tasks contribute more to the objective value.
    """
    return priority * weight


def create_start_penalty_term(
    start_var: cp_model.IntVar,
    weight: int
) -> cp_model.LinearExpr:
    """
    Creates objective term penalizing late starts.

    Educational Note:
        Multiplying by negative weight converts a penalty into something
        that subtracts from the objective. This encourages earlier starts.
    """
    return start_var * -weight


def normalize_task_energy(energy_level: int) -> float:
    """
    Converts task energy level to normalized scale.

    Educational Note:
        Normalization (0.0-1.0 scale) makes energy levels comparable to
        user energy pattern. This is essential for matching calculation.
    """
    return energy_level / 3.0


def calculate_energy_match_score(
    user_energy: float,
    task_energy: float
) -> int:
    """
    Computes how well task energy matches user energy.

    Returns:
        Score from 0-100 where 100 is perfect match

    Educational Note:
        Using absolute difference penalizes mismatches. A high-energy task
        during low-energy time (or vice versa) scores poorly. We scale to
        0-100 for interpretability.
    """
    match_quality = 1.0 - abs(user_energy - task_energy)
    return int(match_quality * 100)


def create_hourly_energy_scores(
    task_energy: int,
    energy_pattern: Dict[int, float]
) -> Dict[int, int]:
    """
    Pre-computes energy match scores for each hour.

    Educational Note:
        Pre-computation avoids redundant calculations in the solver. We
        compute 24 scores once, then use CP-SAT's element constraint to
        select the appropriate score based on actual scheduled hour.
    """
    task_energy_norm = normalize_task_energy(task_energy)
    scores = {}
    
    for hour in range(24):
        user_energy = energy_pattern.get(hour, 0.5)
        scores[hour] = calculate_energy_match_score(user_energy, task_energy_norm)
    
    return scores


def create_start_hour_variable(
    model: cp_model.CpModel,
    task_id: UUID,
    start_var: cp_model.IntVar
) -> cp_model.IntVar:
    """
    Creates variable representing which hour task starts in.

    Educational Note:
        Division by 60 converts minutes to hours. CP-SAT's AddDivisionEquality
        maintains the relationship: start_hour = start_minutes // 60
    """
    start_hour = model.NewIntVar(0, 23, f'start_hour_{task_id}')
    model.AddDivisionEquality(start_hour, start_var, 60)
    return start_hour


def create_energy_score_variable(
    model: cp_model.CpModel,
    task_id: UUID,
    start_hour: cp_model.IntVar,
    hourly_scores: Dict[int, int]
) -> cp_model.IntVar:
    """
    Creates variable representing energy match quality.

    Educational Note:
        AddElement is a constraint that says: energy_score = hourly_scores[start_hour].
        This connects the hour the task is scheduled to its energy match score.
    """
    score_var = model.NewIntVar(0, 100, f'energy_score_{task_id}')
    score_list = [hourly_scores[h] for h in range(24)]
    model.AddElement(start_hour, score_list, score_var)
    return score_var


def should_add_energy_term(energy_weight: int, energy_level: int) -> bool:
    """
    Determines if energy matching should be included.

    Educational Note:
        Zero weight means "don't care about energy matching." Checking this
        avoids adding unnecessary variables and constraints to the model.
    """
    return energy_weight > 0 and 1 <= energy_level <= 3


def add_energy_matching_term(
    model: cp_model.CpModel,
    task_id: UUID,
    start_var: cp_model.IntVar,
    energy_level: int,
    energy_pattern: Dict[int, float],
    energy_weight: int,
    objective_terms: List
) -> None:
    """
    Adds energy matching component to objective function.
    
    Applies dynamic weight scaling based on task energy level:
    - HIGH energy tasks (3): 3x weight → strongly prefer peak hours
    - MEDIUM energy tasks (2): 1.5x weight → moderate preference
    - LOW energy tasks (1): 1x weight → base preference

    Educational Note:
        This creates two auxiliary variables (start_hour and energy_score)
        connected by constraints. The energy_score then contributes to the
        objective, weighted by energy_weight scaled by task energy level.
        
        High-energy tasks get 3x boost, making solver strongly prefer
        placing them in peak energy windows (e.g., 17:00-22:00 for night owls).
    """
    hourly_scores = create_hourly_energy_scores(energy_level, energy_pattern)
    start_hour = create_start_hour_variable(model, task_id, start_var)
    energy_score = create_energy_score_variable(model, task_id, start_hour, hourly_scores)
    
    scaled_weight = energy_weight * energy_level
    objective_terms.append(energy_score * scaled_weight)


def build_objective_function(
    model: cp_model.CpModel,
    task_vars: Dict[UUID, Dict],
    tasks_by_id: Dict[UUID, any],
    energy_pattern: Dict[int, float],
    weights: Dict[str, int]
) -> None:
    """
    Constructs complete objective function from all components.

    Educational Note:
        The objective is a weighted sum of multiple terms. CP-SAT maximizes
        this sum, balancing trade-offs between priority, energy matching,
        and start time preferences according to the weights.
        
        CRITICAL: With optional tasks, we multiply all terms by is_scheduled
        boolean to reward scheduling high-priority tasks while allowing
        solver to skip low-priority ones when space is limited.
    """
    objective_terms = []
    priority_weight = weights.get("priority", 10)
    energy_weight = weights.get("energy_match", 5)
    start_penalty_weight = weights.get("start_time_penalty", 1)
    scheduled_bonus = 10000
    
    for task_id, task in tasks_by_id.items():
        if task_id not in task_vars:
            continue
        
        is_scheduled = task_vars[task_id].get('is_scheduled')
        if is_scheduled is None:
            continue
        
        priority_term = create_priority_term(task.priority, priority_weight)
        objective_terms.append(is_scheduled * (scheduled_bonus + priority_term))
        
        start_var = task_vars[task_id]['start']
        penalty_value = model.NewIntVar(-1440, 0, f'penalty_{task_id}')
        model.Add(penalty_value == -start_var * start_penalty_weight).OnlyEnforceIf(is_scheduled)
        model.Add(penalty_value == 0).OnlyEnforceIf(is_scheduled.Not())
        objective_terms.append(penalty_value)
        
        if should_add_energy_term(energy_weight, task.energy_level):
            add_energy_matching_term(
                model,
                task_id,
                task_vars[task_id]['start'],
                task.energy_level,
                energy_pattern,
                energy_weight,
                objective_terms
            )
    
    model.Maximize(sum(objective_terms))
