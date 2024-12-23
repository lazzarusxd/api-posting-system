from fastapi import APIRouter

from app.api.v1.endpoints import auth, posting

router = APIRouter()

router.include_router(auth.router, prefix="/auth", tags=["Auth"])
router.include_router(posting.router, prefix="/posting", tags=["Posting"])
