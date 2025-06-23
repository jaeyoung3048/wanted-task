from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependency import get_db, get_language
from app.schemas.company import CompanyResponse
from app.services.company import CompanyService

router = APIRouter()


@router.get("/{company_name}")
async def get_company(
    company_name: str,
    language: str = Depends(get_language),
    db: AsyncSession = Depends(get_db),
) -> CompanyResponse:
    return await CompanyService.get_company(db, company_name, language)
