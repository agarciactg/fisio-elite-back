from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .models import Payment
from .schemas import PaymentCreate

class PaymentService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_payments(self):
        result = await self.db.execute(select(Payment))
        return result.scalars().all()

    async def create_payment(self, payment: PaymentCreate) -> Payment:
        db_payment = Payment(**payment.model_dump())
        self.db.add(db_payment)
        await self.db.commit()
        await self.db.refresh(db_payment)
        return db_payment
