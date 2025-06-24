from app.schemas.base import ResponseModel


class TagResponse(ResponseModel):
    company_name: str
    tags: list[str]
