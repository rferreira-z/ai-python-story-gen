"""API v1 router aggregator."""

from fastapi import APIRouter

from app.api.v1 import auth, health, stories, story_universes, users

router = APIRouter()

router.include_router(health.router)
router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(users.router, prefix="/users", tags=["users"])
router.include_router(
    story_universes.router, prefix="/story-universes", tags=["story-universes"]
)
router.include_router(stories.router, prefix="/stories", tags=["stories"])
