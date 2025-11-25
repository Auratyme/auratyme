"""
Schedule API package for intelligent schedule generation.

This package provides a comprehensive schedule generation API with
clean separation of concerns across models, handlers, utilities,
and routing components. Demonstrates modular API architecture
patterns essential for maintainable and scalable web services.

Educational Focus:
- Pydantic model design for data validation
- Request handling patterns with proper error management  
- Service layer integration and dependency injection
- Response formatting and API consistency
- Utility function decomposition and reusability
- Clean router configuration and endpoint documentation

The package structure follows the principle of single responsibility
with each module focused on a specific aspect of the API functionality.
This approach enables easier testing, maintenance, and feature evolution
while serving as an educational example of professional API development.
"""

from .router import router
from .models import (
    ScheduleGenerationRequest,
    ScheduleSuccessResponse,
    TaskInput,
    FixedEventInput
)

__all__ = [
    "router",
    "ScheduleGenerationRequest", 
    "ScheduleSuccessResponse",
    "TaskInput",
    "FixedEventInput"
]
