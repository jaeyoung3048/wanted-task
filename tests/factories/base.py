from __future__ import annotations

from factory.alchemy import SQLAlchemyModelFactory


class TestFactory(SQLAlchemyModelFactory):
    class Meta:
        abstract = True
        sqlalchemy_session = None
        sqlalchemy_session_persistence = "commit"
