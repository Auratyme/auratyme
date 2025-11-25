"""
Main router for schedule generation API endpoints.

This module defines the FastAPI router and endpoint configurations
for schedule generation services. Demonstrates clean router setup,
endpoint documentation, and response model configuration essential
for maintainable API architecture and client integration.
"""

from fastapi import APIRouter, Depends, Request, status, Body
from typing import Optional

from api.dependencies import get_scheduler
from src.core.scheduler import Scheduler

from .models import ScheduleGenerationRequest, ScheduleSuccessResponse
from .handlers import handle_schedule_generation_request
from .sse_stream import router as sse_router

router = APIRouter()


@router.post(
    "/generate-simple",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Generate a Simplified Schedule (Async)",
    description="Initiates asynchronous schedule generation and returns job_id immediately. "
                "Use /status/{job_id} endpoint to stream real-time progress updates via SSE. "
                "Returns job identifier for status monitoring.",
    tags=["V1 - Schedule"]
)
async def generate_simple_schedule(
    request: Request,
    request_data: Optional[ScheduleGenerationRequest] = Body(None),
    scheduler: Scheduler = Depends(get_scheduler)
):
    """
    Endpoint for initiating async schedule generation.
    
    This endpoint creates a background job for schedule generation
    and returns job_id immediately. Client can monitor progress by
    opening SSE stream to /status/{job_id}. Demonstrates non-blocking
    request handling pattern for long-running operations.
    
    Educational Note:
        Returns 202 ACCEPTED status indicating request was accepted
        for processing but not yet complete. Job_id enables client
        to track progress and retrieve results when ready.
    """
    return await handle_schedule_generation_request(request, request_data, scheduler)


router.include_router(sse_router)
