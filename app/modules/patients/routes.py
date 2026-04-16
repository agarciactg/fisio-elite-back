from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from .schemas import PatientCreate, PatientUpdate, PatientResponse, PatientDirectoryResponse
from .service import PatientService
from typing import List

router = APIRouter()

def get_patient_service(db: AsyncSession = Depends(get_db)):
    return PatientService(db)

@router.get("/directory", response_model=PatientDirectoryResponse)
async def get_directory(service: PatientService = Depends(get_patient_service)):
    return await service.get_patient_directory()

@router.get("/", response_model=List[PatientResponse])
async def list_patients(service: PatientService = Depends(get_patient_service)):
    return await service.get_patients()

@router.post("/", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
async def create_patient(patient: PatientCreate, service: PatientService = Depends(get_patient_service)):
    return await service.create_patient(patient)

@router.put("/{patient_id}", response_model=PatientResponse)
async def update_patient(patient_id: int, patient: PatientUpdate, service: PatientService = Depends(get_patient_service)):
    return await service.update_patient(patient_id, patient)

@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_patient(patient_id: int, service: PatientService = Depends(get_patient_service)):
    await service.delete_patient(patient_id)
    return None
