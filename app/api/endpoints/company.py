from fastapi import APIRouter

from app.core.dependency import CompanyServiceDep, Language, TagServiceDep
from app.schemas.company import CompanyResponse, CreateCompanyRequest, CreateTagRequest
from app.schemas.tag import TagResponse

router = APIRouter()


@router.get("/{company_name}")
async def get_company(
    company_name: str,
    language: Language,
    company_service: CompanyServiceDep,
) -> CompanyResponse:
    return await company_service.get_company(company_name, language)


@router.post("")
async def create_company(
    request_body: CreateCompanyRequest,
    language: Language,
    company_service: CompanyServiceDep,
) -> CompanyResponse:
    return await company_service.create_company(request_body, language)


@router.put("/{company_name}/tags")
async def add_tag(
    company_name: str,
    request_body: list[CreateTagRequest],
    language: Language,
    tag_service: TagServiceDep,
    company_service: CompanyServiceDep,
) -> TagResponse:
    """기존 회사에 새 태그를 추가합니다."""
    # 태그 추가
    await tag_service.add_tags_to_existing_company(company_name, request_body)

    company_data = await company_service.get_company(company_name, language)

    return TagResponse(company_name=company_data.company_name, tags=company_data.tags)


@router.delete("/{company_name}/tags/{tag_name}")
async def delete_tag(
    company_name: str,
    tag_name: str,
    language: Language,
    tag_service: TagServiceDep,
) -> TagResponse:
    return await tag_service.delete_tag(company_name, tag_name, language)
