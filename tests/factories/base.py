from __future__ import annotations

from factory.alchemy import SQLAlchemyModelFactory


class AsyncAlchemyFactory(SQLAlchemyModelFactory):
    class Meta:
        abstract = True
        sqlalchemy_session = None
        sqlalchemy_session_persistence = "flush"
