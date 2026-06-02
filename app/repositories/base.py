from abc import ABC, abstractmethod
from typing import TypeVar, Generic

T = TypeVar("T")


class AbstractRepository(ABC, Generic[T]):
    """
    Abstract base repository following the Repository pattern.
    Enforces Dependency Inversion Principle — services depend on
    abstractions, not concrete implementations.
    """

    @abstractmethod
    async def get_by_id(self, id: int) -> T | None:
        raise NotImplementedError

    @abstractmethod
    async def get_all(self) -> list[T]:
        raise NotImplementedError

    @abstractmethod
    async def create(self, data: dict) -> T:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, id: int) -> bool:
        raise NotImplementedError
