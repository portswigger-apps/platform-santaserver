"""Health check endpoints."""

from fastapi import APIRouter
from app import __version__

router = APIRouter()


@router.get("/")
@router.get("")  # Handle both with and without trailing slash
async def health_check() -> dict[str, str]:
    """Detailed health check endpoint with version information."""
    return {
        "status": "healthy",
        "service": "santaserver",
        "version": __version__,
    }
