from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependency import get_db, get_language
from app.schemas.tag import TagResponse
from app.services.tag import TagService

router = APIRouter()


@router.get("/")
async def get_tags(
    query: str = Query(..., description="태그명"),
    language: str = Depends(get_language),
    db: AsyncSession = Depends(get_db),
) -> list[TagResponse]:
    return await TagService.get_tag(db, query, language)
