"""
Server-Sent Events stream endpoint for job status monitoring.

This module provides real-time status updates for schedule generation
jobs using SSE protocol. Enables non-blocking user experience by
streaming job progress updates as they occur.

Educational Note:
    SSE (Server-Sent Events) provides one-way server-to-client streaming
    over HTTP. Unlike WebSockets, SSE is simpler and works over standard
    HTTP, making it ideal for status updates and progress monitoring.
"""

import asyncio
import json
import logging
from typing import AsyncGenerator, Dict, Any
from uuid import uuid4

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

logger = logging.getLogger(__name__)

JOBS_STORE: Dict[str, Dict[str, Any]] = {}


async def generate_status_events(job_id: str) -> AsyncGenerator[str, None]:
    """
    Generates SSE events for job status updates.
    
    This async generator yields formatted SSE events containing job
    status information. Demonstrates streaming response pattern for
    real-time client updates without polling overhead.
    
    Educational Note:
        SSE format requires 'data: ' prefix and double newline separator.
        Generator pattern enables efficient memory usage for long-running
        streams by yielding data incrementally.
    """
    logger.info(f"📡 SSE stream opened for job {job_id}")
    
    iteration = 0
    max_iterations = 300
    
    while iteration < max_iterations:
        iteration += 1
        
        if job_id not in JOBS_STORE:
            error_event = format_sse_event({"error": "Job not found", "job_id": job_id})
            logger.error(f"❌ Job {job_id} not found in store")
            yield error_event
            break
        
        job_data = JOBS_STORE[job_id]
        current_status = job_data.get("status", "unknown")
        
        logger.info(f"📤 SSE event #{iteration} for job {job_id}: status={current_status}")
        
        yield format_sse_event(job_data)
        
        if should_close_stream(current_status):
            logger.info(f"✅ SSE stream closed for job {job_id} (final status: {current_status})")
            break
        
        await asyncio.sleep(1)
    
    if iteration >= max_iterations:
        logger.warning(f"⚠️ SSE stream timeout for job {job_id} after {max_iterations}s")


def format_sse_event(data: Dict[str, Any]) -> str:
    """
    Formats data as Server-Sent Event message.
    
    SSE protocol requires specific format: 'data: ' prefix followed
    by JSON payload and double newline. Demonstrates protocol-specific
    formatting for standards compliance.
    """
    json_data = json.dumps(data)
    return f"data: {json_data}\n\n"


def should_close_stream(status: str) -> bool:
    """
    Determines if SSE stream should close based on job status.
    
    Stream closes when job reaches terminal state (complete or failed).
    Demonstrates state-based control flow for connection management.
    """
    return status in ["complete", "failed", "error"]


router = APIRouter()


@router.get(
    "/status/{job_id}",
    summary="Stream Job Status Updates (SSE)",
    description="Opens Server-Sent Events stream providing real-time status updates "
                "for schedule generation job. Stream closes when job completes or fails.",
    tags=["V1 - Schedule"]
)
async def stream_job_status(job_id: str) -> StreamingResponse:
    """
    SSE endpoint for real-time job status streaming.
    
    This endpoint establishes Server-Sent Events connection streaming
    job status updates to client. Demonstrates async streaming response
    pattern for real-time notifications without websocket complexity.
    
    Educational Note:
        StreamingResponse with text/event-stream media type enables
        SSE protocol. Browser EventSource API can consume this stream
        natively without additional libraries.
    """
    logger.info(f"🌊 Opening SSE stream for job_id: {job_id}")
    
    return StreamingResponse(
        generate_status_events(job_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
