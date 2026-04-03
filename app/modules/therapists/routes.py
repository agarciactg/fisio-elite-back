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
