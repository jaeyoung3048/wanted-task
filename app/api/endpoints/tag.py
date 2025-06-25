from fastapi import APIRouter, Query

from app.core.dependency import Language, TagServiceDep
from app.schemas.tag import TagResponse

router = APIRouter()


@router.get("")
async def get_tags(
    language: Language,
    tag_service: TagServiceDep,
    query: str = Query(..., description="태그명"),
) -> list[TagResponse]:
    return await tag_service.get_tag(query, language)
