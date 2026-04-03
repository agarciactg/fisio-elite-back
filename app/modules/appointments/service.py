from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from .models import Appointment
from .schemas import AppointmentCreate

class AppointmentService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_appointments(self):
        # We use selectinload to eagerly fetch relationships to populate nested Pydantic models
        stmt = select(Appointment).options(
            selectinload(Appointment.patient),
            selectinload(Appointment.therapist)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def create_appointment(self, appointment: AppointmentCreate) -> Appointment:
        db_appointment = Appointment(**appointment.model_dump())
        self.db.add(db_appointment)
        await self.db.commit()
        await self.db.refresh(db_appointment)
        return db_appointment
