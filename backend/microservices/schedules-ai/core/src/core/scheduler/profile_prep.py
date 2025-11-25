"""
User profile preparation for schedule generation.

This module handles extraction and validation of user chronotype context
from various data sources, including energy curve generation.

Educational Note:
    Refactored to use simplified ScheduleChronotypeContext instead of
    complex ChronotypeProfile, focusing only on essential chronotype
    classification data needed for scheduling.
    
    NEW: Integrates energy curve generation from chronotype to provide
    realistic 24-hour energy patterns for energy-aware task scheduling.
"""

import logging
from typing import TYPE_CHECKING, Optional

from src.core.chronotype import Chronotype
from src.core.chronotype.energy_curve import generate_energy_curve_from_chronotype
from src.utils.time_utils import time_to_total_minutes

if TYPE_CHECKING:
    from src.core.chronotype import ChronotypeAnalyzer
    from src.core.scheduler.models import ScheduleInputData, ScheduleChronotypeContext
    from src.core.sleep import SleepMetrics

logger = logging.getLogger(__name__)


def prepare_chronotype_context(
    input_data: "ScheduleInputData",
    chronotype_analyzer: "ChronotypeAnalyzer"
) -> "ScheduleChronotypeContext":
    """
    Creates chronotype context from MEQ data or defaults.
    
    Educational Note:
        Simplified to use analyze_meq() which returns both chronotype
        and prime window in one call, reducing complexity and improving
        maintainability.
        
        NOTE: Energy pattern is initially empty and will be populated
        later by add_energy_pattern_to_context() once sleep metrics
        are calculated. This maintains proper initialization order.
    """
    from src.core.scheduler.models import ScheduleChronotypeContext
    
    meq_score = _extract_meq_score(input_data)
    
    logger.info(f"\n{'='*80}\n🧬 CHRONOTYPE CALCULATION\n{'='*80}")
    logger.info(f"MEQ Score from input: {meq_score if meq_score is not None else 'NOT PROVIDED'}")
    
    chronotype, prime_window = chronotype_analyzer.analyze_meq(meq_score)
    
    logger.info(f"✅ Calculated Chronotype: {chronotype.value}")
    logger.info(f"✅ Prime Window: {prime_window.start.strftime('%H:%M')} - {prime_window.end.strftime('%H:%M')}")
    logger.info(f"{'='*80}\n")
    
    return ScheduleChronotypeContext(
        user_id=input_data.user_id,
        chronotype=chronotype,
        prime_window=prime_window,
        energy_pattern={},
        source="meq" if meq_score is not None else "default"
    )


def add_energy_pattern_to_context(
    chronotype_context: "ScheduleChronotypeContext",
    sleep_metrics: "SleepMetrics"
) -> "ScheduleChronotypeContext":
    """
    Adds realistic energy curve to chronotype context.
    
    Educational Note:
        This function is called AFTER sleep calculation to generate
        24-hour energy pattern based on chronotype and sleep schedule.
        
        Energy pattern replaces flat 0.5 values with realistic circadian
        rhythm curve that respects prime windows and sleep times, enabling
        energy-aware task scheduling.
    """
    from src.core.scheduler.models import ScheduleChronotypeContext
    
    sleep_bedtime_min = time_to_total_minutes(sleep_metrics.ideal_bedtime)
    sleep_wake_min = time_to_total_minutes(sleep_metrics.ideal_wake_time)
    
    energy_pattern = generate_energy_curve_from_chronotype(
        chronotype=chronotype_context.chronotype,
        prime_window=chronotype_context.prime_window,
        sleep_bedtime_minutes=sleep_bedtime_min,
        sleep_wake_minutes=sleep_wake_min
    )
    
    return ScheduleChronotypeContext(
        user_id=chronotype_context.user_id,
        chronotype=chronotype_context.chronotype,
        prime_window=chronotype_context.prime_window,
        energy_pattern=energy_pattern,
        source=chronotype_context.source
    )


def _extract_meq_score(input_data: "ScheduleInputData") -> Optional[int]:
    """
    Extracts MEQ score from input data with fallback.
    
    Educational Note:
        Multiple extraction paths support different API versions
        and client implementations without breaking changes.
    """
    try:
        if input_data.user_profile_data:
            meq = input_data.user_profile_data.get("meq_score")
            if meq is not None:
                return int(meq)
        
        if input_data.preferences:
            meq = input_data.preferences.get("meq_score")
            if meq is not None:
                return int(meq)
    except (ValueError, TypeError) as err:
        logger.warning(f"Invalid MEQ score format: {err}")
    
    return None
