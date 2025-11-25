"""
Wearable data processing package.

Provides service for fetching and processing wearable device data
including sleep analysis, activity metrics, and physiological data.

Educational Note:
    Package structure separates concerns (models, config, processing,
    metrics) enabling independent testing and maintenance.

Usage:
    from src.services.wearables import WearableService, ProcessedWearableData

    service = WearableService(device_adapter, sleep_calculator, config)
    data = await service.get_processed_data_for_day(user_id, date, source)
"""

from .models import ProcessedWearableData, format_timedelta
from .service import WearableService

__all__ = [
    "WearableService",
    "ProcessedWearableData",
    "format_timedelta",
]
