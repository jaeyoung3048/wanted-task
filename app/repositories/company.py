from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, with_loader_criteria

from app.core.language import choose_language
from app.models.company import Company, CompanyName, CompanyTag
from app.models.tag import Tag, TagName


class CompanyRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def find_by_name(self, company_name: str, language: str) -> Company | None:
        stmt = (
            select(Company)
            .distinct()
            .join(Company.names)
            .where(CompanyName.name == company_name)
            .options(
                selectinload(Company.names),
                selectinload(Company.tags)
                .selectinload(CompanyTag.tag)
                .selectinload(Tag.names),
                with_loader_criteria(
                    TagName, TagName.lang_code == language, include_aliases=True
                ),
            )
        )

        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def search_by_name_pattern(
        self, query: str, language: str
    ) -> list[CompanyName]:
        stmt = (
            select(CompanyName)
            .where(
                CompanyName.lang_code == language,
                text("MATCH(name) AGAINST(:query IN BOOLEAN MODE)"),
            )
            .params(query=f"+{query}")
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def create(self, company: Company) -> Company:
        self.db.add(company)
        await self.db.flush()
        return company

    async def exists_by_names(self, company_names: list[str]) -> bool:
        stmt = select(CompanyName).where(CompanyName.name.in_(company_names))
        result = await self.db.execute(stmt)
        return len(result.scalars().all()) > 0

    async def get_company_id_by_name(self, company_name: str) -> int | None:
        stmt = (
            select(Company.id)
            .join(CompanyName, Company.id == CompanyName.company_id)
            .where(CompanyName.name == company_name)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def add_company_name(
        self, company_id: int, name: str, lang_code: str
    ) -> CompanyName:
        company_name = CompanyName(
            company_id=company_id, name=name, lang_code=lang_code
        )

        self.db.add(company_name)
        await self.db.flush()
        return company_name

    async def get_company_names_by_language(
        self, company_id: int, lang_code: str
    ) -> str | None:
        stmt = select(CompanyName.name).where(
            CompanyName.company_id == company_id,
            CompanyName.lang_code == lang_code,
        )
        result = await self.db.execute(stmt)
        direct_result = result.scalar_one_or_none()

        if direct_result:
            return direct_result

        all_names_stmt = select(CompanyName).where(CompanyName.company_id == company_id)
        all_names_result = await self.db.execute(all_names_stmt)
        all_names = all_names_result.scalars().all()

        if all_names:
            available_langs = [name.lang_code for name in all_names]
            chosen_lang = choose_language(available_langs, lang_code)
            return next(
                name.name for name in all_names if name.lang_code == chosen_lang
            )

        return None
