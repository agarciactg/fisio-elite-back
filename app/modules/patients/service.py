from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
 
from .models import Patient
from .schemas import PatientCreate
 
 
class PatientService:
    def __init__(self, db: AsyncSession):
        self.db = db
 
    async def get_patients(self) -> list[Patient]:
        result = await self.db.execute(select(Patient))
        return result.scalars().all()
 
    async def create_patient(self, patient: PatientCreate) -> Patient:
        if patient.email:
            existing = await self.db.execute(
                select(Patient).filter(Patient.email == patient.email)
            )
            if existing.scalars().first():
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Ya existe un paciente registrado con el correo '{patient.email}'.",
                )
 
        try:
            db_patient = Patient(**patient.model_dump())
            self.db.add(db_patient)
            await self.db.commit()
            await self.db.refresh(db_patient)
            return db_patient
 
        except IntegrityError:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Error de integridad al crear el paciente. El correo ya puede estar en uso.",
            )
