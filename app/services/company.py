from fastapi import HTTPException
from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, with_loader_criteria

from app.models.company import Company, CompanyName, CompanyTag
from app.models.tag import Tag, TagName
from app.schemas.company import CompanyResponse, CreateCompanyRequest
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

    @staticmethod
    async def create_company(db: AsyncSession, company_request: CreateCompanyRequest, language: str) -> CompanyResponse:
        # TODO[2025-06-24]: 태그 로직은 추후 분리 및 수정 필요
        company_names = list(company_request.company_name.root.values())

        existing_company_query = await db.execute(
            select(CompanyName.company_id).where(CompanyName.name.in_(company_names))
        )
        existing_company_ids = existing_company_query.scalars().all()

        if existing_company_ids:
            raise HTTPException(status_code=400, detail="Company already exists")

        company = Company()
        db.add(company)
        await db.flush()

        for lang_code, name in company_request.company_name.root.items():
            company_name = CompanyName(company_id=company.id, name=name, lang_code=lang_code)
            db.add(company_name)

        processed_tag_names = set()

        for tag_request in company_request.tags:
            requested_tag_names = list(tag_request.tag_name.root.values())

            first_tag_name = requested_tag_names[0] if requested_tag_names else ""
            if first_tag_name in processed_tag_names:
                continue
            processed_tag_names.add(first_tag_name)

            tag_conditions = []
            for lang_code, tag_name in tag_request.tag_name.root.items():
                tag_conditions.append(and_(TagName.name == tag_name, TagName.lang_code == lang_code))

            existing_tags_query = await db.execute(
                select(Tag).join(TagName).where(or_(*tag_conditions)).options(selectinload(Tag.names))
            )
            existing_tags = existing_tags_query.scalars().all()

            existing_tag = None
            for tag in existing_tags:
                tag_lang_names = {(tn.lang_code, tn.name) for tn in tag.names}
                requested_lang_names = {
                    (lang_code, tag_name) for lang_code, tag_name in tag_request.tag_name.root.items()
                }

                if requested_lang_names.intersection(tag_lang_names):
                    existing_tag = tag
                    break

            if existing_tag:
                existing_lang_codes = {tn.lang_code for tn in existing_tag.names}

                for lang_code, tag_name in tag_request.tag_name.root.items():
                    if lang_code not in existing_lang_codes:
                        new_tag_name = TagName(tag_id=existing_tag.id, name=tag_name, lang_code=lang_code)
                        db.add(new_tag_name)

                tag_to_link = existing_tag
            else:
                new_tag = Tag()
                db.add(new_tag)
                await db.flush()

                for lang_code, tag_name in tag_request.tag_name.root.items():
                    tag_name_obj = TagName(tag_id=new_tag.id, name=tag_name, lang_code=lang_code)
                    db.add(tag_name_obj)

                tag_to_link = new_tag

            existing_relation = await db.execute(
                select(CompanyTag).where(CompanyTag.company_id == company.id, CompanyTag.tag_id == tag_to_link.id)
            )

            if not existing_relation.scalar_one_or_none():
                company_tag = CompanyTag(company_id=company.id, tag_id=tag_to_link.id)
                db.add(company_tag)

        await db.commit()

        company_name_in_language = company_request.company_name.root.get(language, "")

        tags_query = await db.execute(
            select(TagName.name)
            .join(Tag)
            .join(CompanyTag)
            .where(CompanyTag.company_id == company.id, TagName.lang_code == language)
            .order_by(TagName.name)
        )
        tags_in_language = [tag for tag in tags_query.scalars().all()]

        return CompanyResponse(company_name=company_name_in_language, tags=tags_in_language)
