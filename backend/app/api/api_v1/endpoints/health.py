"""Health check endpoints."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def health_check() -> dict[str, str]:
    """Basic health check endpoint."""
    return {"status": "healthy", "service": "santaserver"}