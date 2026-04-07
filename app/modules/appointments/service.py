from fastapi import HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError

from app.modules.therapists.models import Therapist
from app.modules.patients.models import Patient

from .models import Appointment
from .schemas import AppointmentCreate


class AppointmentService:
    def __init__(self, db: AsyncSession):
        self.db = db
 
    async def get_appointments(self) -> list[Appointment]:
        stmt = select(Appointment).options(
            selectinload(Appointment.patient),
            selectinload(Appointment.therapist),
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()
 
    async def create_appointment(self, appointment: AppointmentCreate) -> Appointment:
        patient = await self.db.get(Patient, appointment.patient_id)
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Paciente con id {appointment.patient_id} no encontrado.",
            )
 
        therapist = await self.db.get(Therapist, appointment.therapist_id)
        if not therapist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Terapeuta con id {appointment.therapist_id} no encontrado.",
            )
        if not therapist.is_active:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"El terapeuta '{therapist.first_name} {therapist.last_name}' no está activo.",
            )
 
        if appointment.end_time <= appointment.start_time:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="La hora de fin debe ser posterior a la hora de inicio.",
            )
 
        overlap = await self.db.execute(
            select(Appointment).where(
                Appointment.therapist_id == appointment.therapist_id,
                Appointment.status != "Canceled",
                Appointment.start_time < appointment.end_time,
                Appointment.end_time > appointment.start_time,
            )
        )
        if overlap.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El terapeuta ya tiene una cita en ese horario.",
            )
 
        try:
            db_appointment = Appointment(**appointment.model_dump())
            self.db.add(db_appointment)
            await self.db.commit()
 
            stmt = select(Appointment).options(
                selectinload(Appointment.patient),
                selectinload(Appointment.therapist),
            ).where(Appointment.id == db_appointment.id)
 
            result = await self.db.execute(stmt)
            return result.scalar_one()
 
        except IntegrityError:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Error de integridad al crear la cita. Verifica los datos enviados.",
            )
