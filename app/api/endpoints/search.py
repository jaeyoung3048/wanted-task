from fastapi import APIRouter, Query

from app.core.dependency import CompanyServiceDep, Language
from app.schemas.search import SearchResponse

router = APIRouter()


@router.get("")
async def search(
    language: Language,
    company_service: CompanyServiceDep,
    query: str = Query(..., description="검색 쿼리"),
) -> list[SearchResponse]:
    return await company_service.search(query, language)
