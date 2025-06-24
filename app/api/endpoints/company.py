from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependency import get_db, get_language
from app.schemas.company import CompanyResponse, CreateCompanyRequest, CreateTagRequest
from app.schemas.tag import TagResponse
from app.services.company import CompanyService
from app.services.tag import TagService

router = APIRouter()


@router.get("/{company_name}")
async def get_company(
    company_name: str,
    language: str = Depends(get_language),
    db: AsyncSession = Depends(get_db),
) -> CompanyResponse:
    return await CompanyService.get_company(db, company_name, language)


@router.post("/")
async def create_company(
    company_request: CreateCompanyRequest,
    language: str = Depends(get_language),
    db: AsyncSession = Depends(get_db),
) -> CompanyResponse:
    return await CompanyService.create_company(db, company_request, language)


@router.put("/{company_name}/tags")
async def add_tag(
    company_name: str,
    request: list[CreateTagRequest],
    language: str = Depends(get_language),
    db: AsyncSession = Depends(get_db),
) -> TagResponse:
    """기존 회사에 새 태그를 추가합니다."""
    # 태그 추가
    await TagService.add_tags_to_existing_company(db, company_name, request)

    company_data = await CompanyService.get_company(db, company_name, language)

    return TagResponse(company_name=company_data.company_name, tags=company_data.tags)


@router.delete("/{company_name}/tags/{tag_name}")
async def delete_tag(
    company_name: str,
    tag_name: str,
    language: str = Depends(get_language),
    db: AsyncSession = Depends(get_db),
) -> TagResponse:
    return await TagService.delete_tag(db, company_name, tag_name, language)
