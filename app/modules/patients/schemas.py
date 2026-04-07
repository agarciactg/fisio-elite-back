from pydantic import BaseModel
from typing import Optional

class PatientBase(BaseModel):
    first_name: str
    last_name: str
    document_number: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None 

class PatientCreate(PatientBase):
    pass

class PatientResponse(PatientBase):
    id: int

    class Config:
        from_attributes = True
