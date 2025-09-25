from __future__ import annotations

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .config import get_settings
from .database import get_db
from .models import Patient
from .schemas import PatientCreate, PatientRead
from .crypto import encrypt_value
from .middleware import AuditMiddleware
from .security import require_role


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="Medical History API", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_middleware(AuditMiddleware)

    @app.get("/healthz")
    def healthz():
        return {"status": "ok"}

    @app.post("/patients", response_model=PatientRead, dependencies=[Depends(require_role("provider"))])
    def create_patient(payload: PatientCreate, db: Session = Depends(get_db)):
        if db.query(Patient).filter_by(mrn=payload.mrn).first():
            raise HTTPException(status_code=400, detail="MRN already exists")
        payload_dict = payload.dict()
        ssn = payload_dict.pop("ssn", None)
        patient = Patient(**payload_dict)
        if ssn:
            patient.ssn_encrypted = encrypt_value(ssn)
        db.add(patient)
        db.commit()
        db.refresh(patient)
        return patient

    @app.get("/patients/{patient_id}", response_model=PatientRead, dependencies=[Depends(require_role("provider"))])
    def get_patient(patient_id: int, db: Session = Depends(get_db)):
        patient = db.get(Patient, patient_id)
        if not patient:
            raise HTTPException(status_code=404, detail="Not found")
        return patient

    return app


app = create_app()

