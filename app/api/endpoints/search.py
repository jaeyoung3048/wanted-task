from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependency import get_db, get_language
from app.schemas.search import SearchResponse
from app.services.company import CompanyService

router = APIRouter()


@router.get("/")
async def search(
    query: str,
    language: str = Depends(get_language),
    db: AsyncSession = Depends(get_db),
) -> list[SearchResponse]:
    return await CompanyService.search(db, query, language)
