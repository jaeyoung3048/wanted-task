from pydantic import BaseModel, RootModel

from app.schemas.base import ResponseModel


class CompanyResponse(ResponseModel):
    company_name: str
    tags: list[str]


class DynamicLanguageModel(RootModel[dict[str, str]]):
    pass

    # @model_validator(mode="after")
    # def validate_keys(self) -> "DynamicLanguageModel":
    #     invalid = False  # TODO[2025-06-24]: 추후 국가코드 검증 로직 필요
    #     if invalid:
    #         raise ValueError(f"Invalid lang codes: {invalid}")
    #     return self


class CreateTagRequest(BaseModel):
    tag_name: DynamicLanguageModel


class CreateCompanyRequest(BaseModel):
    company_name: DynamicLanguageModel
    tags: list[CreateTagRequest]
