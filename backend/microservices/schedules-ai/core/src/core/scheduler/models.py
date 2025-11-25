"""
Data models for schedule generation.

This module defines the input and output structures for schedule generation,
providing type-safe interfaces for all scheduling operations.
"""

from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from src.core.chronotype.models import Chronotype, PrimeWindow


@dataclass(frozen=True)
class ScheduleInputData:
    """
    Input data required to generate a schedule.
    
    Educational Note:
        Using frozen dataclass ensures immutability of inputs throughout
        the scheduling pipeline, preventing accidental modifications that
        could lead to inconsistent state.
    """

    user_id: UUID
    target_date: date
    tasks: List[Any]
    fixed_events_input: List[Dict[str, Any]] = field(default_factory=list)
    preferences: Dict[str, Any] = field(default_factory=dict)
    user_profile_data: Optional[Dict[str, Any]] = None
    wearable_data_today: Optional[Dict[str, Any]] = None
    historical_data: Optional[Any] = None


@dataclass(frozen=True)
class ScheduleChronotypeContext:
    """
    Minimal chronotype data for schedule generation.

    Educational Note:
        Replaces complex ChronotypeProfile with simple context containing
        only essential data: chronotype classification and prime window.
        This separation keeps chronotype module focused on classification
        while scheduler handles timing and task placement.
        
        NEW: energy_pattern provides 24-hour energy curve (0.0-1.0) for
        each hour, enabling energy-aware task scheduling that respects
        user's circadian rhythm.
    """
    user_id: UUID
    chronotype: Chronotype
    prime_window: PrimeWindow
    energy_pattern: Dict[int, float] = field(default_factory=dict)
    source: str = "meq"


@dataclass(frozen=True)
class GeneratedSchedule:
    """
    Representation of a generated schedule with metadata.
    
    Educational Note:
        Includes not just the schedule items but also quality metrics,
        explanations for transparency, and warnings to help users understand
        scheduling decisions and constraints.
    """

    user_id: UUID
    target_date: date
    schedule_id: UUID = field(default_factory=uuid4)
    scheduled_items: List[Dict[str, Any]] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    explanations: Dict[str, Any] = field(default_factory=dict)
    generation_timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    warnings: List[str] = field(default_factory=list)
    sleep_recommendation: Optional[Any] = None
    routine_preferences: Dict[str, Any] = field(default_factory=dict)
