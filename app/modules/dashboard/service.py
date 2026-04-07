from datetime import date, datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, cast, Date
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.modules.payments.models import Payment
from app.modules.appointments.models import Appointment
from app.modules.patients.models import Patient
from app.modules.therapists.models import Therapist
from .schemas import DashboardStatsResponse


def _format_cop(value: float) -> str:
    """Formatea en pesos colombianos. Ej: 1250000 → '$1.250.000'"""
    return f"${int(value):,}".replace(",", ".")

def _full_name(first: str, last: str) -> str:
    return f"{first} {last}".strip()

def _initials(first: str, last: str) -> str:
    return f"{first[0].upper()}{last[0].upper()}" if first and last else "??"

def _trend(current: float, previous: float) -> float:
    if previous == 0:
        return 0.0
    return round(((current - previous) / previous) * 100, 1)

def _start_of_month(d: date) -> datetime:
    return datetime(d.year, d.month, 1)

def _end_of_prev_month(d: date) -> datetime:
    first = d.replace(day=1)
    last_day = first - timedelta(days=1)
    return datetime(last_day.year, last_day.month, last_day.day, 23, 59, 59)

def _start_of_prev_month(d: date) -> datetime:
    first_this = d.replace(day=1)
    last_prev = first_this - timedelta(days=1)
    return datetime(last_prev.year, last_prev.month, 1)


class DashboardService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_dashboard_stats(self) -> dict:
        today = date.today()
        now = datetime.now()

        first_this = _start_of_month(today)
        first_prev = _start_of_prev_month(today)
        last_prev  = _end_of_prev_month(today)

        rev_cur = await self.db.execute(
            select(func.sum(Payment.amount))
            .where(Payment.status == "PAID")
            .where(Payment.created_at >= first_this)
        )
        revenue_current = float(rev_cur.scalar() or 0)

        rev_prev = await self.db.execute(
            select(func.sum(Payment.amount))
            .where(Payment.status == "PAID")
            .where(Payment.created_at >= first_prev)
            .where(Payment.created_at <= last_prev)
        )
        revenue_previous = float(rev_prev.scalar() or 0)

        appt_cur = await self.db.execute(
            select(func.count(Appointment.id))
            .where(Appointment.status == "Confirmed")
            .where(Appointment.start_time >= first_this)
        )
        appts_current = appt_cur.scalar() or 0

        appt_prev = await self.db.execute(
            select(func.count(Appointment.id))
            .where(Appointment.status == "Confirmed")
            .where(Appointment.start_time >= first_prev)
            .where(Appointment.start_time <= last_prev)
        )
        appts_previous = appt_prev.scalar() or 0

        # ── Nuevos pacientes ──────────────────────────────────────────────
        pat_cur = await self.db.execute(
            select(func.count(Patient.id))
            .where(Patient.created_at >= first_this)
        )
        patients_current = pat_cur.scalar() or 0

        pat_prev = await self.db.execute(
            select(func.count(Patient.id))
            .where(Patient.created_at >= first_prev)
            .where(Patient.created_at <= last_prev)
        )
        patients_previous = pat_prev.scalar() or 0

        return {
            "revenue":              _format_cop(revenue_current),
            "revenue_trend":        _trend(revenue_current, revenue_previous),
            "appointments_completed": appts_current,
            "appointments_trend":   _trend(appts_current, appts_previous),
            "new_patients":         patients_current,
            "new_patients_trend":   _trend(patients_current, patients_previous),
            "attendance_ratio":     94.8,
            "attendance_trend":     0.8,
            "weekly_appointments":  await _weekly_appointments(self.db),
            "recent_activity":      await _recent_activity(self.db),
            "upcoming_today":       await _upcoming_today(self.db, now),
            "appointments_by_therapist": await _appointments_by_therapist(self.db, first_this),
        }


async def _weekly_appointments(db: AsyncSession) -> list:
    """Últimas 5 semanas: citas actuales vs mismas semanas del período anterior."""
    today = date.today()
    weeks = []
    for i in range(4, -1, -1):
        w_end   = datetime.combine(today - timedelta(weeks=i), datetime.max.time())
        w_start = datetime.combine(today - timedelta(weeks=i, days=6), datetime.min.time())
        p_end   = datetime.combine(today - timedelta(weeks=i + 4), datetime.max.time())
        p_start = datetime.combine(today - timedelta(weeks=i + 4, days=6), datetime.min.time())

        cur = await db.execute(
            select(func.count(Appointment.id))
            .where(Appointment.start_time >= w_start)
            .where(Appointment.start_time <= w_end)
        )
        prev = await db.execute(
            select(func.count(Appointment.id))
            .where(Appointment.start_time >= p_start)
            .where(Appointment.start_time <= p_end)
        )
        weeks.append({
            "week":     f"Sem {5 - i}",
            "current":  cur.scalar() or 0,
            "previous": prev.scalar() or 0,
        })
    return weeks


async def _recent_activity(db: AsyncSession) -> list:
    """Últimas 10 citas con paciente, terapeuta y pago."""
    result = await db.execute(
        select(Appointment)
        .options(
            selectinload(Appointment.patient),
            selectinload(Appointment.therapist),
            selectinload(Appointment.payment),
        )
        .order_by(Appointment.start_time.desc())
        .limit(10)
    )
    appointments = result.scalars().all()

    rows = []
    for appt in appointments:
        p = appt.patient
        t = appt.therapist
        pay = appt.payment

        patient_name   = _full_name(p.first_name, p.last_name) if p else "—"
        therapist_name = _full_name(t.first_name, t.last_name) if t else "—"
        amount  = _format_cop(float(pay.amount)) if pay else "$0"
        status  = pay.status.lower() if pay else "pending"   

        rows.append({
            "patient_name":     patient_name,
            "patient_initials": _initials(p.first_name, p.last_name) if p else "??",
            "therapist":        therapist_name,
            "treatment":        appt.treatment or "—",
            "status":           status,
            "amount":           amount,
        })
    return rows


async def _upcoming_today(db: AsyncSession, now: datetime) -> list:
    """Citas de hoy que aún no han pasado, ordenadas por start_time."""
    today_start = datetime.combine(now.date(), datetime.min.time())
    today_end   = datetime.combine(now.date(), datetime.max.time())

    result = await db.execute(
        select(Appointment)
        .options(
            selectinload(Appointment.patient),
            selectinload(Appointment.therapist),
        )
        .where(Appointment.start_time >= now)          
        .where(Appointment.start_time <= today_end)
        .where(Appointment.status != "Canceled")
        .order_by(Appointment.start_time)
    )
    appointments = result.scalars().all()

    return [
        {
            "id":           appt.id,
            "time":         appt.start_time.strftime("%H:%M"),
            "patient_name": _full_name(appt.patient.first_name, appt.patient.last_name) if appt.patient else "—",
            "patient_id":   appt.patient.id if appt.patient else None,
            "patient_phone": appt.patient.phone_number if appt.patient else "—",
            "therapist":    _full_name(appt.therapist.first_name, appt.therapist.last_name) if appt.therapist else "—",
            "treatment":    appt.treatment or "—",
            "status":       appt.status,
        }
        for appt in appointments
    ]


async def _appointments_by_therapist(db: AsyncSession, since: datetime) -> list:
    """Citas por terapeuta desde 'since', con porcentaje relativo al máximo."""
    result = await db.execute(
        select(
            Therapist.first_name,
            Therapist.last_name,
            func.count(Appointment.id).label("count"),
        )
        .join(Appointment, Appointment.therapist_id == Therapist.id)
        .where(Appointment.start_time >= since)
        .group_by(Therapist.id, Therapist.first_name, Therapist.last_name)
        .order_by(func.count(Appointment.id).desc())
    )
    rows = result.all()

    if not rows:
        return []

    max_count = rows[0].count or 1
    return [
        {
            "name":    _full_name(row.first_name, row.last_name),
            "count":   row.count,
            "percent": round((row.count / max_count) * 100),
        }
        for row in rows
    ]
