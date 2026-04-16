from app.modules.patients.utils import _derive_status
from app.modules.constants import TIMEZONE
from zoneinfo import ZoneInfo
from app.modules.appointments.models import Appointment
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func, cast, Date
from sqlalchemy.orm import selectinload
 
from .models import Patient
from .schemas import PatientCreate, PatientDirectoryResponse, PatientDirectorySummary, PatientDirectoryDetail

from datetime import datetime, date, timedelta
from app.modules.auth.service import AuthService

 
# ── Logic of status ──────────────────────────────────────────────────────────
# ACTIVE         → has confirmed appointment in the last 30 days or future
# PACKAGE PENDING → your last appointment was more than 30 days ago (needs follow-up)
# INACTIVE       → no registered appointments or more than 60 days ago
class PatientService:
    def __init__(self, db: AsyncSession):
        self.db = db
 
    async def get_patients(self) -> list[Patient]:
        result = await self.db.execute(select(Patient))
        return result.scalars().all()

    async def get_patient_directory(self) -> PatientDirectoryResponse:
        today     = date.today()
        now = datetime.now(ZoneInfo(TIMEZONE))
        ago_30    = now - timedelta(days=30)
        ago_60    = now - timedelta(days=60)
 
        total_result = await self.db.execute(select(func.count(Patient.id)))
        total_patients = total_result.scalar() or 0
 
        first_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        new_this_month = await self.db.execute(
            select(func.count(Patient.id)).where(Patient.created_at >= first_of_month)
        )
        new_count = new_this_month.scalar() or 0
        trend = f"+{new_count} este mes" if new_count > 0 else "Sin nuevos este mes"
 
        sessions_today_result = await self.db.execute(
            select(func.count(Appointment.id))
            .where(cast(func.timezone(TIMEZONE, Appointment.start_time), Date) == today)
            .where(Appointment.status != "Canceled")
        )
        sessions_today = sessions_today_result.scalar() or 0
 
        patients_result = await self.db.execute(
            select(Patient).options(selectinload(Patient.appointments))
        )
        patients = patients_result.scalars().all()
 
        detail_list = []
        active_count  = 0
        pending_count = 0
 
        for p in patients:
            appts = [a for a in p.appointments if a.status != "Canceled"]
 
            past_appts = sorted(
                [a for a in appts if a.start_time <= now],
                key=lambda a: a.start_time,
                reverse=True,
            )
            last_appt = past_appts[0] if past_appts else None
 
            has_future = any(a.start_time > now for a in appts)
 
            sessions_used  = len([a for a in appts if a.start_time <= now])
            sessions_total = len(appts)
 
            patient_status = _derive_status(
                last_appt.start_time if last_appt else None,
                has_future,
            )
 
            if patient_status == "ACTIVE":
                active_count += 1
            elif patient_status == "PACKAGE PENDING":
                pending_count += 1
 
            detail_list.append(PatientDirectoryDetail(
                id=p.id,
                first_name=p.first_name,
                last_name=p.last_name,
                document_number=p.document_number,
                email=p.email,
                phone_number=p.phone_number,
                avatar_url=None,
                last_visit_date=(
                    last_appt.start_time.strftime("%b %d, %Y")
                    if last_appt else None
                ),
                last_visit_reason=(
                    last_appt.treatment if last_appt and last_appt.treatment else "—"
                ),
                session_used=sessions_used,
                session_total=sessions_total,
                status=patient_status,
            ))
 
        # Capacity: % of the day occupied with respect to the clinic schedule 
        # Clinic schedule: 8:00–20:00 = 12 hours. Assuming 1h slots per therapist.
        therapist_count_result = await self.db.execute(
            select(func.count()).select_from(
                select(Appointment.therapist_id)
                .where(cast(func.timezone(TIMEZONE, Appointment.start_time), Date) == today)
                .where(Appointment.status != "Canceled")
                .distinct()
                .subquery()
            )
        )
        active_therapists = therapist_count_result.scalar() or 1
        max_slots = active_therapists * 12  # 12 slots de 1h por terapeuta
        capacity  = round((sessions_today / max_slots) * 100) if max_slots > 0 else 0
        capacity  = min(capacity, 100)
 
        summary = PatientDirectorySummary(
            total_patients=total_patients,
            total_patients_trend=trend,
            active_now=active_count,
            package_pending=pending_count,
            sessions_today=sessions_today,
            capacity_percentage=capacity,
        )
 
        return PatientDirectoryResponse(summary=summary, patients=detail_list)
 
    async def create_patient(self, patient: PatientCreate) -> Patient:
        # Validate duplicate email in patients
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
 
            temp_password = None
            if patient.email:
                _, temp_password = await AuthService._create_user_if_not_exists(self.db, patient.email)
            await self.db.commit()
            await self.db.refresh(db_patient)
 
            if temp_password:
                print(
                    f"[INFO] Usuario creado para paciente '{patient.email}'. "
                    f"Contraseña temporal: {temp_password}"
                )
 
            return db_patient
 
        except IntegrityError:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Error de integridad al crear el paciente. El correo ya puede estar en uso.",
            )
