"""Enhanced data models for Analytics Control Center.

Educational Rationale:
Separates user-provided data from algorithm-computed data to maintain
clear data flow and enable better debugging of the schedule generation
process. Each model has a single responsibility and clear validation rules.
"""
from __future__ import annotations
import os
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any
from datetime import datetime

SCHEMA_VERSION = 2

class UserProfileData(BaseModel):
    """Complete user profile and preferences provided by the user."""
    # Basic Profile
    name: str = Field(default="User", description="Full name of the user")
    age: int = Field(default=30, ge=16, le=100, description="Age in years")
    role: str = Field(default="", description="User role/title")
    industry: str = Field(default="", description="Industry/sector")
    meq_score: int = Field(default=50, ge=16, le=86, description="Morningness–eveningness questionnaire score")
    sleep_need: str = Field(default="medium", description="Sleep need level: low, medium, or high")
    
    # Work Preferences
    start_time: str = Field(default="08:00", description="Work start time (HH:MM)")
    end_time: str = Field(default="17:00", description="Work end time (HH:MM)")
    commute_minutes: int = Field(default=30, ge=0, description="Daily commute duration in minutes")
    location: str = Field(default="Office", description="Work location setting")
    type: str = Field(default="office", description="Work type (office/hybrid/remote)")
    
    # Meal Preferences (only lunch - breakfast/dinner in routines)
    lunch_duration_minutes: int = Field(default=45, ge=15, le=120, description="Lunch duration")
    
    # Routines (morning includes breakfast, evening includes dinner)
    morning_duration_minutes: int = Field(default=30, ge=10, le=120, description="Morning routine duration including breakfast")
    evening_duration_minutes: int = Field(default=45, ge=10, le=120, description="Evening routine duration including dinner")

    @field_validator('start_time', 'end_time', mode='before')
    @classmethod
    def validate_time_format(cls, v):
        """Validate HH:MM time format."""
        if v and isinstance(v, str):
            try:
                parts = v.split(':')
                if len(parts) == 2:
                    hour, minute = int(parts[0]), int(parts[1])
                    if 0 <= hour <= 23 and 0 <= minute <= 59:
                        return f"{hour:02d}:{minute:02d}"
            except ValueError:
                pass
        return "09:00"  # Default fallback

class TaskForSchedule(BaseModel):
    """Simplified task data for schedule generation."""
    title: str = Field(..., description="Task title")
    priority: int = Field(default=3, ge=1, le=5, description="Priority level 1=Highest, 5=Lowest")
    duration_hours: float = Field(..., ge=0.25, le=12.0, description="Task duration in hours")
    is_fixed_time: bool = Field(default=False, description="Whether timing cannot be changed")
    start_time: Optional[str] = Field(default=None, description="Fixed start time (HH:MM) - only if is_fixed_time=True")
    end_time: Optional[str] = Field(default=None, description="Fixed end time (HH:MM) - only if is_fixed_time=True")
    
    @field_validator('priority', mode='before')
    @classmethod 
    def clean_priority(cls, v):
        """Clean priority from various inputs."""
        if v is None or (isinstance(v, float) and (v != v or str(v).lower() == 'nan')):  # Check for NaN
            return 3
        try:
            return int(float(v))
        except (ValueError, TypeError):
            return 3

    @field_validator('duration_hours', mode='before')
    @classmethod
    def clean_duration(cls, v):
        """Clean duration from various inputs."""
        if v is None or (isinstance(v, float) and (v != v or str(v).lower() == 'nan')):  # Check for NaN
            return 1.0
        if isinstance(v, str):
            try:
                return float(v)
            except ValueError:
                return 1.0
        try:
            return float(v)
        except (ValueError, TypeError):
            return 1.0

    @field_validator('is_fixed_time', mode='before')
    @classmethod
    def clean_fixed_time(cls, v):
        """Clean fixed time from various inputs."""
        if v is None or (isinstance(v, float) and (v != v or str(v).lower() == 'nan')):  # Check for NaN
            return False
        return bool(v)

    @field_validator('start_time', 'end_time', mode='before')
    @classmethod
    def validate_time_fields(cls, v):
        """Validate and clean time fields for fixed-time tasks."""
        if v is None or v == "" or (isinstance(v, float) and (v != v or str(v).lower() == 'nan')):
            return None
        
        if isinstance(v, str):
            # Handle various time formats and convert to HH:MM
            if ':' in v:
                # Remove seconds if present (HH:MM:SS -> HH:MM)
                time_parts = v.split(':')
                if len(time_parts) >= 2:
                    try:
                        hour = int(time_parts[0])
                        minute = int(time_parts[1])
                        if 0 <= hour <= 23 and 0 <= minute <= 59:
                            return f"{hour:02d}:{minute:02d}"
                    except ValueError:
                        pass
            # Handle HH format (add :00)
            elif v.isdigit() and 0 <= int(v) <= 23:
                return f"{int(v):02d}:00"
        
        return None
    
    def get_duration_display(self) -> str:
        """
        Convert duration_hours to human-readable format (Xh Ym).
        
        Returns:
            str: Duration in format like "1h 30m" or "45m"
            
        Educational Note:
            Provides user-friendly time display instead of decimal hours.
        """
        total_minutes = int(self.duration_hours * 60)
        hours = total_minutes // 60
        minutes = total_minutes % 60
        
        if hours > 0 and minutes > 0:
            return f"{hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h"
        else:
            return f"{minutes}m"

class WearableData(BaseModel):
    """Raw wearable device data from user."""
    sleep_quality: str = Field(default="Good", description="Sleep quality rating")
    stress_level: str = Field(default="Low", description="Current stress level")
    readiness_score: float = Field(default=0.8, ge=0.0, le=1.0, description="Overall readiness score")
    steps_yesterday: int = Field(default=8000, ge=0, description="Steps from previous day")
    avg_heart_rate: int = Field(default=70, ge=40, le=200, description="Average heart rate in bpm")
    sleep_duration_hours: float = Field(default=8.0, ge=3.0, le=12.0, description="Actual sleep duration")
    deep_sleep_percentage: int = Field(default=20, ge=0, le=100, description="Deep sleep percentage")
    rem_sleep_percentage: int = Field(default=20, ge=0, le=100, description="REM sleep percentage")
    recovery_index: int = Field(default=80, ge=0, le=100, description="Recovery index percentage")
    
    @field_validator('sleep_quality', mode='before')
    @classmethod
    def validate_sleep_quality(cls, v):
        """Ensure valid sleep quality options."""
        valid_options = ["Poor", "Fair", "Good", "Excellent"]
        if v in valid_options:
            return v
        return "Good"
    
    @field_validator('stress_level', mode='before') 
    @classmethod
    def validate_stress_level(cls, v):
        """Ensure valid stress level options."""
        valid_options = ["Very Low", "Low", "Moderate", "High", "Very High"]
        if v in valid_options:
            return v
        return "Low"

class ComputedAlgorithmData(BaseModel):
    """Data computed by our algorithms - READ ONLY for user."""
    # Energy & Performance (computed from chronotype + wearable data)
    energy_level: Optional[int] = Field(default=None, ge=1, le=5, description="Computed energy level")
    fatigue_level: Optional[int] = Field(default=None, ge=1, le=5, description="Computed fatigue level") 
    motivation_level: Optional[int] = Field(default=None, ge=1, le=5, description="Computed motivation level")
    
    # Optimal Timing Windows (computed from chronotype analysis)
    optimal_work_windows: List[str] = Field(default_factory=list, description="Computed optimal work periods")
    optimal_break_times: List[str] = Field(default_factory=list, description="Suggested break times")
    focus_blocks: List[Dict[str, str]] = Field(default_factory=list, description="Deep focus time blocks")
    
    # Sleep Analysis (computed from sleep calculator)
    recommended_bedtime: Optional[str] = Field(default=None, description="Computed optimal bedtime")
    recommended_wake_time: Optional[str] = Field(default=None, description="Computed optimal wake time")
    sleep_quality_score: Optional[float] = Field(default=None, ge=0.0, le=100.0, description="Computed sleep quality")
    
    # Schedule Metrics (computed after schedule generation)  
    schedule_efficiency: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Overall schedule efficiency")
    energy_alignment_score: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Energy-task alignment")
    break_density: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Break distribution quality")
    
    # Chronotype Analysis Results
    detected_chronotype: Optional[str] = Field(default=None, description="Detected chronotype")
    chronotype_confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Chronotype confidence")

class InputCollection(BaseModel):
    """Collection of all input data types."""
    user_profile: UserProfileData = Field(default_factory=UserProfileData)
    tasks: List[TaskForSchedule] = Field(default_factory=list)
    wearable_data: Optional[WearableData] = Field(default=None)
    algorithm_results: ComputedAlgorithmData = Field(default_factory=ComputedAlgorithmData)
    target_date: str = Field(default_factory=lambda: datetime.now().date().isoformat(), description="Target date for schedule generation (YYYY-MM-DD)")

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
    # Legacy support for existing smartwatch functionality
    wearable_data: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Manually entered or uploaded smartwatch/wearable data (legacy)"
    )

    def load_inputs(self, data: Dict[str, Any]) -> None:
        """Load input data from dictionary."""
        if 'user_profile' in data:
            self.current_inputs.user_profile = UserProfileData(**data['user_profile'])
        if 'tasks' in data:
            self.current_inputs.tasks = [TaskForSchedule(**task) for task in data['tasks']]
        if 'wearable_data' in data:
            self.current_inputs.wearable_data = WearableData(**data['wearable_data'])
