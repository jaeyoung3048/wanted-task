from pydantic import BaseModel

from app.schemas.base import ResponseModel


class TagResponse(BaseModel):
    company_name: str
    tags: list[str]


class AddTagsResponse(ResponseModel):
    company_name: str
    linked: int
    created: int
    skipped: int
