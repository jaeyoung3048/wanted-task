from fastapi import APIRouter

from app.api.endpoints import company, search, tag

# 메인 API 라우터
api_router = APIRouter(prefix="")

api_router.include_router(search.router, prefix="/search", tags=["search"])
api_router.include_router(company.router, prefix="/companies", tags=["companies"])
api_router.include_router(tag.router, prefix="/tags", tags=["tags"])
