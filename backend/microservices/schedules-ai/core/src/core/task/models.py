"""
Task data structures and enumerations.

Defines core task representation including priority levels, energy requirements,
and task metadata.

Educational Context:
    Dataclasses provide clean, immutable-ish structures for domain objects.
    Enums ensure type safety and prevent magic numbers/strings.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import List, Optional, Set
from uuid import UUID, uuid4

logger = logging.getLogger(__name__)


class TaskPriority(Enum):
    """
    Task priority levels from critical to optional.
    
    Educational Note:
        Enum values are comparable, enabling natural sorting by priority.
    """
    CRITICAL = 5   
    HIGH = 4       
    MEDIUM = 3     
    LOW = 2        
    OPTIONAL = 1   

    def __lt__(self, other):
        """Enables priority comparison."""
        if self.__class__ is other.__class__:
            return self.value < other.value
        return NotImplemented


class EnergyLevel(Enum):
    """
    Required energy level for task execution.
    
    Educational Note:
        Matching task energy to user energy patterns improves scheduling quality.
    """
    HIGH = 3       
    MEDIUM = 2     
    LOW = 1        


@dataclass
class Task:
    """
    Complete task representation with scheduling metadata.
    
    Educational Note:
        Dataclass auto-generates __init__, __repr__, __eq__ reducing boilerplate.
        field(default_factory) ensures each instance gets its own mutable defaults.
    """
    title: str
    id: UUID = field(default_factory=uuid4)
    description: str = ""
    priority: TaskPriority = TaskPriority.MEDIUM
    energy_level: EnergyLevel = EnergyLevel.MEDIUM
    duration: timedelta = timedelta(minutes=30)
    deadline: Optional[datetime] = None
    earliest_start: Optional[datetime] = None
    dependencies: Set[UUID] = field(default_factory=set)
    tags: List[str] = field(default_factory=list)
    location: Optional[str] = None
    completed: bool = False
    completion_date: Optional[datetime] = None
    postponed_count: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_modified: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self):
        """
        Validates task data after initialization.
        """
        self._validate_title()
        self._validate_duration()
        self._ensure_timezone_aware()

    def _validate_title(self) -> None:
        """
        Ensures task has non-empty title.
        """
        if not self.title:
            raise ValueError("Task title cannot be empty")

    def _validate_duration(self) -> None:
        """
        Ensures task has positive duration.
        """
        if self.duration.total_seconds() <= 0:
            raise ValueError(f"Duration must be positive: {self.duration}")

    def _ensure_timezone_aware(self) -> None:
        """
        Converts naive datetimes to UTC.
        
        Educational Note:
            Timezone-naive datetimes cause subtle bugs. We enforce UTC.
        """
        if self.deadline and self.deadline.tzinfo is None:
            object.__setattr__(self, 'deadline', self.deadline.replace(tzinfo=timezone.utc))
        if self.earliest_start and self.earliest_start.tzinfo is None:
            object.__setattr__(self, 'earliest_start', self.earliest_start.replace(tzinfo=timezone.utc))
        if self.completion_date and self.completion_date.tzinfo is None:
            object.__setattr__(self, 'completion_date', self.completion_date.replace(tzinfo=timezone.utc))

    def __hash__(self) -> int:
        """
        Makes Task hashable by ID for use in sets/dicts.
        """
        return hash(self.id)

    def __eq__(self, other: object) -> bool:
        """
        Tasks are equal if IDs match.
        """
        if not isinstance(other, Task):
            return NotImplemented
        return self.id == other.id

    def mark_complete(self) -> None:
        """
        Marks task as completed with current timestamp.
        """
        if not self.completed:
            now_utc = datetime.now(timezone.utc)
            self.completed = True
            self.completion_date = now_utc
            self.last_modified = now_utc
