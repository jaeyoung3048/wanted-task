from fastapi import HTTPException
from sqlalchemy import and_, delete, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.company import Company, CompanyName, CompanyTag
from app.models.tag import Tag, TagName
from app.schemas.company import CreateTagRequest
from app.schemas.tag import TagResponse


class TagService:
    @staticmethod
    async def get_company_name(company: Company, lang_code: str) -> str:
        current_name_by_lang_code = next(
            (n.name for n in company.names if n.lang_code == lang_code), ""
        )
        available_name = company.names[0].name
        return current_name_by_lang_code or available_name

    @staticmethod
    async def get_tag(db: AsyncSession, tag: str, lang_code: str) -> list[TagResponse]:
        target_tag_query = await db.execute(
            select(TagName.tag_id).where(TagName.name == tag)
        )
        target_tag = target_tag_query.scalar_one_or_none()

        if not target_tag:
            raise HTTPException(status_code=404, detail="Tag not found")

        search_query = await db.execute(
            select(Company)
            .join(Company.tags)
            .join(CompanyTag.tag)
            .join(Tag.names)
            .where(TagName.name == tag)
            .options(
                selectinload(Company.names),
                selectinload(Company.tags)
                .selectinload(CompanyTag.tag)
                .selectinload(Tag.names),
            )
        )

        searched_data = search_query.scalars().all()

        return [
            TagResponse(
                company_name=await TagService.get_company_name(result, lang_code),
                tags=[
                    n.name
                    for ct in result.tags
                    for n in ct.tag.names
                    if n.lang_code == lang_code
                ],
            )
            for result in searched_data
        ]

    @staticmethod
    async def find_existing_tag_by_names(
        db: AsyncSession, tag_names: dict[str, str]
    ) -> Tag | None:
        if not tag_names:
            return None

        tag_conditions = []
        for lang_code, tag_name in tag_names.items():
            tag_conditions.append(
                and_(TagName.name == tag_name, TagName.lang_code == lang_code)
            )

        existing_tags_query = await db.execute(
            select(Tag)
            .join(TagName)
            .where(or_(*tag_conditions))
            .options(selectinload(Tag.names))
        )
        existing_tags = existing_tags_query.scalars().all()

        for tag in existing_tags:
            tag_lang_names = {(tn.lang_code, tn.name) for tn in tag.names}
            requested_lang_names = {
                (lang_code, tag_name) for lang_code, tag_name in tag_names.items()
            }

            if requested_lang_names.intersection(tag_lang_names):
                return tag

        return None

    @staticmethod
    async def add_missing_tag_names(
        db: AsyncSession, tag: Tag, tag_names: dict[str, str]
    ) -> None:
        existing_lang_codes = {tn.lang_code for tn in tag.names}

        for lang_code, tag_name in tag_names.items():
            if lang_code not in existing_lang_codes:
                new_tag_name = TagName(
                    tag_id=tag.id, name=tag_name, lang_code=lang_code
                )
                db.add(new_tag_name)

    @staticmethod
    async def create_tag_with_names(db: AsyncSession, tag_names: dict[str, str]) -> Tag:
        new_tag = Tag()
        db.add(new_tag)
        await db.flush()

        for lang_code, tag_name in tag_names.items():
            tag_name_obj = TagName(
                tag_id=new_tag.id, name=tag_name, lang_code=lang_code
            )
            db.add(tag_name_obj)

        return new_tag

    @staticmethod
    async def link_company_to_tag(
        db: AsyncSession, company_id: int, tag_id: int
    ) -> bool:
        existing_relation = await db.execute(
            select(CompanyTag).where(
                CompanyTag.company_id == company_id, CompanyTag.tag_id == tag_id
            )
        )

        if existing_relation.scalar_one_or_none():
            return False

        company_tag = CompanyTag(company_id=company_id, tag_id=tag_id)
        db.add(company_tag)
        return True

    @staticmethod
    async def process_company_tags(
        db: AsyncSession, company_id: int, tag_requests: list[CreateTagRequest]
    ) -> list[int]:
        processed_tag_names = set()
        created_tag_ids: list[int] = []

        for tag_request in tag_requests:
            requested_tag_names = list(tag_request.tag_name.root.values())

            first_tag_name = requested_tag_names[0] if requested_tag_names else ""
            if first_tag_name in processed_tag_names:
                continue
            processed_tag_names.add(first_tag_name)

            existing_tag = await TagService.find_existing_tag_by_names(
                db, tag_request.tag_name.root
            )

            if existing_tag:
                await TagService.add_missing_tag_names(
                    db, existing_tag, tag_request.tag_name.root
                )
                tag_to_link = existing_tag
            else:
                tag_to_link = await TagService.create_tag_with_names(
                    db, tag_request.tag_name.root
                )

            await TagService.link_company_to_tag(db, company_id, tag_to_link.id)
            created_tag_ids.append(tag_to_link.id)

        return created_tag_ids

    @staticmethod
    async def get_tags_in_order(
        db: AsyncSession, tag_ids: list[int], language: str
    ) -> list[str]:
        if not tag_ids:
            return []

        tag_names_query = await db.execute(
            select(TagName.tag_id, TagName.name).where(
                TagName.tag_id.in_(tag_ids), TagName.lang_code == language
            )
        )
        tag_names_result = tag_names_query.all()

        tag_id_to_name = {tag_id: name for tag_id, name in tag_names_result}

        return [
            tag_id_to_name.get(tag_id, "")
            for tag_id in tag_ids
            if tag_id in tag_id_to_name
        ]

    @staticmethod
    async def add_tags_to_existing_company(
        db: AsyncSession, company_name: str, tag_requests: list[CreateTagRequest]
    ) -> dict[str, int]:
        company_query = await db.execute(
            select(Company).join(Company.names).where(CompanyName.name == company_name)
        )
        company = company_query.scalar_one_or_none()

        if not company:
            raise HTTPException(status_code=404, detail="Company not found")

        existing_company_tags_query = await db.execute(
            select(CompanyTag.tag_id).where(CompanyTag.company_id == company.id)
        )
        existing_tag_ids = set(existing_company_tags_query.scalars().all())

        result = {
            "linked": 0,
            "created": 0,
            "skipped": 0,
        }

        processed_tag_names = set()

        for tag_request in tag_requests:
            requested_tag_names = list(tag_request.tag_name.root.values())

            first_tag_name = requested_tag_names[0] if requested_tag_names else ""
            if first_tag_name in processed_tag_names:
                continue
            processed_tag_names.add(first_tag_name)

            existing_tag = await TagService.find_existing_tag_by_names(
                db, tag_request.tag_name.root
            )

            if existing_tag:
                if existing_tag.id in existing_tag_ids:
                    result["skipped"] += 1
                    continue

                await TagService.link_company_to_tag(db, company.id, existing_tag.id)
                result["linked"] += 1
            else:
                new_tag = await TagService.create_tag_with_names(
                    db, tag_request.tag_name.root
                )
                await TagService.link_company_to_tag(db, company.id, new_tag.id)
                result["created"] += 1

        await db.commit()
        return result

    @staticmethod
    async def delete_tag(
        db: AsyncSession, company_name: str, tag_name: str, language: str
    ) -> TagResponse:
        company_query = await db.execute(
            select(Company).join(Company.names).where(CompanyName.name == company_name)
        )
        company = company_query.scalar_one_or_none()

        if not company:
            raise HTTPException(status_code=404, detail="Company not found")

        tag_query = await db.execute(
            select(Tag).join(TagName).where(TagName.name == tag_name)
        )
        tag = tag_query.scalar_one_or_none()

        if not tag:
            raise HTTPException(status_code=404, detail="Tag not found")

        await db.execute(
            delete(CompanyTag).where(
                CompanyTag.company_id == company.id, CompanyTag.tag_id == tag.id
            )
        )
        await db.commit()

        remaining_tags_query = await db.execute(
            select(TagName.name)
            .join(Tag)
            .join(CompanyTag)
            .where(CompanyTag.company_id == company.id, TagName.lang_code == language)
            .order_by(TagName.name)
        )
        remaining_tags = [tag_name for tag_name in remaining_tags_query.scalars().all()]

        company_name_query = await db.execute(
            select(CompanyName.name).where(
                CompanyName.company_id == company.id, CompanyName.lang_code == language
            )
        )
        company_name_in_language = company_name_query.scalar_one_or_none()

        if not company_name_in_language:
            first_name_query = await db.execute(
                select(CompanyName.name)
                .where(CompanyName.company_id == company.id)
                .limit(1)
            )
            company_name_in_language = first_name_query.scalar_one()

        return TagResponse(company_name=company_name_in_language, tags=remaining_tags)
