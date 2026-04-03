from pydantic import BaseModel
from typing import List

class TherapistStat(BaseModel):
    name: str
    appointments_count: int

class DashboardStatsResponse(BaseModel):
    revenue: str
    appointments_completed: int
    new_patients: int
    attendance_ratio: float
    recent_activity: list # Just loose dicts for now
    appointments_by_therapist: List[TherapistStat]
