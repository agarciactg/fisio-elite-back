from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .models import Patient
from .schemas import PatientCreate

class PatientService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_patients(self):
        result = await self.db.execute(select(Patient))
        return result.scalars().all()

    async def create_patient(self, patient: PatientCreate) -> Patient:
        db_patient = Patient(**patient.model_dump())
        self.db.add(db_patient)
        await self.db.commit()
        await self.db.refresh(db_patient)
        return db_patient
