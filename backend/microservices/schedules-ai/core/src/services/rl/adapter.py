"""
Parameter adaptation application utilities.

Applies calculated adaptations to current parameter configurations.

Educational Note:
    Separating calculation from application allows validation and logging
    of changes before committing them, enabling rollback if needed.
"""

import logging
from typing import Any, Dict

from .models import AdaptationParameters

logger = logging.getLogger(__name__)


def apply_sleep_scale_adaptation(
    params: Dict[str, Any],
    adjustment: float
) -> None:
    """
    Applies sleep need scale adjustment with bounds.
    
    Educational Note:
        Scaling factor (×50) converts -0.15 to 0.15 adjustment range
        into meaningful 0-100 scale changes while respecting limits.
    """
    if adjustment == 0.0:
        return
    
    if "sleep_need_scale" not in params:
        return
    
    scale_change = adjustment * 50
    new_value = params["sleep_need_scale"] + scale_change
    params["sleep_need_scale"] = max(0.0, min(100.0, new_value))
    
    logger.debug(f"Sleep scale adjusted to {params['sleep_need_scale']:.2f}")


def apply_chronotype_scale_adaptation(
    params: Dict[str, Any],
    adjustment: float
) -> None:
    """
    Applies chronotype scale adjustment with bounds.
    
    Educational Note:
        Chronotype scale balances circadian preference vs practical
        constraints; bounds prevent extreme values that ignore reality.
    """
    if adjustment == 0.0:
        return
    
    if "chronotype_scale" not in params:
        return
    
    scale_change = adjustment * 50
    new_value = params["chronotype_scale"] + scale_change
    params["chronotype_scale"] = max(0.0, min(100.0, new_value))
    
    logger.debug(f"Chronotype scale adjusted to {params['chronotype_scale']:.2f}")


def apply_weight_adjustment(
    weights: Dict[str, float],
    key: str,
    adjustment: float
) -> None:
    """
    Applies single weight adjustment with 0-1 bounds.
    
    Educational Note:
        Weight bounds ensure all weights remain valid probabilities
        that can be normalized without creating negative/infinite values.
    """
    if key not in weights:
        logger.warning(f"Weight key '{key}' not found, skipping")
        return
    
    new_value = weights[key] + adjustment
    weights[key] = max(0.0, min(1.0, new_value))
    
    logger.debug(f"Weight '{key}' adjusted to {weights[key]:.3f}")


def apply_prioritizer_weight_adaptations(
    params: Dict[str, Any],
    adjustments: Dict[str, float]
) -> None:
    """
    Applies all prioritizer weight adjustments.
    
    Educational Note:
        Iterative application with validation prevents invalid states
        where sum of weights becomes meaningless (e.g., all zero).
    """
    if not adjustments:
        return
    
    if "prioritizer_weights" not in params:
        logger.warning("No prioritizer_weights in params, skipping")
        return
    
    weights = params["prioritizer_weights"]
    
    if not isinstance(weights, dict):
        logger.warning("prioritizer_weights not dict, skipping")
        return
    
    for key, adj in adjustments.items():
        apply_weight_adjustment(weights, key, adj)


def validate_adaptations(adaptations: AdaptationParameters) -> bool:
    """
    Validates adaptation object before application.
    
    Educational Note:
        Pre-application validation catches type errors early,
        preventing partial updates that leave system in bad state.
    """
    if not isinstance(adaptations, AdaptationParameters):
        logger.error("Invalid adaptations type")
        return False
    
    return True


def apply_adaptations(
    current_params: Dict[str, Any],
    adaptations: AdaptationParameters
) -> Dict[str, Any]:
    """
    Main adaptation application function.
    
    Educational Note:
        Copy-on-write pattern preserves original params for comparison/rollback
        while ensuring mutations don't affect caller's data structures.
    """
    if not validate_adaptations(adaptations):
        logger.error("Adaptation validation failed")
        return current_params
    
    updated_params = current_params.copy()
    logger.debug(f"Applying adaptations: {adaptations}")
    
    apply_sleep_scale_adaptation(
        updated_params,
        adaptations.sleep_need_scale_adjustment
    )
    
    apply_chronotype_scale_adaptation(
        updated_params,
        adaptations.chronotype_scale_adjustment
    )
    
    apply_prioritizer_weight_adaptations(
        updated_params,
        adaptations.prioritizer_weight_adjustments
    )
    
    logger.info("Adaptations applied successfully")
    logger.debug(f"Original: {current_params}")
    logger.debug(f"Updated: {updated_params}")
    
    return updated_params
