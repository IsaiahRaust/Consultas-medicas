from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr, field_validator

class PatientIn(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr | None = None

class PatientOut(BaseModel):
    id: int
    name: str
    email: EmailStr | None
    class Config:
        from_attributes = True

class DoctorIn(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    specialty: str | None = Field(default=None, max_length=120)

class DoctorOut(BaseModel):
    id: int
    name: str
    specialty: str | None
    class Config:
        from_attributes = True

class AppointmentIn(BaseModel):
    patient_id: int
    doctor_id: int
    start_at: datetime
    duration_min: int = Field(ge=10, le=180, default=30)
    reason: str | None = Field(default=None, max_length=250)

class AppointmentOut(BaseModel):
    id: int
    patient_id: int
    doctor_id: int
    start_at: datetime
    duration_min: int
    reason: str | None
    class Config:
        from_attributes = True