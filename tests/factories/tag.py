from __future__ import annotations

from factory.declarations import Iterator, SubFactory
from factory.faker import Faker

from app.models.tag import Tag, TagName
from tests.factories.base import TestFactory


class TagFactory(TestFactory):
    class Meta:
        model = Tag


class TagNameFactory(TestFactory):
    tag = SubFactory(TagFactory)
    name = Faker("word")
    lang_code = Iterator(["en", "ko", "ja"])

    class Meta:
        model = TagName


__all__ = [
    "TagFactory",
    "TagNameFactory",
]
