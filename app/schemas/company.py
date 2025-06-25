from pydantic import BaseModel, ConfigDict, RootModel, model_validator

from app.core.language import validate_language_code
from app.schemas.base import ResponseModel


class CompanyResponse(ResponseModel):
    company_name: str
    tags: list[str]


class DynamicLanguageModel(RootModel[dict[str, str]]):
    @model_validator(mode="before")
    @classmethod
    def _validate_language_codes(
        cls, data: dict[str, str]
    ) -> dict[str, dict[str, str]]:
        for key in data.keys():
            if not validate_language_code(key):
                raise ValueError("Invalid language code")
        return {"root": data}

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "ko": "string",
                "en": "string",
                "jp": "string",
            }
        },
    )


class CreateTagRequest(BaseModel):
    tag_name: DynamicLanguageModel


class CreateCompanyRequest(BaseModel):
    company_name: DynamicLanguageModel
    tags: list[CreateTagRequest]
