from __future__ import annotations

from factory.declarations import Iterator, SubFactory
from factory.faker import Faker

from app.models.company import Company, CompanyName, CompanyTag
from tests.factories.base import TestFactory
from tests.factories.tag import TagFactory


class CompanyFactory(TestFactory):
    class Meta:
        model = Company


class CompanyNameFactory(TestFactory):
    company = SubFactory(CompanyFactory)
    name = Faker("company")
    lang_code = Iterator(["en", "ko", "ja"])

    class Meta:
        model = CompanyName


class CompanyTagFactory(TestFactory):
    company = SubFactory(CompanyFactory)
    tag = SubFactory(TagFactory)

    class Meta:
        model = CompanyTag


__all__ = [
    "CompanyFactory",
    "CompanyNameFactory",
    "CompanyTagFactory",
]
