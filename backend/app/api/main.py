from fastapi import APIRouter

from app.api.routes import options

router = APIRouter()
router.include_router(options.router)
