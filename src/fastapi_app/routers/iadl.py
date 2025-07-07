from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, Dict
from datetime import date
from uuid import UUID

from models.iadl_answers import IADLAnswers
from database import get_db

router = APIRouter(prefix="/iadl", tags=["iadl"])

@router.get("/by_patient/{patient_id}")
def get_iadl_by_patient(patient_id: str, db: Session = Depends(get_db)):
    from uuid import UUID
    try:
        uuid_obj = UUID(patient_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid patient_id format (must be UUID)")
    from models.iadl_answers import IADLAnswers
    iadl = db.query(IADLAnswers).filter(IADLAnswers.patient_id == uuid_obj).order_by(IADLAnswers.date_completed.desc()).first()
    if not iadl:
        return None
    return {
        "iadl_id": str(iadl.iadl_id),
        "patient_id": str(iadl.patient_id),
        "date_completed": str(iadl.date_completed),
        "telephone": iadl.telephone,
        "shopping": iadl.shopping,
        "food_preparation": iadl.food_preparation,
        "housekeeping": iadl.housekeeping,
        "laundry": iadl.laundry,
        "transportation": iadl.transportation,
        "medication": iadl.medication,
        "finances": iadl.finances,
        "answers": iadl.answers
    }

class IADLSubmission(BaseModel):
    patient_id: UUID
    date_completed: Optional[date]
    telephone: int
    shopping: int
    food_preparation: int
    housekeeping: int
    laundry: int
    transportation: int
    medication: int
    finances: int
    answers: Dict[str, int]

@router.post("/submit")
def submit_iadl(iadl: IADLSubmission, db: Session = Depends(get_db)):
    try:
        # Check if a record exists for this patient and date
        existing = db.query(IADLAnswers).filter(
            IADLAnswers.patient_id == iadl.patient_id,
            IADLAnswers.date_completed == iadl.date_completed
        ).first()
        was_update = False
        if existing:
            existing.telephone = iadl.telephone
            existing.shopping = iadl.shopping
            existing.food_preparation = iadl.food_preparation
            existing.housekeeping = iadl.housekeeping
            existing.laundry = iadl.laundry
            existing.transportation = iadl.transportation
            existing.medication = iadl.medication
            existing.finances = iadl.finances
            existing.answers = iadl.answers
            db.commit()
            db.refresh(existing)
            was_update = True
            iadl_row = existing
        else:
            db_iadl = IADLAnswers(
                patient_id=iadl.patient_id,
                date_completed=iadl.date_completed,
                telephone=iadl.telephone,
                shopping=iadl.shopping,
                food_preparation=iadl.food_preparation,
                housekeeping=iadl.housekeeping,
                laundry=iadl.laundry,
                transportation=iadl.transportation,
                medication=iadl.medication,
                finances=iadl.finances,
                answers=iadl.answers
            )
            db.add(db_iadl)
            db.commit()
            db.refresh(db_iadl)
            iadl_row = db_iadl

        return {"iadl_id": str(iadl_row.iadl_id), "patient_id": str(iadl_row.patient_id), "status": "created" if not was_update else "updated", "was_update": was_update}
    except Exception as e:
        db.rollback()
        print("Error in submit_iadl:", e)
        raise HTTPException(status_code=500, detail=str(e))
