from pydantic import BaseModel, EmailStr
from typing import Optional

class TherapistBase(BaseModel):
    first_name: str
    last_name: str
    specialty: str
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = True

class TherapistCreate(TherapistBase):
    pass

class TherapistResponse(TherapistBase):
    id: int

    class Config:
        from_attributes = True
