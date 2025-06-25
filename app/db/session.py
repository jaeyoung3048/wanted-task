from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from app.core.config import settings

# 전역 변수 선언 (초기화는 init_db에서)
async_engine: AsyncEngine | None = None
AsyncSessionLocal: async_sessionmaker[AsyncSession] | None = None


def _create_engine() -> AsyncEngine:
    """비동기 엔진을 생성합니다."""
    if settings.DEBUG:
        return create_async_engine(
            settings.database_url,
            echo=settings.DEBUG,
            poolclass=NullPool,
        )

    return create_async_engine(
        settings.database_url,
        echo=settings.DEBUG,
        pool_size=settings.DB_POOL_SIZE,
        max_overflow=settings.DB_MAX_OVERFLOW,
        pool_timeout=settings.DB_POOL_TIMEOUT,
        pool_pre_ping=True,  # 연결 유효성 검사
    )


def _create_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """비동기 세션 팩토리를 생성합니다."""
    return async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,  # 트랜잭션 커밋 후 객체 만료 방지
        autoflush=True,  # 자동 flush (쿼리 전 변경사항 반영)
        autocommit=False,  # 수동 트랜잭션 관리
    )


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    비동기 데이터베이스 세션을 생성하고 반환합니다.
    FastAPI의 Depends와 함께 사용할 수 있는 의존성 함수입니다.

    Yields:
        AsyncSession: 비동기 데이터베이스 세션

    Raises:
        RuntimeError: 데이터베이스가 초기화되지 않은 경우
    """
    if AsyncSessionLocal is None:
        raise RuntimeError("init_db()를 먼저 호출하세요.")

    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """
    데이터베이스 엔진과 세션을 초기화하고 테이블을 생성합니다.
    애플리케이션 시작 시 호출됩니다.
    """
    global async_engine, AsyncSessionLocal

    # 엔진 생성
    async_engine = _create_engine()

    # 세션 팩토리 생성
    AsyncSessionLocal = _create_session_factory(async_engine)


async def close_db() -> None:
    """
    데이터베이스 연결을 정리합니다.
    애플리케이션 종료 시 호출됩니다.
    """
    global async_engine, AsyncSessionLocal

    if async_engine is not None:
        await async_engine.dispose()
        async_engine = None
        AsyncSessionLocal = None
