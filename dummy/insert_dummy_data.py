# ruff: noqa
# mypy: ignore-errors

import asyncio
import csv
from typing import Dict, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import close_db, get_async_session, init_db
from app.models.company import Company, CompanyName, CompanyTag
from app.models.tag import Tag, TagName


async def get_or_create_tag(session: AsyncSession, tag_names: Dict[str, str]) -> Tag:
    ko_name = tag_names.get("ko", "").strip()
    if ko_name:
        result = await session.execute(
            select(Tag)
            .join(TagName)
            .where(TagName.name == ko_name, TagName.lang_code == "ko")
        )
        existing_tag = result.scalar_one_or_none()
        if existing_tag:
            return existing_tag

    tag = Tag()
    session.add(tag)
    await session.flush()

    for lang_code, name in tag_names.items():
        if name.strip():
            tag_name = TagName(tag_id=tag.id, name=name.strip(), lang_code=lang_code)
            session.add(tag_name)

    return tag


async def process_tags(
    session: AsyncSession, tag_string: str, lang_code: str
) -> List[str]:
    if not tag_string.strip():
        return []

    return [tag.strip() for tag in tag_string.split("|") if tag.strip()]


async def insert_company_data(session: AsyncSession, row_data: Dict[str, str]) -> None:
    company = Company()
    session.add(company)
    await session.flush()

    company_names = {
        "ko": row_data.get("company_ko", "").strip(),
        "en": row_data.get("company_en", "").strip(),
        "ja": row_data.get("company_ja", "").strip(),
    }

    for lang_code, name in company_names.items():
        if name:
            company_name = CompanyName(
                company_id=company.id, name=name, lang_code=lang_code
            )
            session.add(company_name)

    tag_data = {
        "ko": await process_tags(session, row_data.get("tag_ko", ""), "ko"),
        "en": await process_tags(session, row_data.get("tag_en", ""), "en"),
        "ja": await process_tags(session, row_data.get("tag_ja", ""), "ja"),
    }

    max_tags = max(len(tags) for tags in tag_data.values())

    for i in range(max_tags):
        tag_names = {}
        for lang_code, tags in tag_data.items():
            if i < len(tags):
                tag_names[lang_code] = tags[i]

        if tag_names:
            tag = await get_or_create_tag(session, tag_names)

            existing_relation = await session.execute(
                select(CompanyTag).where(
                    CompanyTag.company_id == company.id, CompanyTag.tag_id == tag.id
                )
            )

            if not existing_relation.scalar_one_or_none():
                company_tag = CompanyTag(company_id=company.id, tag_id=tag.id)
                session.add(company_tag)


async def insert_dummy_data() -> None:
    await init_db()

    dummy_data = []

    with open("dummy/company_tag_sample.csv", "r", encoding="utf-8") as f:
        data = csv.reader(f)
        key_list = []

        for i, row in enumerate(data):
            if i == 0:
                key_list = row
                continue
            dummy_data.append(dict(zip(key_list, row)))

    async for session in get_async_session():
        try:
            for idx, row_data in enumerate(dummy_data):
                await insert_company_data(session, row_data)

                if (idx + 1) % 10 == 0:
                    await session.commit()

            await session.commit()

        except Exception as e:
            await session.rollback()
            print(f"에러 발생: {e}")
            raise
        finally:
            await session.close()

    await close_db()


async def main():
    await insert_dummy_data()


if __name__ == "__main__":
    asyncio.run(main())
