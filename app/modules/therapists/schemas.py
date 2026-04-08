from pydantic import BaseModel, EmailStr
from typing import Optional

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
