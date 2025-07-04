from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class PrimaryKeyMixin:
    id: Mapped[int] = mapped_column(
        INTEGER(unsigned=True),  # type: ignore[no-untyped-call]
        primary_key=True,
        autoincrement=True,
    )


class BasicDateTimeMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now, server_default=func.now()
    )
