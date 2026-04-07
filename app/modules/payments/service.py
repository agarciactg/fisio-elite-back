from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
 
from .models import Payment
from .schemas import PaymentCreate
from app.modules.appointments.models import Appointment
 
 
VALID_STATUSES = {"PAID", "PENDING", "CANCELED"}
VALID_METHODS  = {"Cash", "Credit Card", "Transfer", "Card"}
 
 
class PaymentService:
    def __init__(self, db: AsyncSession):
        self.db = db
 
    async def get_payments(self) -> list[Payment]:
        result = await self.db.execute(select(Payment))
        return result.scalars().all()
 
    async def create_payment(self, payment: PaymentCreate) -> Payment:
        appointment = await self.db.get(Appointment, payment.appointment_id)
        if not appointment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cita con id {payment.appointment_id} no encontrada.",
            )
 
        if appointment.status == "Canceled":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="No se puede registrar un pago para una cita cancelada.",
            )
 
        existing_payment = await self.db.execute(
            select(Payment).filter(Payment.appointment_id == payment.appointment_id)
        )
        if existing_payment.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"La cita {payment.appointment_id} ya tiene un pago registrado. Solo se permite un pago por cita.",
            )
 
        if payment.amount <= 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="El monto del pago debe ser mayor a $0.",
            )
 
        if payment.status and payment.status not in VALID_STATUSES:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Estado de pago inválido. Valores permitidos: {', '.join(VALID_STATUSES)}.",
            )
        if payment.payment_method and payment.payment_method not in VALID_METHODS:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Método de pago inválido. Valores permitidos: {', '.join(VALID_METHODS)}.",
            )
 
        try:
            db_payment = Payment(**payment.model_dump())
            self.db.add(db_payment)
            await self.db.commit()
            await self.db.refresh(db_payment)
            return db_payment
 
        except IntegrityError:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Esta cita ya tiene un pago registrado.",
            )
