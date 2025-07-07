from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, Dict
from datetime import date
import uuid

from models.adl_answers import ADLAnswers
from database import get_db

class ADLSubmission(BaseModel):
    patient_id: uuid.UUID
    date_completed: Optional[date] = Field(default_factory=date.today)
    feeding: Optional[int]
    bathing: Optional[int]
    grooming: Optional[int]
    dressing: Optional[int]
    bowels: Optional[int]
    bladder: Optional[int]
    toilet_use: Optional[int]
    transfers: Optional[int]
    mobility: Optional[int]
    stairs: Optional[int]
    answers: Dict[str, int]

router = APIRouter(prefix="/adl", tags=["adl"])

@router.get("/by_patient/{patient_id}")
def get_adl_by_patient(patient_id: str, db: Session = Depends(get_db)):
    from uuid import UUID
    try:
        uuid_obj = UUID(patient_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid patient_id format (must be UUID)")
    adl = db.query(ADLAnswers).filter(ADLAnswers.patient_id == uuid_obj).order_by(ADLAnswers.date_completed.desc()).first()
    if not adl:
        return None
    return {
        "adl_id": str(adl.adl_id),
        "patient_id": str(adl.patient_id),
        "date_completed": str(adl.date_completed),
        "feeding": adl.feeding,
        "bathing": adl.bathing,
        "grooming": adl.grooming,
        "dressing": adl.dressing,
        "bowels": adl.bowels,
        "bladder": adl.bladder,
        "toilet_use": adl.toilet_use,
        "transfers": adl.transfers,
        "mobility": adl.mobility,
        "stairs": adl.stairs,
        "answers": adl.answers
    }

@router.post("/submit")
def submit_adl(data: ADLSubmission, db: Session = Depends(get_db)):
    try:
        # Check if a record exists for this patient and date
        existing = db.query(ADLAnswers).filter(
            ADLAnswers.patient_id == data.patient_id,
            ADLAnswers.date_completed == data.date_completed
        ).first()
        was_update = False
        if existing:
            # Update existing record
            existing.feeding = data.feeding
            existing.bathing = data.bathing
            existing.grooming = data.grooming
            existing.dressing = data.dressing
            existing.bowels = data.bowels
            existing.bladder = data.bladder
            existing.toilet_use = data.toilet_use
            existing.transfers = data.transfers
            existing.mobility = data.mobility
            existing.stairs = data.stairs
            existing.answers = data.answers
            db.commit()
            db.refresh(existing)
            was_update = True
            adl_row = existing
        else:
            adl = ADLAnswers(
                patient_id=data.patient_id,
                date_completed=data.date_completed,
                feeding=data.feeding,
                bathing=data.bathing,
                grooming=data.grooming,
                dressing=data.dressing,
                bowels=data.bowels,
                bladder=data.bladder,
                toilet_use=data.toilet_use,
                transfers=data.transfers,
                mobility=data.mobility,
                stairs=data.stairs,
                answers=data.answers
            )
            db.add(adl)
            db.commit()
            db.refresh(adl)
            adl_row = adl

        return {"adl_id": str(adl_row.adl_id), "status": "created" if not was_update else "updated", "was_update": was_update}

    except Exception as e:
        db.rollback()
        print("Error in submit_adl:", e)
        raise HTTPException(status_code=500, detail=str(e))
