from contextlib import asynccontextmanager
from typing import Annotated

import uvicorn
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.api import router as api_router
from src.builder import get_clients
from src.builder.helper import fetch_and_build, fetch_config
from src.pkg import logging
from src.pkg.auth import verify_client
from src.pkg.middlewares.standard import ErrorHandlingMiddleware, LoggerInitMiddleware

logging.configure_logger(
    default_logger_names=[
        "root",
        "fastapi",
        "sqlalchemy.engine",
        "alembic.runtime.migration",
        "uvicorn.access",
        "uvicorn.error",
        "uvicorn",
    ],
)

logger = logging.get_logger()


class HealthCheckResponse(BaseModel):
    status: str


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Initialize resources here (e.g., database connections, caches)
    fetch_and_build()
    yield


app = FastAPI(
    title="VPN API",
    lifespan=lifespan,
    redoc_url=None,
    openapi_tags=[{"name": "API", "description": "API endpoints"}],
)

allowed_origins = ["*"]
# Adjust this in production for security


@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    return HealthCheckResponse(status="healthy")


app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(LoggerInitMiddleware)
app.add_middleware(ErrorHandlingMiddleware)
app.include_router(
    api_router, prefix="/api", tags=["API"], dependencies=[Depends(verify_client)]
)


if __name__ == "__main__":
    config = fetch_config()
    uvicorn.run(
        app=app, host=config.server.host, port=config.server.port, log_level=None
    )
