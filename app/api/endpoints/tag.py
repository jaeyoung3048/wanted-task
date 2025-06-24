from fastapi import APIRouter, Query

from app.core.dependency import DatabaseSession, Language
from app.schemas.tag import TagResponse
from app.services.tag import TagService

router = APIRouter()


@router.get("/")
async def get_tags(
    language: Language,
    db: DatabaseSession,
    query: str = Query(..., description="태그명"),
) -> list[TagResponse]:
    return await TagService.get_tag(db, query, language)
