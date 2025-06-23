from app.schemas.base import ResponseModel


class SearchResponse(ResponseModel):
    company_name: str
