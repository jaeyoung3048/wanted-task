from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import settings

# 비동기 엔진 생성
async_engine = create_async_engine(
    settings.database_url,
    echo=settings.DEBUG,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_timeout=settings.DB_POOL_TIMEOUT,
    pool_pre_ping=True,  # 연결 유효성 검사
    poolclass=NullPool if settings.DEBUG else None,  # 개발 환경에서는 풀링 비활성화
)

# 비동기 세션 팩토리 생성
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    비동기 데이터베이스 세션을 생성하고 반환합니다.
    FastAPI의 Depends와 함께 사용할 수 있는 의존성 함수입니다.

    Yields:
        AsyncSession: 비동기 데이터베이스 세션
    """
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
    데이터베이스 테이블을 초기화합니다.
    애플리케이션 시작 시 호출됩니다.
    """
    from app.db.base import Base

    async with async_engine.begin() as conn:
        # 모든 테이블 생성 (개발용)
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """
    데이터베이스 연결을 정리합니다.
    애플리케이션 종료 시 호출됩니다.
    """
    await async_engine.dispose()
