from app.modules.therapists.schemas import TherapistDirectoryResponse
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.db.database import get_db
from .schemas import TherapistCreate, TherapistResponse
from .service import TherapistService

router = APIRouter()

def get_therapist_service(db: AsyncSession = Depends(get_db)):
    return TherapistService(db)

@router.get("/", response_model=List[TherapistResponse])
async def list_therapists(service: TherapistService = Depends(get_therapist_service)):
    return await service.get_therapists()

@router.post("/", response_model=TherapistResponse, status_code=status.HTTP_201_CREATED)
async def create_therapist(therapist: TherapistCreate, service: TherapistService = Depends(get_therapist_service)):
    return await service.create_therapist(therapist)
 
@router.get("/directory", response_model=TherapistDirectoryResponse)
async def get_therapist_directory(db: AsyncSession = Depends(get_db)):
    """
    Directorio completo del equipo médico con estado en tiempo real,
    carga de trabajo semanal y resumen de rendimiento del equipo.
    GET /api/v1/therapists/directory
    """
    service = TherapistService(db)
    return await service.get_therapist_directory()
