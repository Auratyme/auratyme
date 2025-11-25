"""
LLM integration package for schedule generation and refinement.

Provides configuration models, prompt templates, and utilities for integrating
Large Language Models into the schedule optimization pipeline.

Educational Note:
    This package separates LLM concerns (models, templates, parsing) from
    core scheduling logic, enabling independent testing and evolution of
    prompt engineering strategies without impacting solver or task logic.
"""

from .models import (
    ModelConfig,
    ModelProvider,
    ScheduleGenerationContext,
    SleepMetrics,
    Chronotype,
    PrimeWindow,
    Task,
    TaskPriority,
    EnergyLevel,
    RAGContext,
    RetrievedContext,
    ScheduledTaskInfo
)

from .templates import (
    GENERATE_FROM_SCRATCH_TEMPLATE,
    REFINE_SCHEDULE_TEMPLATE,
    initialize_templates
)

from .parser import (
    extract_valid_json,
    clean_json_text,
    find_json_start,
    scan_for_balanced_close
)

from .validator import validate_llm_schedule

from .engine import LLMEngine


__all__ = [
    "ModelConfig",
    "ModelProvider",
    "ScheduleGenerationContext",
    "SleepMetrics",
    "Chronotype",
    "PrimeWindow",
    "Task",
    "TaskPriority",
    "EnergyLevel",
    "RAGContext",
    "RetrievedContext",
    "ScheduledTaskInfo",
    "GENERATE_FROM_SCRATCH_TEMPLATE",
    "REFINE_SCHEDULE_TEMPLATE",
    "initialize_templates",
    "extract_valid_json",
    "clean_json_text",
    "find_json_start",
    "scan_for_balanced_close",
    "validate_llm_schedule",
    "LLMEngine",
]
