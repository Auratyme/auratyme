"""
LLM configuration and context models for schedule generation.

This module defines core data structures for LLM integration including provider
enumeration, configuration settings, and comprehensive scheduling context that
aggregates user profile, preferences, tasks, and insights.

Educational Note:
    Separating configuration models from business logic enables easier testing,
    validation, and environment-specific adjustments without code changes.
"""

import logging
import os
from dataclasses import dataclass, field
from datetime import date, time, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from pydantic import Field, HttpUrl, validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


def import_sleep_metrics():
    """
    Dynamically imports SleepMetrics with fallback to dummy implementation.
    
    Returns:
        Type: SleepMetrics class or dummy replacement
        
    Educational Note:
        Lazy imports prevent circular dependencies and allow graceful
        degradation when optional dependencies are unavailable.
    """
    try:
        from src.core.sleep import SleepMetrics
        return SleepMetrics
    except ImportError:
        @dataclass
        class DummySleepMetrics:
            ideal_duration: Optional[timedelta] = None
            ideal_bedtime: Optional[time] = None
            ideal_wake_time: Optional[time] = None
        logger.warning("SleepMetrics unavailable, using dummy")
        return DummySleepMetrics


def import_chronotype_models():
    """
    Dynamically imports chronotype models with fallback implementations.
    
    Returns:
        tuple: (Chronotype, PrimeWindow) classes or dummies
        
    Educational Note:
        Simplified to import only essential chronotype types after
        removal of complex ChronotypeProfile.
    """
    try:
        from src.core.chronotype import Chronotype, PrimeWindow
        return Chronotype, PrimeWindow
    except ImportError:
        class DummyChronotype(Enum):
            UNKNOWN = "unknown"
            EARLY_BIRD = "early_bird"
            INTERMEDIATE = "intermediate"
            NIGHT_OWL = "night_owl"
        
        @dataclass
        class DummyPrimeWindow:
            start: time = time(10, 0)
            end: time = time(14, 0)
            chronotype: str = "unknown"
            
        logger.warning("Chronotype models unavailable, using dummies")
        return DummyChronotype, DummyPrimeWindow


def import_task_models():
    """
    Dynamically imports task models with fallback implementations.
    
    Returns:
        tuple: (Task, TaskPriority, EnergyLevel) classes or dummies
    """
    try:
        from src.core.task import Task, TaskPriority, EnergyLevel
        return Task, TaskPriority, EnergyLevel
    except ImportError:
        @dataclass
        class DummyTask:
            id: UUID
            title: str
            duration: timedelta
            
        class DummyTaskPriority(Enum):
            MEDIUM = 3
            
        class DummyEnergyLevel(Enum):
            MEDIUM = 2
            
        logger.warning("Task models unavailable, using dummies")
        return DummyTask, DummyTaskPriority, DummyEnergyLevel


def import_rag_models():
    """
    Dynamically imports RAG context models with fallback implementations.
    
    Returns:
        tuple: (RAGContext, RetrievedContext) classes or dummies
    """
    try:
        from src.adapters.rag_adapter import RAGContext, RetrievedContext
        return RAGContext, RetrievedContext
    except ImportError:
        @dataclass
        class DummyRetrievedContext:
            content: str
            source: str
            
        @dataclass
        class DummyRAGContext:
            research_snippets: List[DummyRetrievedContext] = field(default_factory=list)
            best_practices: List[str] = field(default_factory=list)
            
        logger.warning("RAG models unavailable, using dummies")
        return DummyRAGContext, DummyRetrievedContext


def import_solver_models():
    """
    Dynamically imports solver models with fallback implementations.
    
    Returns:
        Type: ScheduledTaskInfo class or dummy
    """
    try:
        from src.core.solver import ScheduledTaskInfo
        return ScheduledTaskInfo
    except ImportError:
        @dataclass
        class DummyScheduledTaskInfo:
            task_id: UUID
            start_time: time
            end_time: time
            task_date: date
            
        logger.warning("Solver models unavailable, using dummy")
        return DummyScheduledTaskInfo


SleepMetrics = import_sleep_metrics()
Chronotype, PrimeWindow = import_chronotype_models()
Task, TaskPriority, EnergyLevel = import_task_models()
RAGContext, RetrievedContext = import_rag_models()
ScheduledTaskInfo = import_solver_models()


class ModelProvider(Enum):
    """
    Enumeration of supported LLM providers.
    
    Educational Note:
        Using enums for provider selection ensures type safety and makes
        adding new providers straightforward through extension.
    """
    OPENAI = "openai"
    MISTRAL = "mistral"
    HUGGINGFACE = "huggingface"
    ANTHROPIC = "anthropic"
    LOCAL = "local"
    OPENROUTER = "openrouter"


class ModelConfig(BaseSettings):
    """
    Pydantic configuration model for LLM integration settings.
    
    Loads settings from environment variables with sensible defaults and
    performs validation to ensure API keys and endpoints are properly configured.
    
    Educational Note:
        Pydantic Settings pattern combines environment variable management,
        validation, and type safety in a single declarative configuration class.
    """
    llm_provider: ModelProvider = Field(default=ModelProvider.OPENROUTER, alias="LLM_PROVIDER")
    llm_model_name: Optional[str] = Field(default=None, alias="LLM_MODEL_NAME")
    
    openai_api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY", validate_default=False)
    mistral_api_key: Optional[str] = Field(default=None, alias="MISTRAL_API_KEY", validate_default=False)
    huggingface_api_key: Optional[str] = Field(default=None, alias="HUGGINGFACE_API_KEY", validate_default=False)
    anthropic_api_key: Optional[str] = Field(default=None, alias="ANTHROPIC_API_KEY", validate_default=False)
    openrouter_api_key: Optional[str] = Field(default=None, alias="OPENROUTER_API_KEY", validate_default=False)
    
    llm_api_base: Optional[Union[HttpUrl, str]] = Field(default=None, alias="LLM_API_BASE")
    llm_temperature: float = Field(default=0.3, ge=0.0, le=2.0, alias="LLM_TEMPERATURE")
    llm_max_tokens: int = Field(default=2048, gt=0, alias="LLM_MAX_TOKENS")
    llm_top_p: float = Field(default=0.9, ge=0.0, le=1.0, alias="LLM_TOP_P")
    llm_max_retries: int = Field(default=3, ge=0, alias="LLM_MAX_RETRIES")
    llm_retry_delay: float = Field(default=1.5, ge=0.0, alias="LLM_RETRY_DELAY")
    llm_site_url: Optional[str] = Field(default=None, alias="LLM_SITE_URL")
    llm_site_name: Optional[str] = Field(default=None, alias="LLM_SITE_NAME")
    llm_request_timeout: float = Field(default=60.0, gt=0, alias="LLM_REQUEST_TIMEOUT")
    
    api_key: Optional[str] = None
    api_base: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(__file__), '..', '..', '..', '.env.dev'),
        env_file_encoding='utf-8',
        case_sensitive=False,
        extra='ignore'
    )

    @validator('llm_model_name', pre=True, always=True)
    def set_default_model_name(cls, v, values):
        """
        Sets provider-specific default model names when not explicitly configured.
        
        Educational Note:
            Validators enable complex field interdependencies and smart defaults
            based on other field values.
        """
        provider = values.get('llm_provider')
        if v is None:
            defaults = {
                ModelProvider.MISTRAL: "mistralai/Mistral-7B-Instruct-v0.1",
                ModelProvider.OPENAI: "gpt-3.5-turbo",
                ModelProvider.ANTHROPIC: "claude-3-haiku-20240307",
                ModelProvider.HUGGINGFACE: "mistralai/Mistral-7B-Instruct-v0.1",
                ModelProvider.OPENROUTER: "nvidia/nemotron-nano-9b-v2:free",
                ModelProvider.LOCAL: "local-model"
            }
            return defaults.get(provider)
        return v

    def model_post_init(self, __context: Any) -> None:
        """
        Post-initialization hook to resolve API keys and base URLs.
        
        Educational Note:
            model_post_init runs after Pydantic validation, enabling complex
            setup logic that depends on validated field values.
        """
        provider_key_map = {
            ModelProvider.OPENAI: self.openai_api_key,
            ModelProvider.MISTRAL: self.mistral_api_key,
            ModelProvider.HUGGINGFACE: self.huggingface_api_key,
            ModelProvider.ANTHROPIC: self.anthropic_api_key,
            ModelProvider.OPENROUTER: self.openrouter_api_key,
        }
        self.api_key = provider_key_map.get(self.llm_provider)
        
        if self.llm_provider != ModelProvider.LOCAL and not self.api_key:
            env_var_name = f"{self.llm_provider.value.upper()}_API_KEY"
            logger.warning(f"API key for {self.llm_provider.value} not found via '{env_var_name}'")
            
        if self.llm_api_base:
            self.api_base = str(self.llm_api_base)
        elif self.llm_provider != ModelProvider.LOCAL:
            default_bases = {
                ModelProvider.OPENAI: "https://api.openai.com/v1",
                ModelProvider.MISTRAL: "https://api.mistral.ai/v1",
                ModelProvider.ANTHROPIC: "https://api.anthropic.com/v1",
                ModelProvider.HUGGINGFACE: "https://api-inference.huggingface.co/models",
                ModelProvider.OPENROUTER: "https://openrouter.ai/api/v1"
            }
            self.api_base = default_bases.get(self.llm_provider)
            
        logger.debug(f"ModelConfig: {self.llm_provider.value}, {self.llm_model_name}, Key={bool(self.api_key)}")


@dataclass
class ScheduleGenerationContext:
    """
    Comprehensive context aggregating all inputs for LLM schedule generation.
    
    Bundles chronotype, prime window, preferences, tasks, events, sleep recommendations,
    wearable data, historical patterns, and RAG-retrieved context into a single
    cohesive structure for prompt template rendering.
    
    Educational Note:
        Context objects follow the Parameter Object pattern, reducing function
        signatures and enabling flexible context extension without breaking changes.
        Refactored to use simplified chronotype/prime_window instead of complex profile.
    """
    user_id: UUID
    user_name: str
    target_date: date
    chronotype: Optional[Any] = None  # Chronotype enum
    prime_window: Optional[Any] = None  # PrimeWindow dataclass
    preferences: Dict[str, Any] = field(default_factory=dict)
    tasks: List[Task] = field(default_factory=list)  # type: ignore
    fixed_events: List[Dict[str, Any]] = field(default_factory=list)
    sleep_recommendation: Optional[SleepMetrics] = None  # type: ignore
    energy_pattern: Optional[Dict[int, float]] = None
    wearable_insights: Dict[str, Any] = field(default_factory=dict)
    historical_insights: Dict[str, Any] = field(default_factory=dict)
    rag_context: Optional[RAGContext] = None  # type: ignore
    previous_feedback: Optional[Dict[str, Any]] = None
