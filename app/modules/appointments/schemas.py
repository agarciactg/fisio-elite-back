from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.modules.patients.schemas import PatientResponse
from app.modules.therapists.schemas import TherapistResponse

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
    
    # Nested relationships for comprehensive frontend loading
    patient: Optional[PatientResponse] = None
    therapist: Optional[TherapistResponse] = None

    class Config:
        from_attributes = True
