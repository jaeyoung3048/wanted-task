from fastapi import APIRouter

from app.api.endpoints import search

# 메인 API 라우터
api_router = APIRouter(prefix="")

api_router.include_router(search.router, prefix="/search", tags=["search"])
