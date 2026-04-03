from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.db.database import get_db
from .schemas import AppointmentCreate, AppointmentResponse
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
