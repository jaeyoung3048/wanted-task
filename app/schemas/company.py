from pydantic import BaseModel, RootModel

from app.core.language import LanguageCode
from app.schemas.base import ResponseModel


class CompanyResponse(ResponseModel):
    company_name: str
    tags: list[str]


class DynamicLanguageModel(RootModel[dict[LanguageCode, str]]):
    pass


class CreateTagRequest(BaseModel):
    tag_name: DynamicLanguageModel


class CreateCompanyRequest(BaseModel):
    company_name: DynamicLanguageModel
    tags: list[CreateTagRequest]
