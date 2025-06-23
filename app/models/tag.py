from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, BasicDateTimeMixin, PrimaryKeyMixin
from app.models.company import CompanyTag


class Tag(Base, PrimaryKeyMixin, BasicDateTimeMixin):
    __tablename__ = "tag"

    names: Mapped[list["TagName"]] = relationship(
        back_populates="tag", passive_deletes=True, cascade="all, delete-orphan"
    )
    companies: Mapped[list["CompanyTag"]] = relationship(
        back_populates="tag", passive_deletes=True, cascade="all, delete-orphan"
    )


class TagName(Base, PrimaryKeyMixin, BasicDateTimeMixin):
    __tablename__ = "tag_name"

    tag_id: Mapped[int] = mapped_column(ForeignKey("tag.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    lang_code: Mapped[str] = mapped_column(String(2), nullable=False)

    tag: Mapped["Tag"] = relationship(back_populates="names", passive_deletes=True)

    __table_args__ = (UniqueConstraint("tag_id", "lang_code", name="uq_tagname_lang"),)
