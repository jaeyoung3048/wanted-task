from fastapi import APIRouter

from app.core.dependency import DatabaseSession, Language
from app.schemas.company import CompanyResponse, CreateCompanyRequest, CreateTagRequest
from app.schemas.tag import TagResponse
from app.services.company import CompanyService
from app.services.tag import TagService

router = APIRouter()


@router.get("/{company_name}")
async def get_company(
    language: Language,
    db: DatabaseSession,
    company_name: str,
) -> CompanyResponse:
    return await CompanyService.get_company(db, company_name, language)


@router.post("/")
async def create_company(
    request_body: CreateCompanyRequest,
    language: Language,
    db: DatabaseSession,
) -> CompanyResponse:
    return await CompanyService.create_company(db, request_body, language)


@router.put("/{company_name}/tags")
async def add_tag(
    company_name: str,
    request_body: list[CreateTagRequest],
    language: Language,
    db: DatabaseSession,
) -> TagResponse:
    """기존 회사에 새 태그를 추가합니다."""
    # 태그 추가
    await TagService.add_tags_to_existing_company(db, company_name, request_body)

    company_data = await CompanyService.get_company(db, company_name, language)

    return TagResponse(company_name=company_data.company_name, tags=company_data.tags)


@router.delete("/{company_name}/tags/{tag_name}")
async def delete_tag(
    company_name: str,
    tag_name: str,
    language: Language,
    db: DatabaseSession,
) -> TagResponse:
    return await TagService.delete_tag(db, company_name, tag_name, language)
