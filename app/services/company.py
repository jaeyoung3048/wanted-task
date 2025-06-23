from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.company import CompanyName
from app.schemas.search import SearchResponse


class CompanyService:
    @staticmethod
    async def search(db: AsyncSession, query: str, language: str) -> list[SearchResponse]:
        data = await db.execute(
            select(CompanyName).where(CompanyName.lang_code == language, CompanyName.name.ilike(f"%{query}%"))
        )
        result = data.scalars().all()

        return [SearchResponse(company_name=result.name) for result in result]
