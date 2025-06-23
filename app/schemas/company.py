from app.schemas.base import ResponseModel


class CompanyResponse(ResponseModel):
    company_name: str
    tags: list[str]
