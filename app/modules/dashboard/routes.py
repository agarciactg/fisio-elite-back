from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from .schemas import DashboardStatsResponse
from .service import DashboardService

router = APIRouter()

def get_dashboard_service(db: AsyncSession = Depends(get_db)):
    return DashboardService(db)

@router.get("/stats", response_model=DashboardStatsResponse)
async def get_stats(service: DashboardService = Depends(get_dashboard_service)):
    return await service.get_dashboard_stats()
