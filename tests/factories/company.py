from __future__ import annotations

from typing import TYPE_CHECKING

from factory.declarations import Iterator, SubFactory
from factory.faker import Faker

from app.models.company import Company, CompanyName, CompanyTag
from tests.factories.base import AsyncAlchemyFactory

if TYPE_CHECKING:
    from tests.factories.tag import TagFactory


class CompanyFactory(AsyncAlchemyFactory):
    class Meta:
        model = Company


class CompanyNameFactory(AsyncAlchemyFactory):
    company = SubFactory(CompanyFactory)
    name = Faker("company")
    lang_code = Iterator(["en", "ko", "ja"])

    class Meta:
        model = CompanyName


class CompanyTagFactory(AsyncAlchemyFactory):
    company = SubFactory(CompanyFactory)
    tag = SubFactory(TagFactory)

    class Meta:
        model = CompanyTag


__all__ = [
    "CompanyFactory",
    "CompanyNameFactory",
    "CompanyTagFactory",
]
