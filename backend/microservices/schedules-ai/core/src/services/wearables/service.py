"""
Wearable Service main class.

Provides high-level interface for accessing processed wearable data.

Educational Note:
    Service layer coordinates adapters and calculators,
    delegating actual processing to specialized modules.
"""

import logging
from datetime import date
from typing import Any, Dict, Optional
from uuid import UUID

from .models import ProcessedWearableData
from .config import get_sleep_window_hours
from .processor import process_wearable_data

logger = logging.getLogger(__name__)


def validate_dependencies(sleep_calculator: Any) -> None:
    """
    Validates service dependencies at initialization.
    
    Educational Note:
        Fail-fast validation prevents runtime errors deep in
        processing pipeline, improving debugging experience.
    """
    try:
        from src.core.sleep import SleepCalculator
        
        if not isinstance(sleep_calculator, SleepCalculator):
            raise TypeError("sleep_calculator must be SleepCalculator instance")
            
    except ImportError:
        raise ImportError(
            "WearableService requires core dependencies (SleepCalculator)"
        )


class WearableService:
    """
    Orchestrates wearable data fetching and processing.
    
    Educational Note:
        Thin service layer delegates heavy lifting to processor,
        keeping class focused on initialization and coordination.
    """
    
    def __init__(
        self,
        device_adapter: Any,
        sleep_calculator: Any,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Initializes wearable service.
        
        Args:
            device_adapter: Adapter for device data access
            sleep_calculator: Calculator for sleep analysis
            config: Optional configuration dictionary
            
        Raises:
            ImportError: If core dependencies unavailable
            TypeError: If dependencies wrong type
            
        Educational Note:
            Service initialization focuses on dependency injection
            and configuration, not business logic.
        """
        validate_dependencies(sleep_calculator)
        
        self.device_adapter = device_adapter
        self.sleep_calculator = sleep_calculator
        self._config = config or {}
        
        self._sleep_window_start_hour, self._sleep_window_end_hour = (
            get_sleep_window_hours(self._config)
        )
        
        logger.info(
            f"WearableService initialized. Sleep window: "
            f"{self._sleep_window_start_hour:02d}:00-"
            f"{self._sleep_window_end_hour:02d}:00 UTC"
        )
    
    async def get_processed_data_for_day(
        self,
        user_id: UUID,
        target_date: date,
        preferred_source: Any,
        recommended_sleep: Optional[Any] = None,
    ) -> ProcessedWearableData:
        """
        Fetches and processes wearable data for user and date.
        
        Args:
            user_id: User identifier
            target_date: Date to process data for
            preferred_source: Preferred data source (DataSource enum)
            recommended_sleep: Recommended sleep for quality analysis
            
        Returns:
            Processed wearable data with all available metrics
            
        Educational Note:
            Service method is thin wrapper delegating to processor,
            following single responsibility principle.
        """
        return await process_wearable_data(
            device_adapter=self.device_adapter,
            sleep_calculator=self.sleep_calculator,
            user_id=user_id,
            target_date=target_date,
            preferred_source=preferred_source,
            recommended_sleep=recommended_sleep,
            window_start_hour=self._sleep_window_start_hour,
            window_end_hour=self._sleep_window_end_hour
        )
