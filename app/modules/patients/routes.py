from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from .schemas import PatientCreate, PatientResponse
from .service import PatientService
from typing import List

router = APIRouter()

def get_patient_service(db: AsyncSession = Depends(get_db)):
    return PatientService(db)

@router.get("/", response_model=List[PatientResponse])
async def list_patients(service: PatientService = Depends(get_patient_service)):
    return await service.get_patients()

@router.post("/", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
async def create_patient(patient: PatientCreate, service: PatientService = Depends(get_patient_service)):
    return await service.create_patient(patient)
