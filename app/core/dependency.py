from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.language import validate_language_code
from app.db.session import get_async_session
from app.repositories.company import CompanyRepository
from app.repositories.company_tag import CompanyTagRepository
from app.repositories.tag import TagRepository
from app.services.company import CompanyService
from app.services.tag import TagService


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

    if not validate_language_code(x_wanted_language):
        raise HTTPException(status_code=400, detail="Invalid language code")

    return x_wanted_language


Language = Annotated[str, Depends(get_language)]


# Repository 의존성들
def get_company_repository(db: DatabaseSession) -> CompanyRepository:
    """CompanyRepository 의존성 팩토리"""
    return CompanyRepository(db)


def get_tag_repository(db: DatabaseSession) -> TagRepository:
    """TagRepository 의존성 팩토리"""
    return TagRepository(db)


def get_company_tag_repository(db: DatabaseSession) -> CompanyTagRepository:
    """CompanyTagRepository 의존성 팩토리"""
    return CompanyTagRepository(db)


# Service 의존성들
def get_company_service(
    db: DatabaseSession,
    company_repo: Annotated[CompanyRepository, Depends(get_company_repository)],
    tag_repo: Annotated[TagRepository, Depends(get_tag_repository)],
    company_tag_repo: Annotated[
        CompanyTagRepository, Depends(get_company_tag_repository)
    ],
) -> CompanyService:
    """CompanyService 의존성 팩토리"""
    return CompanyService(db, company_repo, tag_repo, company_tag_repo)


def get_tag_service(
    db: DatabaseSession,
    tag_repo: Annotated[TagRepository, Depends(get_tag_repository)],
    company_repo: Annotated[CompanyRepository, Depends(get_company_repository)],
    company_tag_repo: Annotated[
        CompanyTagRepository, Depends(get_company_tag_repository)
    ],
) -> TagService:
    """TagService 의존성 팩토리"""
    return TagService(db, company_repo, tag_repo, company_tag_repo)


# 타입 힌트 별칭들
CompanyRepositoryDep = Annotated[CompanyRepository, Depends(get_company_repository)]
TagRepositoryDep = Annotated[TagRepository, Depends(get_tag_repository)]
CompanyTagRepositoryDep = Annotated[
    CompanyTagRepository, Depends(get_company_tag_repository)
]
CompanyServiceDep = Annotated[CompanyService, Depends(get_company_service)]
TagServiceDep = Annotated[TagService, Depends(get_tag_service)]
