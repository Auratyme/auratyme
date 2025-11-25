"""
Middleware package for the Scheduler Core API.

This package contains custom FastAPI middleware used for various purposes
such as authentication, logging, request/response processing, etc.
"""

from api.middleware.jwt_auth import JWTAuthMiddleware
from api.middleware.auth import verify_token

__all__ = ["JWTAuthMiddleware", "verify_token"]
