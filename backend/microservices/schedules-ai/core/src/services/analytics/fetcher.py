"""
Historical data fetching with mock generation.

Educational Note:
    Mock data generation allows development and testing without
    requiring full database infrastructure, accelerating iteration.
"""

import logging
import random
from datetime import date, timedelta
from typing import Any, Dict, List, Optional
from uuid import UUID

logger = logging.getLogger(__name__)

GeneratedSchedule = None
UserFeedback = None

try:
    from src.core.scheduler import GeneratedSchedule
    GENERATED_SCHEDULE_AVAILABLE = True
except ImportError:
    logger.warning("GeneratedSchedule not available. Using dummy.")
    from dataclasses import dataclass, field
    
    @dataclass
    class DummyGeneratedSchedule:
        user_id: UUID
        target_date: date
        metrics: Dict[str, Any] = field(default_factory=dict)
    
    GeneratedSchedule = DummyGeneratedSchedule
    GENERATED_SCHEDULE_AVAILABLE = False

try:
    from feedback.collectors.user_input import UserFeedback
    USER_FEEDBACK_AVAILABLE = True
except ImportError:
    logger.warning("UserFeedback not available. Using dummy.")
    from dataclasses import dataclass
    
    @dataclass
    class DummyUserFeedback:
        user_id: UUID
        schedule_date: date
        rating: Optional[int] = None
    
    UserFeedback = DummyUserFeedback
    USER_FEEDBACK_AVAILABLE = False


def generate_mock_schedules(
    user_id: UUID,
    start_date: date,
    end_date: date,
    base_task_minutes: int = 280,
) -> List[Any]:
    """
    Generates mock schedule data with simulated trends.
    
    Args:
        user_id: User identifier
        start_date: Period start
        end_date: Period end
        base_task_minutes: Starting task minutes per day
    
    Returns:
        List of mock GeneratedSchedule objects
    
    Educational Note:
        Simulated trends (day_index × random.uniform) create
        realistic variance for testing trend detection algorithms.
    """
    if not GeneratedSchedule:
        return []
    
    schedules = []
    current = start_date
    
    while current <= end_date:
        day_index = (current - start_date).days
        minutes = base_task_minutes + day_index * random.uniform(-2, 3)
        
        schedules.append(GeneratedSchedule(
            user_id=user_id,
            target_date=current,
            metrics={
                "total_scheduled_task_minutes": int(max(120, minutes)),
                "scheduled_task_count": random.randint(3, 8),
                "unscheduled_task_count": random.randint(0, 2),
            }
        ))
        current += timedelta(days=1)
    
    return schedules


def generate_mock_feedback(
    user_id: UUID,
    start_date: date,
    end_date: date,
    base_rating: float = 3.5,
    base_sleep: float = 450,
) -> List[Any]:
    """
    Generates mock feedback data correlated with sleep.
    
    Args:
        user_id: User identifier
        start_date: Period start
        end_date: Period end
        base_rating: Starting average rating
        base_sleep: Sleep duration affecting rating
    
    Returns:
        List of mock UserFeedback objects
    
    Educational Note:
        Correlation formula (base_sleep - 440)/60 creates realistic
        relationship where better sleep improves ratings by ~0.2/hour.
    """
    if not UserFeedback:
        return []
    
    feedback_list = []
    current = start_date
    
    while current <= end_date:
        if random.random() < 0.7:
            rating_noise = random.randint(-1, 1)
            rating = base_rating + (base_sleep - 440) / 60 + rating_noise
            clamped = int(max(1, min(5, round(rating))))
            
            feedback_list.append(UserFeedback(
                user_id=user_id,
                schedule_date=current,
                rating=clamped,
            ))
        current += timedelta(days=1)
    
    return feedback_list


def generate_mock_sleep_data(
    start_date: date,
    end_date: date,
    base_sleep: float = 450,
) -> List[Any]:
    """
    Generates mock sleep data with progressive trends.
    
    Args:
        start_date: Period start
        end_date: Period end
        base_sleep: Starting sleep duration in minutes
    
    Returns:
        List of HistoricalSleepData objects
    
    Educational Note:
        Gaussian distribution (normalvariate) for mid-sleep creates
        realistic clustering around user's natural chronotype.
    """
    from .models import HistoricalSleepData
    
    sleep_data = []
    current = start_date
    
    while current <= end_date:
        day_index = (current - start_date).days
        minutes = base_sleep + day_index * random.uniform(-5, 10)
        
        sleep_data.append(HistoricalSleepData(
            target_date=current,
            actual_sleep_duration_minutes=max(360, minutes),
            sleep_quality_score=random.uniform(60, 95),
            mid_sleep_hour_local=random.normalvariate(4.0, 0.8),
        ))
        current += timedelta(days=1)
    
    return sleep_data


async def fetch_historical_data(
    user_id: UUID,
    start_date: date,
    end_date: date,
    db_client: Optional[Any] = None,
) -> Dict[str, List[Any]]:
    """
    Fetches or generates historical data for analysis period.
    
    Args:
        user_id: User to fetch data for
        start_date: Period start
        end_date: Period end
        db_client: Database connection (if None, uses mock)
    
    Returns:
        Dict with keys: schedules, feedback, sleep_data
    
    Educational Note:
        Async signature allows future database integration without
        changing caller code - mocks complete instantly but real
        DB queries benefit from async/await patterns.
    """
    logger.info(
        f"Fetching historical data for user {user_id} "
        f"from {start_date} to {end_date}."
    )
    
    if db_client is None:
        logger.warning("DB client not initialized. Returning mock data.")
        
        base_sleep = random.uniform(400, 500)
        base_rating = random.uniform(2.5, 4.5)
        base_tasks = random.randint(200, 350)
        
        return {
            "schedules": generate_mock_schedules(
                user_id, start_date, end_date, base_tasks
            ),
            "feedback": generate_mock_feedback(
                user_id, start_date, end_date, base_rating, base_sleep
            ),
            "sleep_data": generate_mock_sleep_data(
                start_date, end_date, base_sleep
            ),
        }
    
    try:
        logger.warning("Actual DB fetching not implemented. Returning empty.")
        return {"schedules": [], "feedback": [], "sleep_data": []}
    except Exception:
        logger.exception(f"Error fetching data for user {user_id}")
        return {"schedules": [], "feedback": [], "sleep_data": []}
