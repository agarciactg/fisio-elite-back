from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func
from sqlalchemy.future import select
from app.modules.payments.models import Payment
from app.modules.appointments.models import Appointment
from app.modules.patients.models import Patient
from app.modules.therapists.models import Therapist
from .schemas import DashboardStatsResponse

class DashboardService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_dashboard_stats(self) -> dict:
        # Mocking aggregate logic specifically for the UI view
        
        # Total Revenue (sum of all PAID payments)
        revenue_sum = await self.db.execute(select(func.sum(Payment.amount)).where(Payment.status == "PAID"))
        revenue = revenue_sum.scalar() or 0.0

        # Appointments completed
        appts_completed = await self.db.execute(select(func.count(Appointment.id)).where(Appointment.status == "Confirmed"))
        completed = appts_completed.scalar() or 0

        # New Patients
        pat_count = await self.db.execute(select(func.count(Patient.id)))
        new_pats = pat_count.scalar() or 0

        return {
            "revenue": f"€{revenue:.2f}",
            "appointments_completed": completed,
            "new_patients": new_pats,
            "attendance_ratio": 94.8,
            "recent_activity": [], # Placeholder for joins
            "appointments_by_therapist": []
        }
