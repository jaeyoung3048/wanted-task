from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.language import choose_language
from app.db.transaction import transactional
from app.models.company import Company
from app.repositories.company import CompanyRepository
from app.repositories.company_tag import CompanyTagRepository
from app.repositories.tag import TagRepository
from app.schemas.company import CompanyResponse, CreateCompanyRequest, CreateTagRequest
from app.schemas.search import SearchResponse


class CompanyService:
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

    async def get_company(self, company_name: str, language: str) -> CompanyResponse:
        data = await self.company_repo.find_by_name(company_name, language)

        if not data:
            raise HTTPException(status_code=404, detail="Company not found")

        available_langs = [name.lang_code for name in data.names]
        chosen_lang = choose_language(available_langs, language)
        company_name_in_lang = next(
            name for name in data.names if name.lang_code == chosen_lang
        )

        tag_names = []

        for company_tag in data.tags:
            tag_available_langs = [
                tag_name.lang_code for tag_name in company_tag.tag.names
            ]
            tag_chosen_lang = choose_language(tag_available_langs, language)
            tag_name = next(
                tag_name
                for tag_name in company_tag.tag.names
                if tag_name.lang_code == tag_chosen_lang
            )
            tag_names.append(tag_name.name)

        return CompanyResponse(
            company_name=company_name_in_lang.name,
            tags=tag_names,
        )

    @transactional
    async def create_company(
        self, request: CreateCompanyRequest, language: str
    ) -> CompanyResponse:
        company_names = list(request.company_name.root.values())
        if await self.company_repo.exists_by_names(company_names):
            raise HTTPException(status_code=400, detail="Company already exists")

        company = Company()
        created_company = await self.company_repo.create(company)

        for lang_code, name in request.company_name.root.items():
            await self.company_repo.add_company_name(
                created_company.id, name, lang_code
            )

        created_tag_ids = []
        if request.tags:
            created_tag_ids = await self._process_company_tags(
                created_company.id, request.tags
            )

        available_company_langs = list(request.company_name.root.keys())
        chosen_company_lang = choose_language(available_company_langs, language)
        company_name_in_language = request.company_name.root[chosen_company_lang]

        tags_in_language = []
        if created_tag_ids:
            tags_in_language = await self._get_tags_in_order(created_tag_ids, language)

        return CompanyResponse(
            company_name=company_name_in_language, tags=sorted(tags_in_language)
        )

    async def _process_company_tags(
        self, company_id: int, tag_requests: list[CreateTagRequest]
    ) -> list[int]:
        processed_tag_names = set()
        created_tag_ids: list[int] = []

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

                await self.tag_repo.add_missing_tag_names(
                    tag_id, existing_lang_codes, tag_request.tag_name.root
                )

                await self.company_tag_repo.create_relation(company_id, tag_id)
                created_tag_ids.append(tag_id)
            else:
                new_tag = await self.tag_repo.create_with_names(
                    tag_request.tag_name.root
                )
                await self.company_tag_repo.create_relation(company_id, new_tag.id)
                created_tag_ids.append(new_tag.id)

        return created_tag_ids

    async def _get_tags_in_order(self, tag_ids: list[int], language: str) -> list[str]:
        if not tag_ids:
            return []

        tag_id_to_name = await self.tag_repo.get_tag_names_by_ids(tag_ids, language)

        return [
            tag_id_to_name[tag_id] for tag_id in tag_ids if tag_id in tag_id_to_name
        ]

    async def search(self, query: str, language: str) -> list[SearchResponse]:
        search_data = await self.company_repo.search_by_name_pattern(query, language)

        return [SearchResponse(company_name=d.name) for d in search_data]
