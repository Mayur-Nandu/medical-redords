from __future__ import annotations

from datetime import date, datetime
from pydantic import BaseModel, EmailStr


class PatientCreate(BaseModel):
    mrn: str
    first_name: str
    last_name: str
    date_of_birth: date | None = None
    sex: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    ssn: str | None = None
    address_line1: str | None = None
    address_line2: str | None = None
    city: str | None = None
    state: str | None = None
    postal_code: str | None = None
    country: str | None = None


class PatientRead(BaseModel):
    id: int
    mrn: str
    first_name: str
    last_name: str
    date_of_birth: date | None
    sex: str | None
    email: EmailStr | None
    phone: str | None
    # SSN intentionally not exposed in read model
    address_line1: str | None
    address_line2: str | None
    city: str | None
    state: str | None
    postal_code: str | None
    country: str | None
    created_at: datetime
    updated_at: datetime | None

    class Config:
        from_attributes = True

