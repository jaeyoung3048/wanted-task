from pydantic import BaseModel


class TagResponse(BaseModel):
    company_name: str
    tags: list[str]
