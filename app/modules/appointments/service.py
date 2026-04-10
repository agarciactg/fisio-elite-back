from app.modules.appointments.schemas import AppointmentUpdate
from datetime import date, datetime, timedelta
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError
 
from .models import Appointment
from .schemas import AppointmentCreate
from app.modules.patients.models import Patient
from app.modules.therapists.models import Therapist
 
 
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

    async def get_by_day(
        self,
        target_date: date,
        therapist_id: int | None = None,
    ) -> list[Appointment]:
        """
        Date appointments.
        GET /api/v1/appointments/by-day?date=2026-04-08&therapist_id=1
        """
        day_start = datetime.combine(target_date, datetime.min.time())
        day_end   = datetime.combine(target_date, datetime.max.time())
 
        stmt = (
            select(Appointment)
            .options(
                selectinload(Appointment.patient),
                selectinload(Appointment.therapist),
            )
            .where(Appointment.start_time >= day_start)
            .where(Appointment.start_time <= day_end)
        )
 
        if therapist_id:
            stmt = stmt.where(Appointment.therapist_id == therapist_id)
 
        stmt = stmt.order_by(Appointment.start_time)
        result = await self.db.execute(stmt)
        return result.scalars().all()
 
    async def get_by_week(
        self,
        target_date: date,
        therapist_id: int | None = None,
    ) -> list[Appointment]:
        """
        Appointments for a week (Monday–Sunday) containing the given date.
        GET /api/v1/appointments/by-week?date=2026-04-08&therapist_id=1
        """
        monday    = target_date - timedelta(days=target_date.weekday())
        sunday    = monday + timedelta(days=6)
        week_start = datetime.combine(monday, datetime.min.time())
        week_end   = datetime.combine(sunday, datetime.max.time())
 
        stmt = (
            select(Appointment)
            .options(
                selectinload(Appointment.patient),
                selectinload(Appointment.therapist),
            )
            .where(Appointment.start_time >= week_start)
            .where(Appointment.start_time <= week_end)
        )
 
        if therapist_id:
            stmt = stmt.where(Appointment.therapist_id == therapist_id)
 
        stmt = stmt.order_by(Appointment.start_time)
        result = await self.db.execute(stmt)
        return result.scalars().all()
 
    async def get_by_month(
        self,
        year: int,
        month: int,
        therapist_id: int | None = None,
    ) -> list[Appointment]:
        """
        Appointments for a full month.
        GET /api/v1/appointments/by-month?year=2026&month=4&therapist_id=1
        """
        month_start = datetime(year, month, 1)
        if month == 12:
            month_end = datetime(year + 1, 1, 1) - timedelta(seconds=1)
        else:
            month_end = datetime(year, month + 1, 1) - timedelta(seconds=1)
 
        stmt = (
            select(Appointment)
            .options(
                selectinload(Appointment.patient),
                selectinload(Appointment.therapist),
            )
            .where(Appointment.start_time >= month_start)
            .where(Appointment.start_time <= month_end)
        )
 
        if therapist_id:
            stmt = stmt.where(Appointment.therapist_id == therapist_id)
 
        stmt = stmt.order_by(Appointment.start_time)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def update_appointment(self, appointment_id: int, obj_in: AppointmentUpdate) -> Appointment:
        result = await self.db.execute(
            select(Appointment).where(Appointment.id == appointment_id)
        )
        db_obj = result.scalar_one_or_none()
        
        if not db_obj:
            raise HTTPException(status_code=404, detail="Cita no encontrada")

        update_data = obj_in.model_dump(exclude_unset=True)
        
        for field in update_data:
            setattr(db_obj, field, update_data[field])

        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def cancel_appointment(self, appointment_id: int) -> Appointment:
        result = await self.db.execute(
            select(Appointment)
            .options(
                selectinload(Appointment.patient),
                selectinload(Appointment.therapist)
            )
            .where(Appointment.id == appointment_id)
        )
        db_obj = result.scalar_one_or_none()

        if not db_obj:
            raise HTTPException(status_code=404, detail="Cita no encontrada")

        db_obj.status = "Canceled"
        
        await self.db.commit()
        
        await self.db.refresh(db_obj)
        
        return db_obj
