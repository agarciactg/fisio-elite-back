from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.db.database import get_db
from .schemas import PaymentCreate, PaymentResponse
from .service import PaymentService

router = APIRouter()

def get_payment_service(db: AsyncSession = Depends(get_db)):
    return PaymentService(db)

@router.get("/", response_model=List[PaymentResponse])
async def list_payments(service: PaymentService = Depends(get_payment_service)):
    return await service.get_payments()

@router.post("/", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def create_payment(payment: PaymentCreate, service: PaymentService = Depends(get_payment_service)):
    return await service.create_payment(payment)
