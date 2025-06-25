import asyncio
from collections.abc import Generator, Iterable
from typing import Any

import pytest
import pytest_asyncio
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.main import app
from dummy.insert_dummy_data import insert_dummy_data
from tests.factories.company import (
    CompanyFactory,
    CompanyNameFactory,
    CompanyTagFactory,
)
from tests.factories.tag import TagFactory, TagNameFactory


class TrackingSession(Session):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.created_objects: list[object] = []

    def add(self, instance: object, _warn: bool = True) -> None:
        super().add(instance, _warn)
        self.created_objects.append(instance)

    def add_all(self, instances: Iterable[object]) -> None:
        super().add_all(instances)
        self.created_objects.extend(instances)


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_db_with_data() -> None:
    try:
        base_url = settings.base_database_url
        if base_url:
            base_engine = create_async_engine(base_url)
            async with base_engine.begin() as conn:
                await conn.execute(text(f"DROP DATABASE IF EXISTS {settings.DB_NAME}"))
                await conn.execute(text(f"CREATE DATABASE {settings.DB_NAME}"))
            await base_engine.dispose()
    except Exception:
        pass

    config = Config()
    config.set_main_option("sqlalchemy.url", settings.database_url)
    config.set_main_option("script_location", "migrations")

    command.upgrade(config, "head")
    await insert_dummy_data()


def create_sync_engine() -> Engine:
    sync_url = settings.database_url.replace("+aiomysql", "+mysqldb")
    return create_engine(sync_url, echo=False)


@pytest.fixture(scope="function", autouse=True)
def test_session() -> Generator[TrackingSession, None, None]:
    engine = create_sync_engine()
    SessionLocal = sessionmaker(bind=engine, class_=TrackingSession)  # noqa: N806
    session = SessionLocal()

    CompanyFactory._meta.sqlalchemy_session = session  # type: ignore
    CompanyNameFactory._meta.sqlalchemy_session = session  # type: ignore
    CompanyTagFactory._meta.sqlalchemy_session = session  # type: ignore
    TagFactory._meta.sqlalchemy_session = session  # type: ignore
    TagNameFactory._meta.sqlalchemy_session = session  # type: ignore

    yield session

    for obj in reversed(session.created_objects):
        if obj in session:
            session.delete(obj)

    try:
        session.commit()
    except Exception:
        session.rollback()
    finally:
        session.close()


@pytest.fixture
def api() -> Generator[TestClient, None, None]:
    with TestClient(app) as client:
        yield client
