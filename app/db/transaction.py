from collections.abc import Awaitable, Callable
from functools import wraps
from typing import Any, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")


def transactional(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
    @wraps(func)
    async def wrapper(self, *args: Any, **kwargs: Any) -> T:
        db = getattr(self, "db", None)

        if not isinstance(db, AsyncSession):
            raise ValueError(
                f"@transactional decorator requires self.db to be AsyncSession, "
                f"got {type(db)}"
            )

        async with db.begin():
            return await func(self, *args, **kwargs)

    return wrapper
