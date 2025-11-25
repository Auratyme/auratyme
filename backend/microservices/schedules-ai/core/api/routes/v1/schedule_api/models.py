"""
Pydantic models for schedule generation API endpoints.

This module defines request and response models that validate data
flow between clients and the schedule generation service. Models
demonstrate input validation, field constraints, and response
structure patterns essential for robust API design.
"""

from datetime import date, time
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator


class TaskInput(BaseModel):
    """
    Structure for defining a task in schedule generation requests.
    
    This model validates task input data ensuring required fields
    are present and constraints like positive duration are met.
    Demonstrates Pydantic field validation and default value
    generation patterns for API input handling.
    
    Educational Note:
        ID is not required - backend auto-generates it during
        processing. This simplifies client payload by removing
        unnecessary UUID generation from frontend.
    """
    name: str = Field(..., description="Descriptive name of the task")
    duration_minutes: int = Field(..., gt=0, description="Duration in minutes")
    priority: int = Field(default=3, ge=1, le=5, description="Priority level 1-5")
    deadline: Optional[date] = Field(default=None, description="Optional deadline date")


class FixedEventInput(BaseModel):
    """
    Structure for defining fixed events in schedule requests.
    
    This model ensures fixed events have proper time ordering
    through custom validation. Demonstrates field-level validation
    techniques for maintaining data consistency in API requests.
    
    Educational Note:
        ID is not required - backend auto-generates it during
        processing. This simplifies client payload by removing
        unnecessary UUID generation from frontend.
    """
    name: str = Field(..., description="Name of the fixed event")
    start_time: time = Field(..., description="Start time of the event")
    end_time: time = Field(..., description="End time of the event")

    @field_validator('end_time')
    def validate_end_after_start(cls, end_time, info):
        """
        Validates end time occurs after start time for events.
        
        This validator prevents logical inconsistencies in event
        scheduling by ensuring chronological order. Educational
        example of cross-field validation in Pydantic models.
        """
        values = info.data
        if 'start_time' in values and end_time <= values['start_time']:
            raise ValueError('End time must be after start time')
        return end_time


class ScheduleGenerationRequest(BaseModel):
    """
    Request payload for generating personalized schedules.
    
    This model aggregates all input data needed for schedule
    generation including tasks, events, and user preferences.
    Demonstrates complex request model composition and optional
    field handling for flexible API design.
    
    Educational Note:
        Both user_id and target_date are now optional. When not
        provided, the backend generates them automatically using
        UUID4 and today's date respectively. This simplifies
        client integration by removing unnecessary fields.
    """
    user_id: Optional[UUID] = Field(
        default=None,
        description="User identifier for schedule (auto-generated if omitted)"
    )
    target_date: Optional[date] = Field(
        default=None,
        description="Target date for schedule (today if omitted)"
    )
    tasks: List[TaskInput] = Field(..., description="Tasks to be scheduled")
    fixed_events: List[FixedEventInput] = Field(
        default_factory=list,
        description="Pre-scheduled fixed events"
    )
    preferences: Dict[str, Any] = Field(
        default_factory=dict,
        description="User scheduling preferences"
    )
    user_profile: Dict[str, Any] = Field(
        default_factory=dict,
        description="User profile data including MEQ score, age, and sleep need"
    )


class ScheduledItem(BaseModel):
    """
    Represents a single item in the generated schedule.
    
    This model provides a unified structure for different types
    of schedule items (tasks, breaks, events). Demonstrates
    polymorphic data modeling within API responses.
    """
    id: str = Field(..., description="Unique identifier of the item")
    type: str = Field(..., description="Type of the item")
    name: str = Field(..., description="Name of the item")
    start_time: time = Field(..., description="Scheduled start time")
    end_time: time = Field(..., description="Scheduled end time")


class SimplifiedScheduleTask(BaseModel):
    """
    Represents a task in simplified schedule format.
    
    This model provides backward compatibility with legacy
    API clients by maintaining a simple task structure.
    Demonstrates API evolution and backward compatibility
    techniques in response model design.
    """
    start_time: str = Field(..., description="Start time in HH:MM format")
    end_time: str = Field(..., description="End time in HH:MM format")
    task: str = Field(..., description="Name of the task")


class ScheduleSuccessResponse(BaseModel):
    """
    Response payload with structured success data.
    
    This model wraps schedule data with metadata providing
    consistent response structure. Demonstrates response
    standardization patterns for API design consistency.
    """
    message: str = Field(
        default="Schedule received successfully.",
        description="Success message"
    )
    data: Dict[str, List[SimplifiedScheduleTask]] = Field(
        ...,
        description="Response data containing scheduled tasks"
    )
