"""Health check endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check() -> dict:
    """Basic health check endpoint."""
    return {"status": "healthy"}


@router.get("/health/db")
async def db_health_check(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict:
    """Health check with database connectivity test."""
    await db.execute(text("SELECT 1"))
    return {"status": "healthy", "database": "connected"}
