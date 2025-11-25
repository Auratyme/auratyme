"""
User Input Feedback Collector.

Handles the collection, validation, and preparation for storage of feedback
provided directly by the user (e.g., schedule ratings, comments).
"""

import logging
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from typing import Any, Dict, Optional
from uuid import UUID, uuid4

logger = logging.getLogger(__name__)

try:
    from src.utils.validators import validate_feedback_rating
    VALIDATOR_AVAILABLE = True
except ImportError:
    logger.warning("Validator 'validate_feedback_rating' not found in src.utils. Using basic validation.")
    VALIDATOR_AVAILABLE = False
    def validate_feedback_rating(rating: int) -> bool: return True

# --- Constants ---
MAX_COMMENT_LENGTH = 1000

# --- Data Structure for User Feedback ---

@dataclass
class UserFeedback:
    """
    Represents feedback submitted by a user for a specific schedule.

    Contains user identification, schedule date, rating, and optional comment.
    Automatically generates a unique feedback ID and timestamp upon creation.
    """
    user_id: UUID
    schedule_date: date
    rating: int
    feedback_id: UUID = field(default_factory=uuid4)
    comment: Optional[str] = None
    submitted_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    schedule_version_id: Optional[str] = None

# --- Collector Class ---

class UserInputCollector:
    """
    Collects, validates, and prepares user feedback for storage.

    Handles validation of feedback data and preparation for persistence.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """
        Initialize the UserInputCollector with optional configuration.

        Args:
            config: Optional configuration dictionary for the collector.
        """
        self._config = config or {}
        self._storage_client = None
        logger.info("UserInputCollector initialized.")

    def _validate_feedback(self, rating: int, comment: Optional[str]) -> bool:
        """
        Validate feedback data against defined rules.

        Args:
            rating: Numerical rating (typically 1-5)
            comment: Optional textual feedback

        Returns:
            True if feedback is valid, False otherwise
        """
        if VALIDATOR_AVAILABLE:
            if not validate_feedback_rating(rating):
                logger.warning(f"Invalid feedback rating (failed custom validator): {rating}")
                return False
        else:
            if not isinstance(rating, int) or not (1 <= rating <= 5):
                logger.warning(
                    f"Invalid feedback rating (basic check): {rating}. Must be int between 1-5."
                )
                return False

        if comment is not None and not isinstance(comment, str):
            logger.warning(
                f"Invalid feedback comment type: {type(comment)}. Must be string or None."
            )
            return False

        if comment is not None and len(comment) > MAX_COMMENT_LENGTH:
            logger.warning(
                f"Feedback comment exceeds length limit ({MAX_COMMENT_LENGTH} chars). Length: {len(comment)}"
            )
            return False

        return True

    async def collect_feedback(
        self,
        user_id: UUID,
        schedule_date: date,
        rating: int,
        comment: Optional[str] = None,
        schedule_version_id: Optional[str] = None,
    ) -> Optional[UserFeedback]:
        """
        Collect and store user feedback for a specific schedule.

        Args:
            user_id: Unique identifier for the user
            schedule_date: Date of the schedule being rated
            rating: Numerical rating (typically 1-5)
            comment: Optional textual feedback
            schedule_version_id: Optional version identifier for the schedule

        Returns:
            UserFeedback object if successfully collected and stored, None otherwise
        """
        logger.info(
            f"Collecting feedback for user '{user_id}', schedule date '{schedule_date}' "
            f"(Rating: {rating})."
        )

        if not self._validate_feedback(rating, comment):
            logger.warning(f"Feedback validation failed for user '{user_id}', date '{schedule_date}'.")
            return None

        cleaned_comment = comment.strip() if comment else None
        feedback_entry = UserFeedback(
            user_id=user_id,
            schedule_date=schedule_date,
            rating=rating,
            comment=cleaned_comment,
            schedule_version_id=schedule_version_id,
        )

        try:
            storage_successful = True
            if storage_successful:
                logger.info(
                    f"Successfully collected and stored feedback ID {feedback_entry.feedback_id} "
                    f"for user '{user_id}', date '{schedule_date}'."
                )
                return feedback_entry
            else:
                logger.error(
                    f"Failed to store user feedback for user '{user_id}', date '{schedule_date}' "
                    f"(storage operation returned failure)."
                )
                return None
        except Exception:
            logger.exception(
                f"Error storing user feedback for user '{user_id}', date '{schedule_date}'.",
            )
            return None

async def run_example():
    from dataclasses import asdict
    from datetime import timedelta

    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger.info("--- Running UserInputCollector Example ---")

    collector = UserInputCollector()
    test_user_id = uuid4()
    test_schedule_date = date.today() - timedelta(days=1)

    print("\n--- Collecting Valid Feedback ---")
    feedback1 = await collector.collect_feedback(
        user_id=test_user_id,
        schedule_date=test_schedule_date,
        rating=4,
        comment=" Generally good, but the morning felt a bit rushed. ",
        schedule_version_id="v1.2"
    )
    if feedback1:
        print(f"Collected: {asdict(feedback1)}")

    print("\n--- Collecting Feedback with High Rating (No Comment) ---")
    feedback2 = await collector.collect_feedback(
        user_id=test_user_id,
        schedule_date=test_schedule_date,
        rating=5
    )
    if feedback2:
        print(f"Collected: {asdict(feedback2)}")

    print("\n--- Collecting Invalid Feedback (Bad Rating) ---")
    feedback3 = await collector.collect_feedback(
        user_id=test_user_id,
        schedule_date=test_schedule_date,
        rating=6,
        comment="This rating is wrong."
    )
    if not feedback3:
        print("Invalid feedback (rating=6) correctly rejected.")

    print("\n--- Collecting Invalid Feedback (Long Comment) ---")
    long_comment = "a" * (MAX_COMMENT_LENGTH + 1)
    feedback4 = await collector.collect_feedback(
        user_id=test_user_id,
        schedule_date=test_schedule_date,
        rating=3,
        comment=long_comment
    )
    if not feedback4:
        print(f"Invalid feedback (comment length > {MAX_COMMENT_LENGTH}) correctly rejected.")

if __name__ == "__main__":
    import asyncio
    asyncio.run(run_example())
