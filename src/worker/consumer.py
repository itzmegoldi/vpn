import inspect
from typing import Any

from pydantic import BaseModel, ValidationError

from src.builder import get_service
from src.pkg import logging
from src.worker.dtos import DTO_REQUEST_MAPPER

logger = logging.get_logger()


async def process_message(message: dict[str, Any]):
    payload = _extract_payload(message)
    class_name = payload.pop("class_name", None)
    method_name = payload.pop("method_name", None)

    if not class_name or not method_name:
        raise ValueError("Worker message must include class_name and method_name")

    dto_class = DTO_REQUEST_MAPPER.get(method_name)

    try:
        if dto_class is not None:
            dto = dto_class.model_validate(payload)
        else:
            logger.info(
                "No DTO class found for method, passing raw payload",
                context={"method_name": method_name},
            )
            dto = payload
    except ValidationError:
        logger.error(
            "Worker message payload validation failed",
            context={"class_name": class_name, "method_name": method_name},
        )
        raise

    service = _resolve_service(class_name)
    method = getattr(service, method_name, None)
    if method is None or not callable(method):
        raise ValueError(f"Method {method_name} not found on {class_name}")

    result = method(*_method_args(method, dto))
    if inspect.isawaitable(result):
        return await result
    return result


def _extract_payload(message: dict[str, Any]) -> dict[str, Any]:
    if isinstance(message.get("payload"), dict):
        payload = message["payload"].copy()
        if "class_name" in message:
            payload.setdefault("class_name", message["class_name"])
        if "method_name" in message:
            payload.setdefault("method_name", message["method_name"])
        return payload
    return message.copy()


def _resolve_service(class_name: str):
    services = get_service()
    for service in vars(services).values():
        if service.__class__.__name__ == class_name:
            return service
    snake_name = _camel_to_snake(class_name)
    attr_name = (
        snake_name if snake_name.endswith("_service") else f"{snake_name}_service"
    )
    service = getattr(services, attr_name, None)
    if service is None:
        raise ValueError(f"Service class {class_name} not found")
    return service


def _method_args(method, dto: BaseModel) -> tuple[Any, ...]:
    params = list(inspect.signature(method).parameters.values())
    if not params:
        return ()

    data = dto.model_dump()
    first_param = params[0]
    if len(data) == 1 and first_param.name in data:
        return (data[first_param.name],)
    return (dto,)


def _camel_to_snake(value: str) -> str:
    chars = []
    for index, char in enumerate(value):
        if char.isupper() and index > 0:
            chars.append("_")
        chars.append(char.lower())
    return "".join(chars)
