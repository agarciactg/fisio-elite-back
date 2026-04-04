from pydantic import BaseModel
from typing import List

class RecentActivityItem(BaseModel):
    patient_name: str
    patient_initials: str
    therapist: str
    treatment: str
    status: str        
    amount: str        

class WeeklyAppointments(BaseModel):
    week: str          
    current: int       
    previous: int      

class UpcomingAppointment(BaseModel):
    time: str          
    patient_name: str
    therapist: str

class TherapistStat(BaseModel):
    name: str
    count: int
    percent: int       

class DashboardStatsResponse(BaseModel):
    revenue: str               
    revenue_trend: float       
    appointments_completed: int
    appointments_trend: float
    new_patients: int
    new_patients_trend: float
    attendance_ratio: float    
    attendance_trend: float

    weekly_appointments: List[WeeklyAppointments]
    recent_activity: List[RecentActivityItem]
    upcoming_today: List[UpcomingAppointment]
    appointments_by_therapist: List[TherapistStat]