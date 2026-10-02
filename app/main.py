from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.database import models  # noqa: F401
from app.database.database import create_schema
from app.routers import auth, routes, users


@asynccontextmanager
async def lifespan(_: FastAPI):
    create_schema()
    yield


settings = get_settings()
app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_origin_regex=(
        None if settings.is_production else settings.cors_origin_regex or None
    ),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth.router, prefix=settings.api_v1_prefix)
app.include_router(users.router, prefix=settings.api_v1_prefix)
app.include_router(routes.router, prefix=settings.api_v1_prefix)


@app.get("/health", tags=["Health"])
def health() -> dict[str, str]:
    return {"status": "ok"}