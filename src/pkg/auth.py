from typing import Annotated, Optional

from fastapi import HTTPException, Request, Security
from fastapi.security import APIKeyHeader
from fastapi.security.http import HTTPAuthorizationCredentials, HTTPBearer

from src.builder import get_config

from src.pkg import logging

logger = logging.get_logger()

api_key_header = APIKeyHeader(name="x-api-key", auto_error=False)
http_bearer = HTTPBearer(auto_error=False)


async def verify_client(
    request: Request,
    hdr_key: Annotated[Optional[str], Security(api_key_header)] = None,
    bearer: Annotated[HTTPAuthorizationCredentials, Security(http_bearer)] = None,
):
    result = await validate_request_authentication(request, hdr_key, bearer)
    return result["client_name"]


def handle_regular_auth(hdr_key):
    if hdr_key is None:
        raise HTTPException(status_code=401, detail="Missing API key")

    for auth in get_config().server.auth:
        if auth.client_key == hdr_key:
            return {"client_name": auth.client_name}

    raise HTTPException(status_code=403, detail="Invalid API key")


async def validate_request_authentication(
    request: Request,
    hdr_key: Annotated[Optional[str], Security(api_key_header)] = None,
    bearer: Annotated[HTTPAuthorizationCredentials, Security(http_bearer)] = None,
):

    return handle_regular_auth(hdr_key)
