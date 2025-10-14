from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.main import router
from app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
)


origins = [
    "http://localhost:8080",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(router)