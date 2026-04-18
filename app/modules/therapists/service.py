import secrets

from datetime import date, datetime, timedelta

from app.modules.therapists.schemas import TherapistDirectoryResponse
from app.modules.therapists.schemas import TeamPerformanceSummary
from app.modules.appointments.models import Appointment
from app.modules.therapists.schemas import TherapistDirectoryItem
from app.modules.patients.utils import _derive_status
from app.modules.therapists.schemas import TherapistStatus
from app.modules.auth.models import User
from app.modules.auth.service import AuthService
from .models import Therapist
from .schemas import TherapistCreate

from sqlalchemy import func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
 
from passlib.context import CryptContext
from fastapi import HTTPException, status as http_status


WEEKLY_CAPACITY_H  = 40.0
SESSION_DURATION_H = 1.0
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

 
class TherapistService:
    def __init__(self, db: AsyncSession):
        self.db = db
 
    async def get_therapists(self) -> list[Therapist]:
        result = await self.db.execute(
            select(Therapist).filter(Therapist.is_active == True)
        )
        return result.scalars().all()
 
    async def create_therapist(self, therapist: TherapistCreate) -> Therapist:
        if therapist.email:
            existing = await self.db.execute(
                select(Therapist).filter(Therapist.email == therapist.email)
            )
            if existing.scalars().first():
                raise HTTPException(
                    status_code=http_status.HTTP_409_CONFLICT,
                    detail=f"Ya existe un terapeuta registrado con el correo '{therapist.email}'.",
                )
 
        try:
            db_therapist = Therapist(**therapist.model_dump())
            self.db.add(db_therapist)
 
            temp_password = None
            if therapist.email:
                _, temp_password = await AuthService._create_user_if_not_exists(self.db, therapist.email)
            await self.db.commit()
            await self.db.refresh(db_therapist)
 
            if temp_password:
                print(
                    f"[INFO] Usuario creado para terapeuta '{therapist.email}'. "
                    f"Contraseña temporal: {temp_password}"
                )
 
            return db_therapist
 
        except IntegrityError:
            await self.db.rollback()
            raise HTTPException(
                status_code=http_status.HTTP_409_CONFLICT,
                detail="Error de integridad al crear el terapeuta. El correo ya puede estar en uso.",
            )


    async def get_therapists(self) -> list[Therapist]:
        result = await self.db.execute(
            select(Therapist).filter(Therapist.is_active == True)
        )
        return result.scalars().all()
 
    async def create_therapist(self, therapist: TherapistCreate) -> Therapist:
        if therapist.email:
            existing = await self.db.execute(
                select(Therapist).filter(Therapist.email == therapist.email)
            )
            if existing.scalars().first():
                raise HTTPException(
                    status_code=http_status.HTTP_409_CONFLICT,
                    detail=f"Ya existe un terapeuta con el correo '{therapist.email}'.",
                )
 
        try:
            db_therapist = Therapist(**therapist.model_dump())
            self.db.add(db_therapist)
 
            if therapist.email:
                existing_user = await self.db.execute(
                    select(User).filter(User.email == therapist.email)
                )
                if not existing_user.scalars().first():
                    temp_pwd = secrets.token_urlsafe(12)
                    self.db.add(User(
                        email=therapist.email,
                        hashed_password=pwd_context.hash(temp_pwd),
                        document_number=getattr(therapist, 'document_number', None),
                        is_active=True,
                    ))
                    print(f"[INFO] User creado para terapeuta '{therapist.email}'. Contraseña temporal: {temp_pwd}")
 
            await self.db.commit()
            await self.db.refresh(db_therapist)
            return db_therapist
 
        except IntegrityError:
            await self.db.rollback()
            raise HTTPException(
                status_code=http_status.HTTP_409_CONFLICT,
                detail="Error de integridad al crear el terapeuta.",
            )
 
    async def get_therapist_directory(self) -> dict:
        now   = datetime.now()
        today = date.today()
 
        monday = today - timedelta(days=today.weekday())
        sunday = monday + timedelta(days=6)
 
        first_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
 
        therapists_result = await self.db.execute(
            select(Therapist).options(selectinload(Therapist.appointments))
        )
        therapists = therapists_result.scalars().all()
 
        items = []
        for t in therapists:
            appts = t.appointments
 
            appts_today = [
                a for a in appts
                if a.start_time.date() == today and a.status != "Canceled"
            ]
 
            appts_week = [
                a for a in appts
                if monday <= a.start_time.date() <= sunday and a.status != "Canceled"
            ]
 
            workload_hours = len(appts_week) * SESSION_DURATION_H
 
            if not t.is_active:
                therapist_status: TherapistStatus = "Fuera"
            else:
                therapist_status = _derive_status(now, appts_today)
 
            items.append(TherapistDirectoryItem(
                id=t.id,
                first_name=t.first_name,
                last_name=t.last_name,
                specialty=t.specialty,
                email=t.email,
                is_active=t.is_active,
                status=therapist_status,
                workload_hours=workload_hours,
                workload_capacity=WEEKLY_CAPACITY_H,
                appointments_today=len(appts_today),
                total_appointments=len(appts),
            ))
 
        consult_result = await self.db.execute(
            select(func.count(Appointment.id))
            .where(Appointment.start_time >= first_of_month)
            .where(Appointment.status == "Confirmed")
        )
        total_consultations = consult_result.scalar() or 0
 
        patients_with_appts = await self.db.execute(
            select(Appointment.patient_id, func.count(Appointment.id).label("cnt"))
            .where(Appointment.status != "Canceled")
            .group_by(Appointment.patient_id)
        )
        rows = patients_with_appts.all()
        total_with_appts   = len(rows)
        returning_patients = sum(1 for r in rows if r.cnt > 1)
        retention = round((returning_patients / total_with_appts) * 100) if total_with_appts else 0
 
        performance = TeamPerformanceSummary(
            total_consultations=total_consultations,
            avg_rating=0.0,
            retention_percentage=retention,
        )
 
        return TherapistDirectoryResponse(therapists=items, performance=performance)
