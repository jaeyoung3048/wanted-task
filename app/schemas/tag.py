from app.schemas.base import ResponseModel
from app.schemas.company import CreateTagRequest


class TagResponse(ResponseModel):
    company_name: str
    tags: list[str]


class AddTagsRequest(ResponseModel):
    tags: list[CreateTagRequest]


class AddTagsResponse(ResponseModel):
    company_name: str
    linked: int
    created: int
    skipped: int
