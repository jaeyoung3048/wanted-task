from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.company import CompanyTag


class CompanyTagRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_relation(self, company_id: int, tag_id: int) -> CompanyTag:
        company_tag = CompanyTag(company_id=company_id, tag_id=tag_id)
        self.db.add(company_tag)
        await self.db.flush()
        return company_tag

    async def exists_relation(self, company_id: int, tag_id: int) -> bool:
        stmt = select(CompanyTag).where(
            CompanyTag.company_id == company_id, CompanyTag.tag_id == tag_id
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def delete_relation(self, company_id: int, tag_id: int) -> None:
        stmt = delete(CompanyTag).where(
            CompanyTag.company_id == company_id, CompanyTag.tag_id == tag_id
        )
        await self.db.execute(stmt)

    async def get_tag_ids_by_company_id(self, company_id: int) -> list[int]:
        stmt = select(CompanyTag.tag_id).where(CompanyTag.company_id == company_id)
        result = await self.db.execute(stmt)
        return [tag_id for tag_id in result.scalars().all()]
