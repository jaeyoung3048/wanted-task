from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, PrimaryKeyConstraint, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, BasicDateTimeMixin, PrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.tag import Tag


class Company(Base, PrimaryKeyMixin, BasicDateTimeMixin):
    __tablename__ = "company"

    names: Mapped[list["CompanyName"]] = relationship(
        back_populates="company", passive_deletes=True, cascade="all, delete-orphan"
    )
    tags: Mapped[list["CompanyTag"]] = relationship(
        back_populates="company", passive_deletes=True, cascade="all, delete-orphan"
    )


class CompanyName(Base, PrimaryKeyMixin, BasicDateTimeMixin):
    __tablename__ = "company_name"

    company_id: Mapped[int] = mapped_column(ForeignKey("company.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    lang_code: Mapped[str] = mapped_column(String(2), nullable=False)

    company: Mapped["Company"] = relationship(back_populates="names", passive_deletes=True)

    __table_args__ = (UniqueConstraint("company_id", "lang_code", name="uq_companyname_lang"),)


class CompanyTag(Base):
    __tablename__ = "company_tag"

    company_id: Mapped[int] = mapped_column(ForeignKey("company.id", ondelete="CASCADE"), nullable=False)
    tag_id: Mapped[int] = mapped_column(ForeignKey("tag.id", ondelete="CASCADE"), nullable=False)

    company: Mapped["Company"] = relationship(back_populates="tags", passive_deletes=True)
    tag: Mapped["Tag"] = relationship(back_populates="companies", passive_deletes=True)

    __table_args__ = (PrimaryKeyConstraint("company_id", "tag_id", name="pk_company_tag"),)
