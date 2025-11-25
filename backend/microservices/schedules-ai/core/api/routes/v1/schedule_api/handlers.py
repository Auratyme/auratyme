"""
Request handlers for schedule generation API endpoints.

This module contains the core request handling logic for schedule
generation endpoints. Demonstrates clean request processing patterns,
error handling strategies, and service integration while maintaining
educational clarity in business logic implementation.
"""

import asyncio
import logging
from typing import Optional, Dict, Any
from uuid import uuid4
from datetime import datetime, timezone, date

from fastapi import Request, HTTPException, status, Depends

from api.dependencies import get_scheduler
from src.core.scheduler import Scheduler

from .models import ScheduleGenerationRequest, ScheduleSuccessResponse
from .data_preparation import prepare_schedule_input_data
from .example_data import create_example_schedule_input
from .response_formatting import (
    create_success_response_with_tasks,
    get_demonstration_schedule_tasks,
)
from .request_evaluation import is_demonstration_request
from .conversion_helpers import convert_schedule_to_response_tasks
from .sse_stream import JOBS_STORE

logger = logging.getLogger(__name__)


async def handle_schedule_generation_request(
    request: Request,
    request_data: Optional[ScheduleGenerationRequest],
    scheduler: Scheduler = Depends(get_scheduler)
) -> Dict[str, Any]:
    """
    Processes schedule generation requests asynchronously with SSE support.
    
    This handler creates a background job for schedule generation and
    returns immediately with job_id. Client can then stream progress
    via SSE endpoint. Demonstrates non-blocking request handling for
    long-running operations.
    
    Educational Note:
        Returns job_id immediately instead of blocking. Background task
        runs independently using asyncio.create_task(), enabling server
        to handle multiple concurrent requests efficiently.
    """
    logger.info(f"📨 Received schedule generation request for path: {request.url.path}")
    
    if is_demonstration_request(request_data):
        logger.info("🎭 Demonstration mode - returning mock job")
        return _create_demo_job()
    
    return await _create_async_job(request_data, scheduler)


def _handle_demonstration_request() -> ScheduleSuccessResponse:
    """
    Processes demonstration requests with example data.
    
    This handler provides consistent demonstration responses
    for testing and API exploration. Shows how to handle
    special cases in API endpoints while maintaining
    response structure consistency for client compatibility.
    """
    logger.info("Using demonstration data for schedule generation")
    
    demonstration_tasks = get_demonstration_schedule_tasks()
    return create_success_response_with_tasks(demonstration_tasks)


def _create_demo_job() -> Dict[str, Any]:
    """
    Creates demo job for demonstration mode.
    
    Returns mock job_id for testing SSE without real generation.
    Demonstrates test mode implementation for development.
    """
    job_id = str(uuid4())
    JOBS_STORE[job_id] = {
        "job_id": job_id,
        "status": "complete",
        "result": get_demonstration_schedule_tasks(),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    logger.info(f"🎭 Created demo job: {job_id}")
    return {"job_id": job_id, "status": "queued"}


async def _create_async_job(
    request_data: ScheduleGenerationRequest,
    scheduler: Scheduler
) -> Dict[str, Any]:
    """
    Creates async background job for schedule generation.
    
    Initiates background task and returns job_id immediately.
    Demonstrates async job creation pattern for non-blocking
    request handling in high-traffic scenarios.
    
    Educational Note:
        If user_id or target_date are not provided, they are
        auto-generated here. This simplifies client integration
        by allowing minimal request payloads.
    """
    job_id = str(uuid4())
    
    _apply_auto_defaults(request_data)
    
    logger.info(f"🆕 Creating job {job_id} for user {request_data.user_id}")
    
    JOBS_STORE[job_id] = initialize_job_data(job_id, request_data)
    
    asyncio.create_task(_process_schedule_generation(job_id, request_data, scheduler))
    
    logger.info(f"✅ Job {job_id} queued, background task started")
    
    return {"job_id": job_id, "status": "queued"}


def _apply_auto_defaults(request_data: ScheduleGenerationRequest) -> None:
    """
    Applies automatic defaults to optional fields if not provided.
    
    Ensures user_id and target_date always have values by
    generating them from system when client omits them.
    Demonstrates defensive programming for API robustness.
    """
    if request_data.user_id is None:
        request_data.user_id = uuid4()
        logger.info(f"🆔 Auto-generated user_id: {request_data.user_id}")
    
    if request_data.target_date is None:
        request_data.target_date = date.today()
        logger.info(f"📅 Auto-generated target_date: {request_data.target_date}")


def initialize_job_data(job_id: str, request_data: ScheduleGenerationRequest) -> Dict[str, Any]:
    """
    Initializes job data structure in memory store.
    
    Creates initial job record with queued status. Demonstrates
    data structure initialization for job tracking.
    """
    return {
        "job_id": job_id,
        "status": "queued",
        "user_id": str(request_data.user_id),
        "target_date": str(request_data.target_date),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "progress": 0
    }


async def _process_schedule_generation(
    job_id: str,
    request_data: ScheduleGenerationRequest,
    scheduler: Scheduler
) -> None:
    """
    Background task processing schedule generation.
    
    This async function runs independently from request handling,
    updating job status as generation progresses. Demonstrates
    background task pattern for long-running operations.
    
    Educational Note:
        Exception handling prevents background task failures from
        crashing the application. All errors are logged and stored
        in job data for client notification via SSE.
    """
    try:
        logger.info(f"🔄 Job {job_id} - Starting processing")
        update_job_status(job_id, "processing", progress=10)
        
        logger.info(f"📊 Job {job_id} - Preparing input data")
        input_data = prepare_schedule_input_data(request_data)
        update_job_status(job_id, "processing", progress=30)
        
        logger.info(f"🤖 Job {job_id} - Generating schedule (this may take 60+ seconds)")
        update_job_status(job_id, "generating", progress=50)
        
        generated_schedule = await scheduler.generate_schedule(input_data)
        
        logger.info(f"✨ Job {job_id} - Formatting response")
        update_job_status(job_id, "formatting", progress=90)
        
        real_tasks = convert_schedule_to_response_tasks(generated_schedule)
        result = create_success_response_with_tasks(real_tasks)
        
        logger.info(f"✅ Job {job_id} - COMPLETE!")
        complete_job_successfully(job_id, result)
        
    except Exception as e:
        logger.exception(f"❌ Job {job_id} - FAILED: {e}")
        fail_job_with_error(job_id, e)


def update_job_status(job_id: str, status: str, progress: int = None) -> None:
    """
    Updates job status in memory store.
    
    Modifies job record with new status and optional progress.
    Demonstrates state management for job tracking.
    """
    if job_id in JOBS_STORE:
        JOBS_STORE[job_id]["status"] = status
        JOBS_STORE[job_id]["updated_at"] = datetime.now(timezone.utc).isoformat()
        if progress is not None:
            JOBS_STORE[job_id]["progress"] = progress
        logger.info(f"📍 Job {job_id} status updated: {status} ({progress}%)")


def complete_job_successfully(job_id: str, result: Any) -> None:
    """
    Marks job as complete with result data.
    
    Updates job record with completion status and result payload.
    Demonstrates successful completion handling pattern.
    """
    if job_id in JOBS_STORE:
        JOBS_STORE[job_id].update({
            "status": "complete",
            "progress": 100,
            "result": result.model_dump() if hasattr(result, 'model_dump') else result,
            "completed_at": datetime.now(timezone.utc).isoformat()
        })


def fail_job_with_error(job_id: str, error: Exception) -> None:
    """
    Marks job as failed with error information.
    
    Updates job record with failure status and error details.
    Demonstrates error handling and failure tracking pattern.
    """
    if job_id in JOBS_STORE:
        JOBS_STORE[job_id].update({
            "status": "failed",
            "error": str(error),
            "error_type": type(error).__name__,
            "failed_at": datetime.now(timezone.utc).isoformat()
        })
