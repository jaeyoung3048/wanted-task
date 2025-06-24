from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.language import validate_language_code
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


DatabaseSession = Annotated[AsyncSession, Depends(get_db)]


async def get_language(
    x_wanted_language: str | None = Header(default="ko", alias="x-wanted-language"),
) -> str:
    """
    x-wanted-language 헤더에서 언어 설정을 가져오는 의존성입니다.
    기본값은 'ko' 입니다.

    Args:
        x_wanted_language: 요청 헤더의 x-wanted-language 값

    Returns:
        str: 언어 코드
    """
    if x_wanted_language is None:
        return settings.DEFAULT_LANGUAGE

    # TODO[exception]: 추후 커스텀 예외로 변경 필요
    if not validate_language_code(x_wanted_language):
        raise HTTPException(status_code=400, detail="Invalid language code")

    return x_wanted_language


Language = Annotated[str, Depends(get_language)]
