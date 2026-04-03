from pydantic import BaseModel
from typing import Optional
from decimal import Decimal

class PaymentBase(BaseModel):
    amount: Decimal
    status: str = "PENDING"
    payment_method: Optional[str] = None

class PaymentCreate(PaymentBase):
    appointment_id: int

class PaymentResponse(PaymentBase):
    id: int
    appointment_id: int

    class Config:
        from_attributes = True
