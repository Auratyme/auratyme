"""
Task prioritization logic and scoring.

Combines multiple factors (priority, deadline, dependencies, postponements)
into a single priority score for ranking tasks.

Educational Context:
    Weighted scoring allows balancing different concerns. Weights are
    configurable, letting users emphasize what matters to them.
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set
from uuid import UUID

from .models import Task, TaskPriority
from .urgency import calculate_time_urgency_factor

logger = logging.getLogger(__name__)


class TaskPrioritizer:
    """
    Calculates priority scores for tasks.
    
    Educational Note:
        Combines multiple dimensions (priority, urgency, dependencies)
        into single score for sorting. Configurable weights let users
        tune the balance.
    """
    
    DEFAULT_WEIGHTS = {
        "priority": 0.50,
        "deadline": 0.35,
        "dependencies": 0.10,
        "postponed": 0.05,
    }

    def __init__(
        self,
        weights: Optional[Dict[str, float]] = None,
        user_energy_pattern: Optional[Dict[int, float]] = None,
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initializes prioritizer with configuration.
        """
        self._weights = self._merge_weights(weights)
        self._user_energy_pattern = self._setup_energy_pattern(user_energy_pattern)
        self._config = config or {}
        self._dependency_max = self._config.get("dependency_max_scale", 5)
        self._postponed_max = self._config.get("postponed_max_scale", 5)

    def _merge_weights(self, custom_weights: Optional[Dict[str, float]]) -> Dict[str, float]:
        """
        Merges custom weights with defaults.
        """
        weights = self.DEFAULT_WEIGHTS.copy()
        if custom_weights:
            weights.update(custom_weights)
        return weights

    def _setup_energy_pattern(self, pattern: Optional[Dict[int, float]]) -> Dict[int, float]:
        """
        Sets up energy pattern with defaults if missing.
        """
        if pattern:
            return pattern
        logger.warning("No energy pattern provided, using flat 0.5")
        return {h: 0.5 for h in range(24)}

    def prioritize(
        self,
        tasks: List[Task],
        current_datetime: Optional[datetime] = None,
    ) -> List[Task]:
        """
        Sorts tasks by priority score (highest first).
        """
        if not tasks:
            return []
        
        now = self._normalize_time(current_datetime)
        dep_map = self._build_dependency_map(tasks)
        scored_tasks = self._score_all_tasks(tasks, now, dep_map)
        
        return self._sort_by_score(scored_tasks)

    def _normalize_time(self, dt: Optional[datetime]) -> datetime:
        """
        Ensures datetime is UTC.
        """
        now = dt or datetime.now(timezone.utc)
        if now.tzinfo is None:
            return now.replace(tzinfo=timezone.utc)
        return now

    def _score_all_tasks(
        self,
        tasks: List[Task],
        now: datetime,
        dep_map: Dict[UUID, Set[UUID]]
    ) -> List[tuple]:
        """
        Calculates scores for all non-completed tasks.
        """
        scored = []
        for task in tasks:
            if not task.completed:
                score = self._calculate_priority_score(task, now, dep_map)
                scored.append((-score, str(task.id), task))
        return scored

    def _sort_by_score(self, scored_tasks: List[tuple]) -> List[Task]:
        """
        Sorts tasks by score using heap for efficiency.
        """
        import heapq
        heapq.heapify(scored_tasks)
        return [heapq.heappop(scored_tasks)[2] for _ in range(len(scored_tasks))]

    def _calculate_priority_score(
        self,
        task: Task,
        current_datetime: datetime,
        dependency_map: Dict[UUID, Set[UUID]],
    ) -> float:
        """
        Combines all factors into single priority score.
        """
        prio_factor = self._get_priority_factor(task)
        deadline_factor = calculate_time_urgency_factor(task, current_datetime)
        dep_factor = self._get_dependency_factor(task, dependency_map)
        postponed_factor = self._get_postponed_factor(task)
        
        score = (
            self._weights["priority"] * prio_factor +
            self._weights["deadline"] * deadline_factor +
            self._weights["dependencies"] * dep_factor +
            self._weights["postponed"] * postponed_factor
        )
        
        return max(0.0, score)

    def _get_priority_factor(self, task: Task) -> float:
        """
        Normalizes task priority to 0.0-1.0 range.
        """
        max_prio = max(p.value for p in TaskPriority)
        return task.priority.value / max_prio

    def _get_dependency_factor(
        self,
        task: Task,
        dep_map: Dict[UUID, Set[UUID]]
    ) -> float:
        """
        Calculates factor based on how many tasks depend on this.
        
        Educational Note:
            Tasks that block others should be prioritized higher.
        """
        dependent_count = len(dep_map.get(task.id, set()))
        return min(1.0, dependent_count / max(1, self._dependency_max))

    def _get_postponed_factor(self, task: Task) -> float:
        """
        Increases priority if task has been postponed repeatedly.
        
        Educational Note:
            Penalizes procrastination by boosting repeatedly-delayed tasks.
        """
        return min(1.0, task.postponed_count / max(1, self._postponed_max))

    def _build_dependency_map(self, tasks: List[Task]) -> Dict[UUID, Set[UUID]]:
        """
        Maps task IDs to sets of tasks that depend on them.
        """
        dep_map = {task.id: set() for task in tasks}
        
        for task in tasks:
            for prereq_id in task.dependencies:
                if prereq_id in dep_map:
                    dep_map[prereq_id].add(task.id)
        
        return dep_map

    def get_energy_pattern(self, profile: Optional[Any] = None) -> Dict[int, float]:
        """
        Returns energy pattern, optionally adapted to user profile.
        """
        if not profile:
            return self._user_energy_pattern.copy()
        
        return self._adapt_pattern_to_chronotype(profile)

    def _adapt_pattern_to_chronotype(self, profile: Any) -> Dict[int, float]:
        """
        Adjusts energy pattern based on chronotype.
        """
        pattern = self._user_energy_pattern.copy()
        
        if not hasattr(profile, 'primary_chronotype'):
            return pattern
        
        from src.core.chronotype import Chronotype
        
        if profile.primary_chronotype == Chronotype.EARLY_BIRD:
            pattern = self._boost_morning_energy(pattern)
        elif profile.primary_chronotype == Chronotype.NIGHT_OWL:
            pattern = self._boost_evening_energy(pattern)
        
        return pattern

    def _boost_morning_energy(self, pattern: Dict[int, float]) -> Dict[int, float]:
        """
        Increases energy during morning hours for early birds.
        """
        for h in range(6, 11):
            pattern[h] = min(1.0, pattern.get(h, 0.5) + 0.1)
        return pattern

    def _boost_evening_energy(self, pattern: Dict[int, float]) -> Dict[int, float]:
        """
        Increases energy during evening hours for night owls.
        """
        for h in range(17, 22):
            pattern[h] = min(1.0, pattern.get(h, 0.5) + 0.1)
        return pattern
