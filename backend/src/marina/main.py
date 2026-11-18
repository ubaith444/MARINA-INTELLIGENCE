"""MARINA INTELLIGENCE - FastAPI Main Application Entrypoint."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from marina.api.v1.router import api_v1_router
from marina.core.config import settings
from marina.core.exceptions import MarinaException


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Lifespan event handler for application startup and graceful shutdown."""
    # Startup: logging and readiness check can be placed here
    yield
    # Shutdown: clean up any long-lived resources
    pass


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=(
        "Professional football performance analytics platform initially focused on "
        "Chennaiyin FC and the Indian Super League (ISL) 2026–27 season.\n\n"
        "Strictly enforces football data integrity: never fabricates unplayed match results "
        "or player statistics, preserves null for unmeasured metrics, and tracks source provenance."
    ),
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Domain Exception Handler
@app.exception_handler(MarinaException)
async def marina_exception_handler(request: Request, exc: MarinaException) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": exc.message, "details": exc.details},
    )


# Include Versioned API Routes
app.include_router(api_v1_router, prefix=settings.API_V1_STR)


@app.get("/", include_in_schema=False)
async def root_redirect():
    """Redirect or provide platform metadata at the root path."""
    return {
        "platform": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "operational",
        "docs_url": "/docs",
        "health_url": f"{settings.API_V1_STR}/health",
        "focus": {
            "club": settings.DEFAULT_CLUB_NAME,
            "season": settings.DEFAULT_SEASON_CODE,
            "competition": settings.DEFAULT_COMPETITION_CODE,
        },
    }
