from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.language import choose_language
from app.models.company import Company, CompanyTag
from app.models.tag import Tag, TagName


class TagRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def find_by_name(self, tag_name: str) -> Tag | None:
        stmt = (
            select(Tag)
            .join(TagName)
            .where(TagName.name == tag_name)
            .options(selectinload(Tag.names))
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_names(
        self, tag_names: dict[str, str]
    ) -> tuple[int, set[str]] | None:
        if not tag_names:
            return None

        tag_conditions = []
        for lang_code, tag_name in tag_names.items():
            tag_conditions.append(
                and_(TagName.name == tag_name, TagName.lang_code == lang_code)
            )

        stmt = (
            select(Tag)
            .join(TagName)
            .where(or_(*tag_conditions))
            .options(selectinload(Tag.names))
        )
        result = await self.db.execute(stmt)
        existing_tags = result.scalars().all()

        for tag in existing_tags:
            tag_lang_names = {(tn.lang_code, tn.name) for tn in tag.names}
            requested_lang_names = {
                (lang_code, tag_name) for lang_code, tag_name in tag_names.items()
            }

            if requested_lang_names.intersection(tag_lang_names):
                existing_lang_codes = {tn.lang_code for tn in tag.names}
                return (tag.id, existing_lang_codes)

        return None

    async def create_with_names(self, tag_names: dict[str, str]) -> Tag:
        new_tag = Tag()
        self.db.add(new_tag)
        await self.db.flush()

        for lang_code, tag_name in tag_names.items():
            tag_name_obj = TagName(
                tag_id=new_tag.id, name=tag_name, lang_code=lang_code
            )
            self.db.add(tag_name_obj)

        return new_tag

    async def add_missing_tag_names(
        self,
        tag_id: int,
        existing_lang_codes: set[str],
        tag_names: dict[str, str],
    ) -> None:
        for lang_code, tag_name in tag_names.items():
            if lang_code not in existing_lang_codes:
                new_tag_name = TagName(
                    tag_id=tag_id, name=tag_name, lang_code=lang_code
                )
                self.db.add(new_tag_name)

    async def get_companies_by_tag_name(self, tag_name: str) -> list[Company]:
        stmt = (
            select(Company)
            .join(Company.tags)
            .join(CompanyTag.tag)
            .join(Tag.names)
            .where(TagName.name == tag_name)
            .options(
                selectinload(Company.names),
                selectinload(Company.tags)
                .selectinload(CompanyTag.tag)
                .selectinload(Tag.names),
            )
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_tag_names_by_ids(
        self, tag_ids: list[int], language: str
    ) -> dict[int, str]:
        if not tag_ids:
            return {}

        stmt = select(TagName.tag_id, TagName.name).where(
            TagName.tag_id.in_(tag_ids), TagName.lang_code == language
        )
        result = await self.db.execute(stmt)
        direct_results = {tag_id: name for tag_id, name in result.all()}

        missing_tag_ids = set(tag_ids) - set(direct_results.keys())
        if missing_tag_ids:
            fallback_stmt = (
                select(Tag)
                .where(Tag.id.in_(missing_tag_ids))
                .options(selectinload(Tag.names))
            )
            fallback_result = await self.db.execute(fallback_stmt)
            tags = fallback_result.scalars().all()

            for tag in tags:
                if tag.names:
                    available_langs = [name.lang_code for name in tag.names]
                    chosen_lang = choose_language(available_langs, language)
                    chosen_name = next(
                        name.name for name in tag.names if name.lang_code == chosen_lang
                    )
                    direct_results[tag.id] = chosen_name

        return direct_results

    async def get_tag_names_by_company_id(
        self, company_id: int, language: str
    ) -> list[str]:
        stmt = (
            select(TagName.name)
            .join(Tag)
            .join(CompanyTag)
            .where(CompanyTag.company_id == company_id, TagName.lang_code == language)
            .order_by(TagName.name)
        )
        result = await self.db.execute(stmt)
        return [name for name in result.scalars().all()]
