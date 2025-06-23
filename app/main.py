from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI

from app.db.session import close_db, init_db


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """
    애플리케이션 라이프사이클 관리
    시작 시 데이터베이스 초기화, 종료 시 연결 정리
    """

    await init_db()
    yield
    await close_db()


app = FastAPI(
    title="WantedLab 과제용 API 서버",
    description="WantedLab 과제용 API 서버",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/")
async def read_root() -> dict[str, str]:
    return {"message": "Hello, World!"}


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "healthy"}
