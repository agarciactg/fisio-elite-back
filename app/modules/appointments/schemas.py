from pydantic import BaseModel

from typing import Optional
from datetime import datetime

from app.modules.patients.schemas import PatientResponse
from app.modules.therapists.schemas import TherapistResponse
from app.modules.patients.schemas import PatientBrief
from app.modules.therapists.schemas import TherapistBrief


class AppointmentBase(BaseModel):
    patient_id: int
    therapist_id: int
    start_time: datetime
    end_time: datetime
    status: str = "Confirmed"
    treatment: Optional[str] = None


class AppointmentCreate(AppointmentBase):
    pass


class AppointmentResponse(AppointmentBase):
    id: int
    patient: Optional[PatientResponse] = None
    therapist: Optional[TherapistResponse] = None

    class Config:
        from_attributes = True

 
class AppointmentCalendarItem(BaseModel):
    id: int
    start_time: datetime
    end_time: datetime
    status: str
    treatment: Optional[str] = None
    patient: PatientBrief
    therapist: TherapistBrief
 
    class Config:
        from_attributes = True