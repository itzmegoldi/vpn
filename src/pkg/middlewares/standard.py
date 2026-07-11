import time
from typing import Awaitable, Callable

from fastapi import HTTPException, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from src.builder import get_clients, get_config
from src.pkg import logging

logger = logging.get_logger()


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ):
        try:
            response: Response = await call_next(request)
        except HTTPException as he:
            raise he
        except ValueError as ve:
            raise HTTPException(status_code=400, detail=str(ve))
        except Exception as e:
            raise HTTPException(status_code=500, detail="Internal Server Error")
        return response


class LoggerInitMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ):
        request_id = request.headers.get("X-Request-ID", None)
        logging.init_logger_context(request_id=request_id)
        logging.bind_context(app_source="api")
        request_url = str(request.url)
        logger.info(
            "Request Initiated",
            context={"request_url": request_url},
        )
        start_time = int(time.time() * 1000)

        try:
            response: Response = await call_next(request)
        except HTTPException as he:
            logger.error(
                "Request Failed",
                context={
                    "request_url": request_url,
                    "status_code": he.status_code,
                    "detail": he.detail,
                },
            )
            raise he

        processed_time = int(time.time() * 1000) - start_time
        logger.info(
            "Request Completed",
            context={
                "start_time": start_time,
                "processed_time_ms": processed_time,
            },
        )
        logging.clear_context()
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    excluded_suffixes = ("/connect", "/disconnect")

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ):
        if request.url.path.endswith(self.excluded_suffixes):
            return await call_next(request)

        config = get_config()
        redis_client = get_clients().redis_client
        client_ip = self._client_ip(request)
        key = f"rate_limit:{client_ip}:{request.url.path}"

        try:
            count = await redis_client.increment_with_expiry(
                key=key, expiry_seconds=config.rate_limit_window_seconds
            )
            logger.info("Rate limit check", context={"count": count})
        except Exception as exc:
            logger.error("Rate limit check failed", context={"error": str(exc)})
            return await call_next(request)

        if count > config.rate_limit_requests:
            raise HTTPException(status_code=429, detail="Too many requests")

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(config.rate_limit_requests)
        response.headers["X-RateLimit-Remaining"] = str(
            max(config.rate_limit_requests - count, 0)
        )
        return response

    def _client_ip(self, request: Request) -> str:
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        if request.client is None:
            return "unknown"
        return request.client.host
