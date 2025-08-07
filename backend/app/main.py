"""FastAPI application entry point."""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.api_v1.api import api_router
from app.core.config import settings
from app import __version__

app = FastAPI(
    title="SantaServer",
    description="Enterprise Santa macOS security agent management server",
    version=__version__,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    redirect_slashes=False,
)

# Set CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)


# Add health check endpoint for container monitoring
@app.get("/health")
async def health_check():
    """Health check endpoint for container orchestration."""
    return {
        "status": "healthy",
        "service": "santaserver-backend",
        "version": __version__,
    }


# Support for Unix socket binding when running in unified container
if __name__ == "__main__":
    import uvicorn

    # Check if we should use Unix socket (unified container mode)
    socket_path = os.getenv("UVICORN_UDS")
    if socket_path:
        print(f"Starting uvicorn with Unix socket: {socket_path}")
        uvicorn.run(
            "app.main:app",
            uds=socket_path,
            log_level="info",
            access_log=True,
        )
    else:
        # Default HTTP binding for development/multi-container mode
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            log_level="info",
            reload=True,
        )
