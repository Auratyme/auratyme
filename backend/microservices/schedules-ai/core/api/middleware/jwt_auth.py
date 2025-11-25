"""
JWT Authentication Middleware for the API.

This module provides middleware for verifying JWT tokens in requests using
the public key from oauth-tenant-public-key.pem.
"""

import logging
from typing import List

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware

from api.middleware.auth import verify_token, JWT_PUBLIC_KEY

logger = logging.getLogger(__name__)

# --- Public Paths ---
PUBLIC_PATHS: List[str] = [
    "/health",
    "/docs",
    "/redoc",
    "/openapi.json",
    "/v1/schedule/generate",
    "/v1/schedule/status",
    # "/v1/schedule/generate-simple",  # Wymaga autoryzacji JWT z kluczem!
    "/ai-test/schedules/generate",
]


class JWTAuthMiddleware(BaseHTTPMiddleware):
    """Middleware for JWT authentication using RS256 algorithm and public key."""

    async def dispatch(self, request: Request, call_next):
        """
        Process the request and verify JWT token if needed.

        Args:
            request: The FastAPI request object.
            call_next: The next middleware or route handler.

        Returns:
            The response from the next middleware or route handler.

        Raises:
            HTTPException: If the token is missing, invalid, or expired.
        """
        path = request.url.path

        if any(path.startswith(public_path) for public_path in PUBLIC_PATHS):
            return await call_next(request)

        if not JWT_PUBLIC_KEY:
            logger.error("Public key not available for JWT verification")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Authentication configuration error",
            )

        auth_header = request.headers.get("Authorization")
        try:
            payload = verify_token(request, auth_header)
            request.state.user = payload
            request.state.userId = payload.get("sub")
        except HTTPException as e:
            raise e
        except Exception as e:
            logger.error(f"Unexpected error during JWT verification: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred during authentication",
            )

        return await call_next(request)
