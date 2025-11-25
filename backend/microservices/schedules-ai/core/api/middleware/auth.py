"""
Authentication and Authorization Utilities for the Scheduler Core API.

This module provides dependency functions suitable for use with FastAPI's
`Depends` system to protect API endpoints. It verifies JWT tokens using
a public key from the oauth-tenant-public-key.pem file.
"""

import logging
import jwt
from fastapi import HTTPException, status, Header, Request
from jwt import PyJWTError

# --- Constants and Configuration ---
logger = logging.getLogger(__name__)

def read_public_key(filepath: str) -> str:
    """
    Read the public key from a file.

    Args:
        filepath: Path to the public key file.

    Returns:
        The public key as a string.
    """
    try:
        with open(filepath, "r") as f:
            return f.read().strip()
    except Exception as e:
        logger.error(f"Error reading public key file: {e}")
        raise

try:
    JWT_PUBLIC_KEY = read_public_key("oauth-tenant-public-key.pem")
    logger.info("Public key loaded from relative path")
except Exception as e:
    logger.warning(f"Could not load public key from relative path: {e}")
    try:
        JWT_PUBLIC_KEY = read_public_key("/app/oauth-tenant-public-key.pem")
        logger.info("Public key loaded from absolute path")
    except Exception as e:
        logger.error(f"Failed to load public key: {e}")
        JWT_PUBLIC_KEY = ""

def verify_token(request: Request, authorization: str = Header(None, title='authorization')):
    """
    Verify the JWT token in the Authorization header.

    Args:
        request: The FastAPI request object.
        authorization: The Authorization header value.

    Returns:
        The decoded JWT payload if valid.

    Raises:
        HTTPException: If the token is missing, invalid, or expired.
    """
    if not authorization:
        logger.warning("Authorization header missing")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header"
        )

    if not authorization.startswith("Bearer "):
        logger.warning("Invalid authorization header format")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format"
        )

    token = authorization.split(" ")[1]

    try:
        payload = jwt.decode(
            jwt=token,
            key=JWT_PUBLIC_KEY,
            algorithms=["RS256"],
            audience="https://api.auratyme.com"
        )
        request.state.userId = payload.get("sub")
        logger.debug(f"Token verified successfully for user: {request.state.userId}")
        return payload
    except PyJWTError as err:
        logger.warning(f"JWT verification failed: {err}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
