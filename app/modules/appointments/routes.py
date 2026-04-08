from datetime import date

from typing import Optional, List

from fastapi import APIRouter, Depends, Query, status

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db

from .schemas import AppointmentCreate, AppointmentResponse, AppointmentCalendarItem
from .service import AppointmentService

router = APIRouter()

def get_appointment_service(db: AsyncSession = Depends(get_db)):
    return AppointmentService(db)

@router.get("/", response_model=List[AppointmentResponse])
async def list_appointments(service: AppointmentService = Depends(get_appointment_service)):
    return await service.get_appointments()

@router.post("/", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
async def create_appointment(appointment: AppointmentCreate, service: AppointmentService = Depends(get_appointment_service)):
    return await service.create_appointment(appointment)

@router.get("/by-day", response_model=list[AppointmentCalendarItem])
async def get_appointments_by_day(
    date: date = Query(..., description="Fecha en formato YYYY-MM-DD"),
    therapist_id: Optional[int] = Query(None, description="Filtrar por terapeuta"),
    db: AsyncSession = Depends(get_db),
):
    """Appointments for a specific day. Used by the Calendar's Day view."""
    service = AppointmentService(db)
    return await service.get_by_day(date, therapist_id)
 
 
@router.get("/by-week", response_model=list[AppointmentCalendarItem])
async def get_appointments_by_week(
    date: date = Query(..., description="Cualquier día de la semana (YYYY-MM-DD)"),
    therapist_id: Optional[int] = Query(None, description="Filtrar por terapeuta"),
    db: AsyncSession = Depends(get_db),
):
    """Appointments for a week (Monday–Sunday) containing the given date. Used by the Calendar's Week view."""
    service = AppointmentService(db)
    return await service.get_by_week(date, therapist_id)
 
 
@router.get("/by-month", response_model=list[AppointmentCalendarItem])
async def get_appointments_by_month(
    year:  int = Query(..., description="Año, ej: 2026"),
    month: int = Query(..., ge=1, le=12, description="Mes 1–12"),
    therapist_id: Optional[int] = Query(None, description="Filtrar por terapeuta"),
    db: AsyncSession = Depends(get_db),
):
    """Appointments for a full month. Used by the Calendar's Month view."""
    service = AppointmentService(db)
    return await service.get_by_month(year, month, therapist_id)

