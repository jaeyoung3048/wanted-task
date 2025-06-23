from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, with_loader_criteria

from app.models.company import Company, CompanyName, CompanyTag
from app.models.tag import Tag, TagName
from app.schemas.company import CompanyResponse
from app.schemas.search import SearchResponse


class CompanyService:
    @staticmethod
    async def search(db: AsyncSession, query: str, language: str) -> list[SearchResponse]:
        data = await db.execute(
            select(CompanyName).where(CompanyName.lang_code == language, CompanyName.name.ilike(f"%{query}%"))
        )
        result = data.scalars().all()

        return [SearchResponse(company_name=result.name) for result in result]

    @staticmethod
    async def get_company(db: AsyncSession, company_name: str, language: str) -> CompanyResponse:
        # 1. 입력받은 회사명(어떤 언어든)으로 회사를 찾기
        company_query = await db.execute(
            select(Company)
            .join(Company.names)
            .where(CompanyName.name == company_name)
            .options(
                selectinload(Company.names),
                selectinload(Company.tags).selectinload(CompanyTag.tag).selectinload(Tag.names),
                with_loader_criteria(TagName, TagName.lang_code == language, include_aliases=True),
            )
        )
        company = company_query.scalar_one_or_none()

        if not company:
            raise HTTPException(status_code=404, detail="Company not found")

        current_name = next((n.name for n in company.names if n.lang_code == language), None)

        if not current_name:
            raise HTTPException(status_code=404, detail="Company name not found")

        tag_names = [n.name for t in company.tags for n in t.tag.names if n.lang_code == language]

        return CompanyResponse(
            company_name=current_name or "",
            tags=sorted(tag_names),
        )
