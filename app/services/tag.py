from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.company import Company, CompanyTag
from app.models.tag import Tag, TagName
from app.schemas.tag import TagResponse


class TagService:
    @staticmethod
    async def get_company_name(company: Company, lang_code: str) -> str:
        current_name_by_lang_code = next((n.name for n in company.names if n.lang_code == lang_code), "")
        available_name = company.names[0].name
        return current_name_by_lang_code or available_name

    @staticmethod
    async def get_tag(db: AsyncSession, tag: str, lang_code: str) -> list[TagResponse]:
        target_tag_query = await db.execute(select(TagName.tag_id).where(TagName.name == tag))
        target_tag = target_tag_query.scalar_one_or_none()

        if not target_tag:
            raise HTTPException(status_code=404, detail="Tag not found")

        search_query = await db.execute(
            (
                select(Company)
                .join(Company.tags)
                .join(CompanyTag.tag)
                .join(Tag.names)
                .where(TagName.name == tag)
                .options(
                    selectinload(Company.names),
                    selectinload(Company.tags).selectinload(CompanyTag.tag).selectinload(Tag.names),
                )
            )
        )

        searched_data = search_query.scalars().all()

        return [
            TagResponse(
                company_name=await TagService.get_company_name(result, lang_code),
                tags=[n.name for ct in result.tags for n in ct.tag.names if n.lang_code == lang_code],
            )
            for result in searched_data
        ]
