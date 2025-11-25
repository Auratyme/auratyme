"""UI state and canonical input models for Analytics Control Center.

Educational Rationale:
Structured, explicit schemas reduce accidental coupling and
simplify validation, persistence (presets), and transformation
into API payloads. Each model keeps a single responsibility.
"""
from __future__ import annotations
import os
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any
import math

SCHEMA_VERSION = 1

class CanonicalInput(BaseModel):
    """Single task/event row user can edit in the Inputs page."""
    date: str = Field(default="2025-01-01", description="ISO date YYYY-MM-DD")
    task_type: str = Field(default="Task", description="Domain category or label")
    start_time: Optional[str] = Field(default="09:00", description="HH:MM start (optional if duration)")
    end_time: Optional[str] = Field(default="10:00", description="HH:MM end (optional if duration)")
    duration: Optional[int] = Field(default=60, ge=0, description="Minutes if no end_time")
    task_priority: int = Field(default=3, ge=1, le=5)
    breaks_count: int = Field(default=0, ge=0)
    breaks_duration: int = Field(default=0, ge=0)
    sleep_duration: Optional[int] = Field(default=None, ge=0)
    sleep_quality: Optional[str] = Field(default=None)
    energy_level: Optional[int] = Field(default=None, ge=1, le=5)
    fatigue_level: Optional[int] = Field(default=None, ge=1, le=5)
    motivation_level: Optional[int] = Field(default=None, ge=1, le=5)
    mood: Optional[str] = Field(default=None)
    fixed_task: bool = Field(default=False)
    efficiency_score: Optional[float] = Field(default=None, ge=0)
    no_overlaps: bool = Field(default=True)
    enforce_total_minutes: bool = Field(default=True)
    rounding_flag: bool = Field(default=True)

    @field_validator('task_priority', 'breaks_count', 'breaks_duration', mode='before')
    @classmethod
    def clean_numeric_fields(cls, v):
        """Clean numeric fields from NaN/None values."""
        if v is None or (isinstance(v, float) and math.isnan(v)):
            return 3 if 'task_priority' in cls.model_fields else 0
        return int(v)
    
    @field_validator('duration', 'sleep_duration', 'energy_level', 'fatigue_level', 'motivation_level', mode='before')
    @classmethod
    def clean_optional_numeric_fields(cls, v):
        """Clean optional numeric fields from NaN values."""
        if v is None:
            return None
        if isinstance(v, float) and math.isnan(v):
            return None
        return int(v)
    
    @field_validator('efficiency_score', mode='before')
    @classmethod
    def clean_optional_float_fields(cls, v):
        """Clean optional float fields from NaN values."""
        if v is None:
            return None
        if isinstance(v, float) and math.isnan(v):
            return None
        return float(v)

    @field_validator('fixed_task', 'no_overlaps', 'enforce_total_minutes', 'rounding_flag', mode='before')  
    @classmethod
    def clean_boolean_fields(cls, v):
        """Clean boolean fields from None values."""
        if v is None:
            return False  # Default for all boolean fields
        return bool(v)

    @field_validator('date', 'task_type', 'start_time', 'end_time', 'sleep_quality', 'mood', mode='before')
    @classmethod  
    def clean_string_fields(cls, v):
        """Clean string fields from None values."""
        if v is None:
            return None  # Allow None for optional fields
        return str(v)

class InputCollection(BaseModel):
    """Collection of canonical inputs plus global flags."""
    items: List[CanonicalInput] = Field(default_factory=list)
    rounding: bool = True

class PresetStore(BaseModel):
    """In-memory preset store referenced in session state."""
    presets: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    version: int = SCHEMA_VERSION

class EnergyWindow(BaseModel):
    """Configurable high-focus energy window (start-end HH:MM)."""
    start: str = Field(..., description="HH:MM start of window")
    end: str = Field(..., description="HH:MM end of window")

class AppState(BaseModel):
    """Session-wide mutable application state container."""
    api_base_url: str = os.getenv("API_BASE_URL", "http://localhost:8000")
    timeout_seconds: int = 300
    current_inputs: InputCollection = Field(default_factory=InputCollection)
    last_request: Optional[Dict[str, Any]] = None
    last_response: Optional[Dict[str, Any]] = None
    last_latency_ms: Optional[float] = None
    deep_internals: Optional[Dict[str, Any]] = None
    api_client: Any | None = None
    preset_store: Optional[PresetStore] = None
    prime_windows: List[EnergyWindow] = Field(
        default_factory=lambda: [
            EnergyWindow(start="09:00", end="12:00"),
            EnergyWindow(start="14:00", end="17:00"),
        ],
        description="Configurable energy prime windows",
    )
    wearable_data: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Manually entered or uploaded smartwatch/wearable data"
    )

    def load_inputs(self, data: Dict[str, Any]) -> None:
        self.current_inputs = InputCollection(**data)
