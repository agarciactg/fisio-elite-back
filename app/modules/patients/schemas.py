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


class PatientUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    document_number: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None


class PatientResponse(PatientBase):
    id: int

    class Config:
        from_attributes = True


class PatientBrief(BaseModel):
    id: int
    first_name: str
    last_name: str
    document_number: Optional[str] = None
 
    class Config:
        from_attributes = True


class PatientDirectoryDetail(BaseModel):
    id: int
    first_name: str
    last_name: str
    document_number: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    avatar_url: Optional[str] = None
    last_visit_date: Optional[str] = None
    last_visit_reason: Optional[str] = None
    session_used: int = 0
    session_total: int = 0
    status: str  # "ACTIVE" | "PACKAGE PENDING" | "INACTIVE"
 
    class Config:
        from_attributes = True


class PatientDirectorySummary(BaseModel):
    total_patients: int
    total_patients_trend: str
    active_now: int
    package_pending: int
    sessions_today: int
    capacity_percentage: int


class PatientDirectoryResponse(BaseModel):
    summary: PatientDirectorySummary
    patients: list[PatientDirectoryDetail]
