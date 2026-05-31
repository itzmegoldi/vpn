from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.api import router as api_router
from src.builder import get_clients
from src.builder.helper import fetch_and_build, fetch_config
from src.pkg import logging
from src.pkg.middlewares.standard import ErrorHandlingMiddleware, LoggerInitMiddleware
from src.pkg.middlewares.standard import RateLimitMiddleware

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
async def lifespan(app: FastAPI):
    # Initialize resources here (e.g., database connections, caches)
    fetch_and_build()
    yield
    # Clean up resources here (e.g., close database connections, clear caches)
    await get_clients().redis_client.close()


app = FastAPI(title="VPN API", lifespan=lifespan)

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
app.add_middleware(RateLimitMiddleware)
app.add_middleware(ErrorHandlingMiddleware)
app.include_router(api_router, prefix="/api", tags=["API"])


if __name__ == "__main__":
    config = fetch_config()
    uvicorn.run(
        "src.api.main:app",
        host=config.server_host,
        port=config.server_port,
        log_level=None,
        reload=True,
    )
