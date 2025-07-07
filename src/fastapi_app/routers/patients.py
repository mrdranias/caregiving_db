from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from datetime import date
from typing import Optional, Dict
import uuid
from uuid import UUID

from models.patients import Patients
from database import get_db

class PatientCreate(BaseModel):
    name: str
    dob: Optional[date]
    gender: Optional[str]
    phone: Optional[str]
    email: Optional[str]

router = APIRouter(prefix="/patients", tags=["patients"])

@router.post("/create")
def create_patient(patient: PatientCreate, db: Session = Depends(get_db)):
    try:
        # FHIR-style: search for existing patient by name and dob
        query = db.query(Patients).filter(Patients.name == patient.name)
        if patient.dob:
            query = query.filter(Patients.dob == patient.dob)
        existing = query.first()
        if existing:
            return {"patient_id": str(existing.patient_id), "status": "exists"}
        db_patient = Patients(
            name=patient.name,
            dob=patient.dob,
            gender=patient.gender,
            phone=patient.phone,
            email=patient.email
        )
        db.add(db_patient)
        db.commit()
        db.refresh(db_patient)
        return {"patient_id": str(db_patient.patient_id), "status": "created"}
    except Exception as e:
        db.rollback()
        print("Error in create_patient:", e)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/all")
def list_patients(db: Session = Depends(get_db)):
    patients = db.query(Patients).all()
    return [
        {"patient_id": str(p.patient_id), "name": p.name}
        for p in patients
    ]

@router.get("/{patient_id}")
def get_patient(patient_id: UUID, db: Session = Depends(get_db)):
    patient = db.query(Patients).filter(Patients.patient_id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return {
        "patient_id": str(patient.patient_id),
        "name": patient.name,
        "dob": str(patient.dob) if patient.dob else None,
        "gender": patient.gender,
        "phone": patient.phone,
        "email": patient.email
    }
