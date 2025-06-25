from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.language import choose_language
from app.db.transaction import transactional
from app.repositories.company import CompanyRepository
from app.repositories.company_tag import CompanyTagRepository
from app.repositories.tag import TagRepository
from app.schemas.company import CreateTagRequest
from app.schemas.tag import TagResponse


class TagService:
    def __init__(
        self,
        db: AsyncSession,
        company_repo: CompanyRepository,
        tag_repo: TagRepository,
        company_tag_repo: CompanyTagRepository,
    ):
        self.db = db
        self.company_repo = company_repo
        self.tag_repo = tag_repo
        self.company_tag_repo = company_tag_repo

    async def get_tag(self, tag_name: str, language: str) -> list[TagResponse]:
        tag = await self.tag_repo.find_by_name(tag_name)
        if not tag:
            raise HTTPException(status_code=404, detail="Tag not found")

        companies = await self.tag_repo.get_companies_by_tag_name(tag_name)

        result = []
        for company in companies:
            available_company_langs = [name.lang_code for name in company.names]
            chosen_company_lang = choose_language(available_company_langs, language)
            company_name_in_lang = next(
                name.name
                for name in company.names
                if name.lang_code == chosen_company_lang
            )

            tag_names = []
            for company_tag in company.tags:
                tag_available_langs = [name.lang_code for name in company_tag.tag.names]
                tag_chosen_lang = choose_language(tag_available_langs, language)
                tag_name_in_lang = next(
                    name.name
                    for name in company_tag.tag.names
                    if name.lang_code == tag_chosen_lang
                )
                tag_names.append(tag_name_in_lang)

            result.append(
                TagResponse(company_name=company_name_in_lang, tags=tag_names)
            )

        return result

    @transactional
    async def add_tags_to_existing_company(
        self, company_name: str, tag_requests: list[CreateTagRequest]
    ) -> dict[str, int]:
        company_id = await self.company_repo.get_company_id_by_name(company_name)
        if not company_id:
            raise HTTPException(status_code=404, detail="Company not found")

        existing_tag_ids = set(
            await self.company_tag_repo.get_tag_ids_by_company_id(company_id)
        )

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

            existing_tag_result = await self.tag_repo.find_by_names(
                tag_request.tag_name.root
            )

            if existing_tag_result:
                tag_id, existing_lang_codes = existing_tag_result

                if tag_id in existing_tag_ids:
                    result["skipped"] += 1
                    continue

                await self.tag_repo.add_missing_tag_names(
                    tag_id, existing_lang_codes, tag_request.tag_name.root
                )

                await self.company_tag_repo.create_relation(company_id, tag_id)
                result["linked"] += 1
            else:
                new_tag = await self.tag_repo.create_with_names(
                    tag_request.tag_name.root
                )
                await self.company_tag_repo.create_relation(company_id, new_tag.id)
                result["created"] += 1

        return result

    @transactional
    async def delete_tag(
        self, company_name: str, tag_name: str, language: str
    ) -> TagResponse:
        company_id = await self.company_repo.get_company_id_by_name(company_name)
        if not company_id:
            raise HTTPException(status_code=404, detail="Company not found")

        tag = await self.tag_repo.find_by_name(tag_name)
        if not tag:
            raise HTTPException(status_code=404, detail="Tag not found")

        await self.company_tag_repo.delete_relation(company_id, tag.id)

        remaining_tag_names = await self.tag_repo.get_tag_names_by_company_id(
            company_id, language
        )

        company_name_in_language = (
            await self.company_repo.get_company_names_by_language(company_id, language)
        )

        if not company_name_in_language:
            company = await self.company_repo.find_by_name(company_name, language)
            if company and company.names:
                available_langs = [name.lang_code for name in company.names]
                chosen_lang = choose_language(available_langs, language)
                company_name_in_language = next(
                    name.name for name in company.names if name.lang_code == chosen_lang
                )
            else:
                company_name_in_language = company_name

        return TagResponse(
            company_name=company_name_in_language, tags=remaining_tag_names
        )
