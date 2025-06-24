from fastapi import APIRouter, Query

from app.core.dependency import DatabaseSession, Language
from app.schemas.search import SearchResponse
from app.services.company import CompanyService

router = APIRouter()


@router.get("/")
async def search(
    language: Language,
    db: DatabaseSession,
    query: str = Query(..., description="검색 쿼리"),
) -> list[SearchResponse]:
    return await CompanyService.search(db, query, language)
