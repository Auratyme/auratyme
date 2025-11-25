"""
API Router for Schedule Generation and Retrieval (Version 1).

This module serves as the main entry point for schedule generation
endpoints. Imports and exposes the modular schedule API components
while maintaining backward compatibility. Demonstrates clean API
organization patterns and modular architecture principles.

Educational Note:
This refactored structure separates concerns into focused modules
while maintaining a single import point for the router. This pattern
enables better maintainability, testability, and code organization
while keeping the public interface clean and consistent.
"""

from fastapi import APIRouter

from .schedule_api import router as schedule_router

router = APIRouter()
router.include_router(schedule_router, tags=["V1 - Schedule"])