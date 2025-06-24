from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependency import get_db, get_language
from app.schemas.tag import AddTagsRequest, TagResponse
from app.services.company import CompanyService
from app.services.tag import TagService

router = APIRouter()


@router.get("/")
async def get_tags(
    query: str = Query(..., description="태그명"),
    language: str = Depends(get_language),
    db: AsyncSession = Depends(get_db),
) -> list[TagResponse]:
    return await TagService.get_tag(db, query, language)


@router.put("/{company_name}/tags")
async def add_tag(
    company_name: str,
    request: AddTagsRequest,
    language: str = Depends(get_language),
    db: AsyncSession = Depends(get_db),
) -> TagResponse:
    """기존 회사에 새 태그를 추가합니다."""
    # 태그 추가
    await TagService.add_tags_to_existing_company(db, company_name, request.tags)

    company_data = await CompanyService.get_company(db, company_name, language)

    return TagResponse(company_name=company_data.company_name, tags=company_data.tags)
