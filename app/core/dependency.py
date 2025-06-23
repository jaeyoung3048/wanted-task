from typing import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_async_session


# 비동기 데이터베이스 세션 의존성
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI의 의존성 주입을 위한 데이터베이스 세션 팩토리입니다.

    Yields:
        AsyncSession: 비동기 데이터베이스 세션
    """
    async for session in get_async_session():
        yield session


DatabaseSession = Depends(get_db)
