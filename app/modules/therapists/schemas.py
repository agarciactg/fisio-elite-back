from typing import Literal
from pydantic import BaseModel, EmailStr
from typing import Optional

TherapistStatus = Literal["Disponible", "En sesión", "Fuera"]


class TherapistBase(BaseModel):
    first_name: str
    last_name: str
    specialty: str
    document_number: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = True

class TherapistCreate(TherapistBase):
    pass

class TherapistResponse(TherapistBase):
    id: int

    class Config:
        from_attributes = True


class TherapistBrief(BaseModel):
    id: int
    first_name: str
    last_name: str
    specialty: str
 
    class Config:
        from_attributes = True


class TherapistCreate(BaseModel):
    first_name: str
    last_name: str
    specialty: str
    email: Optional[str] = None
    document_number: Optional[str] = None
 
 
class TherapistResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    specialty: str
    email: Optional[str] = None
    is_active: bool
 
    class Config:
        from_attributes = True

 
class TherapistDirectoryItem(BaseModel):
    id: int
    first_name: str
    last_name: str
    specialty: str
    email: Optional[str] = None
    is_active: bool
    status: TherapistStatus          
    workload_hours: float            
    workload_capacity: float         
    appointments_today: int          
    total_appointments: int          
 
    class Config:
        from_attributes = True
 
 
class TeamPerformanceSummary(BaseModel):
    total_consultations: int         
    avg_rating: float                
    retention_percentage: int        
 
 
class TherapistDirectoryResponse(BaseModel):
    therapists: list[TherapistDirectoryItem]
    performance: TeamPerformanceSummary
 