"""
Integration test comparing old chronotype.py with new chronotype/ package.

This test verifies that the refactored chronotype package produces identical
behavior to the original chronotype.py module.
"""

import logging
import sys
from datetime import datetime, timedelta, timezone
from uuid import uuid4

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_old_module():
    """
    Test old chronotype_legacy.py module.

    Educational Note:
        Imports from deprecated module to capture baseline behavior
        for comparison with refactored implementation.
    """
    from src.core.chronotype_legacy import (
        Chronotype,
        ChronotypeAnalyzer,
        ChronotypeProfile,
    )

    analyzer = ChronotypeAnalyzer()

    meq_score = 65
    chronotype_meq = analyzer.determine_chronotype_from_meq(meq_score)

    user_tz = timezone(timedelta(hours=2))
    sleep_data = [
        (
            datetime(2024, 1, 10, 22, 0, tzinfo=timezone.utc),
            datetime(2024, 1, 11, 6, 0, tzinfo=timezone.utc),
        ),
        (
            datetime(2024, 1, 11, 22, 15, tzinfo=timezone.utc),
            datetime(2024, 1, 12, 6, 15, tzinfo=timezone.utc),
        ),
        (
            datetime(2024, 1, 12, 21, 50, tzinfo=timezone.utc),
            datetime(2024, 1, 13, 5, 50, tzinfo=timezone.utc),
        ),
        (
            datetime(2024, 1, 13, 22, 10, tzinfo=timezone.utc),
            datetime(2024, 1, 14, 6, 10, tzinfo=timezone.utc),
        ),
        (
            datetime(2024, 1, 14, 22, 0, tzinfo=timezone.utc),
            datetime(2024, 1, 15, 6, 0, tzinfo=timezone.utc),
        ),
        (
            datetime(2024, 1, 15, 21, 55, tzinfo=timezone.utc),
            datetime(2024, 1, 16, 5, 55, tzinfo=timezone.utc),
        ),
        (
            datetime(2024, 1, 16, 22, 5, tzinfo=timezone.utc),
            datetime(2024, 1, 17, 6, 5, tzinfo=timezone.utc),
        ),
    ]

    result_sleep = analyzer.determine_chronotype_from_sleep_data(
        sleep_data, user_tz
    )

    user_uuid = uuid4()
    profile = analyzer.create_chronotype_profile(
        user_id=user_uuid,
        chronotype=chronotype_meq,
        source="meq_initial",
        chronotype_strength=0.65,
        consistency_score=0.8,
    )

    from datetime import date

    focus_blocks = analyzer.get_optimal_focus_blocks(
        profile=profile,
        target_date=date(2024, 1, 20),
        block_duration=timedelta(minutes=90),
        min_blocks=2,
        max_blocks=4,
    )

    logger.info("✅ Old module executed successfully")
    logger.info(f"  MEQ {meq_score} → {chronotype_meq.value}")
    if result_sleep:
        logger.info(
            f"  Sleep data → {result_sleep[0].value}, "
            f"confidence={result_sleep[1]:.3f}"
        )
    logger.info(f"  Profile: {profile.primary_chronotype.value}")
    logger.info(f"  Focus blocks generated: {len(focus_blocks)}")

    return {
        "chronotype_meq": chronotype_meq,
        "result_sleep": result_sleep,
        "profile": profile,
        "focus_blocks": focus_blocks,
    }


def test_new_module():
    """
    Test new chronotype/ package.

    Educational Note:
        Imports from refactored package to verify identical behavior
        after modularization.
    """
    from src.core.chronotype import (
        Chronotype,
        ChronotypeAnalyzer,
        ChronotypeProfile,
    )

    analyzer = ChronotypeAnalyzer()

    meq_score = 65
    chronotype_meq = analyzer.determine_chronotype_from_meq(meq_score)

    user_tz = timezone(timedelta(hours=2))
    sleep_data = [
        (
            datetime(2024, 1, 10, 22, 0, tzinfo=timezone.utc),
            datetime(2024, 1, 11, 6, 0, tzinfo=timezone.utc),
        ),
        (
            datetime(2024, 1, 11, 22, 15, tzinfo=timezone.utc),
            datetime(2024, 1, 12, 6, 15, tzinfo=timezone.utc),
        ),
        (
            datetime(2024, 1, 12, 21, 50, tzinfo=timezone.utc),
            datetime(2024, 1, 13, 5, 50, tzinfo=timezone.utc),
        ),
        (
            datetime(2024, 1, 13, 22, 10, tzinfo=timezone.utc),
            datetime(2024, 1, 14, 6, 10, tzinfo=timezone.utc),
        ),
        (
            datetime(2024, 1, 14, 22, 0, tzinfo=timezone.utc),
            datetime(2024, 1, 15, 6, 0, tzinfo=timezone.utc),
        ),
        (
            datetime(2024, 1, 15, 21, 55, tzinfo=timezone.utc),
            datetime(2024, 1, 16, 5, 55, tzinfo=timezone.utc),
        ),
        (
            datetime(2024, 1, 16, 22, 5, tzinfo=timezone.utc),
            datetime(2024, 1, 17, 6, 5, tzinfo=timezone.utc),
        ),
    ]

    result_sleep = analyzer.determine_chronotype_from_sleep_data(
        sleep_data, user_tz
    )

    user_uuid = uuid4()
    profile = analyzer.create_chronotype_profile(
        user_id=user_uuid,
        chronotype=chronotype_meq,
        source="meq_initial",
        chronotype_strength=0.65,
        consistency_score=0.8,
    )

    from datetime import date

    focus_blocks = analyzer.get_optimal_focus_blocks(
        profile=profile,
        target_date=date(2024, 1, 20),
        block_duration=timedelta(minutes=90),
        min_blocks=2,
        max_blocks=4,
    )

    logger.info("✅ New module executed successfully")
    logger.info(f"  MEQ {meq_score} → {chronotype_meq.value}")
    if result_sleep:
        logger.info(
            f"  Sleep data → {result_sleep[0].value}, "
            f"confidence={result_sleep[1]:.3f}"
        )
    logger.info(f"  Profile: {profile.primary_chronotype.value}")
    logger.info(f"  Focus blocks generated: {len(focus_blocks)}")

    return {
        "chronotype_meq": chronotype_meq,
        "result_sleep": result_sleep,
        "profile": profile,
        "focus_blocks": focus_blocks,
    }


def compare_results(old_results, new_results):
    """
    Compare results from old and new modules.

    Educational Note:
        Compares functional behavior rather than object identity,
        focusing on computed classifications and recommendations.
    """
    logger.info("\n" + "=" * 60)
    logger.info("COMPARISON")
    logger.info("=" * 60)

    if old_results["chronotype_meq"].value != new_results["chronotype_meq"].value:
        logger.error(
            f"❌ MEQ chronotype mismatch: "
            f"old={old_results['chronotype_meq'].value}, "
            f"new={new_results['chronotype_meq'].value}"
        )
        return False
    logger.info("✅ MEQ chronotype determination matches")

    old_sleep = old_results["result_sleep"]
    new_sleep = new_results["result_sleep"]

    if old_sleep is None and new_sleep is None:
        logger.info("✅ Sleep data chronotype both None")
    elif old_sleep is not None and new_sleep is not None:
        old_chrono, old_conf = old_sleep
        new_chrono, new_conf = new_sleep
        if old_chrono.value == new_chrono.value and abs(old_conf - new_conf) < 0.001:
            logger.info(
                f"✅ Sleep data chronotype matches: {old_chrono.value}, "
                f"confidence={old_conf:.3f}"
            )
        else:
            logger.error(
                f"❌ Sleep data mismatch: "
                f"old=({old_chrono.value}, {old_conf:.3f}), "
                f"new=({new_chrono.value}, {new_conf:.3f})"
            )
            return False
    else:
        logger.error("❌ Sleep data result existence mismatch")
        return False

    old_profile = old_results["profile"]
    new_profile = new_results["profile"]

    if old_profile.primary_chronotype.value != new_profile.primary_chronotype.value:
        logger.error(
            f"❌ Profile chronotype mismatch: "
            f"old={old_profile.primary_chronotype.value}, "
            f"new={new_profile.primary_chronotype.value}"
        )
        return False
    logger.info("✅ Profile chronotype matches")

    if abs(old_profile.chronotype_strength - new_profile.chronotype_strength) >= 0.001:
        logger.error("❌ Profile strength mismatch")
        return False
    logger.info("✅ Profile strength matches")

    old_blocks = old_results["focus_blocks"]
    new_blocks = new_results["focus_blocks"]

    if len(old_blocks) != len(new_blocks):
        logger.error(
            f"❌ Focus blocks count mismatch: "
            f"old={len(old_blocks)}, new={len(new_blocks)}"
        )
        return False
    logger.info(f"✅ Focus blocks count matches: {len(old_blocks)}")

    for i, (old_block, new_block) in enumerate(zip(old_blocks, new_blocks)):
        if old_block == new_block:
            continue
        else:
            logger.error(
                f"❌ Focus block {i} mismatch: "
                f"old={old_block}, new={new_block}"
            )
            return False

    logger.info("✅ All focus blocks match")

    return True


def test_edge_cases():
    """
    Test edge cases with both modules.

    Educational Note:
        Edge case testing ensures refactoring preserved correct
        behavior for boundary conditions and error handling.
    """
    logger.info("\n" + "=" * 60)
    logger.info("Testing edge cases")
    logger.info("=" * 60)

    from src.core.chronotype import ChronotypeAnalyzer

    analyzer = ChronotypeAnalyzer()

    try:
        analyzer.determine_chronotype_from_meq(150)
        logger.error("❌ Should raise ValueError for invalid MEQ score")
        return False
    except ValueError:
        logger.info("✅ Invalid MEQ score raises ValueError")

    result = analyzer.determine_chronotype_from_sleep_data([], timezone.utc)
    if result is None:
        logger.info("✅ Empty sleep data returns None")
    else:
        logger.error("❌ Empty sleep data should return None")
        return False

    return True


def run_all_tests():
    """
    Execute all comparison tests.

    Educational Note:
        Orchestrates test execution and provides clear pass/fail
        reporting for the entire refactoring validation.
    """
    logger.info("\n" + "=" * 70)
    logger.info("PHASE 4 INTEGRATION TEST: Chronotype Modules Comparison")
    logger.info("=" * 70)

    logger.info("\n" + "=" * 60)
    logger.info("Testing OLD chronotype_legacy.py module")
    logger.info("=" * 60)
    try:
        old_results = test_old_module()
    except Exception as e:
        logger.error(f"❌ Old module failed: {e}")
        return False

    logger.info("\n" + "=" * 60)
    logger.info("Testing NEW chronotype package modules")
    logger.info("=" * 60)
    try:
        new_results = test_new_module()
    except Exception as e:
        logger.error(f"❌ New module failed: {e}")
        return False

    if not compare_results(old_results, new_results):
        logger.error(
            "\n❌ TESTS FAILED - Modules produce different results!"
        )
        return False

    if not test_edge_cases():
        logger.error("\n❌ EDGE CASE TESTS FAILED!")
        return False

    logger.info("\n" + "=" * 70)
    logger.info(
        "✅ ALL TESTS PASSED - Refactored chronotype modules work identically!"
    )
    logger.info("=" * 70)
    return True


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
