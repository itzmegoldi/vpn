from collections.abc import AsyncGenerator, Generator
from typing import Protocol


class IDatabase(Protocol):
    def get_session(self) -> Generator: ...
    def get_async_session(self) -> AsyncGenerator: ...
