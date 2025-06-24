from __future__ import annotations

from app.models.company import Company, CompanyName, CompanyTag
from app.models.tag import Tag, TagName
from tests.factories import (
    CompanyFactory,
    CompanyNameFactory,
    CompanyTagFactory,
    TagFactory,
    TagNameFactory,
)


def test_tag_factory_build() -> None:
    tag = TagFactory.build()
    assert isinstance(tag, Tag)


def test_tagname_factory_build_sequence() -> None:
    tn1, tn2 = TagNameFactory.build_batch(2)
    assert isinstance(tn1, TagName) and isinstance(tn2, TagName)
    assert tn1.name != tn2.name
    assert isinstance(tn1.tag, Tag)
    assert tn1.name and isinstance(tn1.name, str)
    assert tn1.lang_code in {"en", "ko", "ja"}


def test_company_factory_build() -> None:
    company = CompanyFactory.build()
    assert isinstance(company, Company)


def test_companyname_factory_build() -> None:
    company_name = CompanyNameFactory.build()

    assert isinstance(company_name, CompanyName)
    assert isinstance(company_name.company, Company)
    assert company_name.name and isinstance(company_name.name, str)
    assert company_name.lang_code in {"en", "ko", "ja"}


def test_companytag_factory_build() -> None:
    company_tag = CompanyTagFactory.build()

    assert isinstance(company_tag, CompanyTag)
    assert isinstance(company_tag.company, Company)
    assert isinstance(company_tag.tag, Tag)
    assert company_tag.company is not None and company_tag.tag is not None
