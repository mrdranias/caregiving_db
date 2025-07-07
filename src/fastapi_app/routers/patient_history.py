from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from uuid import UUID

from models.patient_history import PatientHistory
from database import get_db

router = APIRouter(prefix="/history", tags=["patient_history"])

@router.get("/by_patient/{patient_id}")
def get_history_by_patient(patient_id: str, db: Session = Depends(get_db)):
    from uuid import UUID
    try:
        uuid_obj = UUID(patient_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid patient_id format (must be UUID)")
    history = db.query(PatientHistory).filter(PatientHistory.patient_id == uuid_obj).order_by(PatientHistory.created_at.desc()).first()
    if not history:
        return None
    return {
        "history_id": str(history.history_id),
        "patient_id": str(history.patient_id),
        "dx_codes": history.dx_codes,
        "tx_codes": history.tx_codes,
        "rx_codes": history.rx_codes,
        "sx_codes": history.sx_codes,
        "notes": history.notes,
        "created_at": str(history.created_at) if hasattr(history, "created_at") else None
    }

from typing import List

class PatientHistoryCreate(BaseModel):
    patient_id: UUID
    dx_codes: Optional[List[str]]
    tx_codes: Optional[List[str]]
    rx_codes: Optional[List[str]]
    sx_codes: Optional[List[str]]
    notes: Optional[str]

@router.post("/submit")
def submit_history(history: PatientHistoryCreate, db: Session = Depends(get_db)):
    try:
        db_history = PatientHistory(
            patient_id=history.patient_id,
            dx_codes=history.dx_codes,
            tx_codes=history.tx_codes,
            rx_codes=history.rx_codes,
            sx_codes=history.sx_codes,
            notes=history.notes
        )
        db.add(db_history)
        db.commit()
        db.refresh(db_history)
        return {"history_id": str(db_history.history_id), "patient_id": str(db_history.patient_id), "status": "created"}
    except Exception as e:
        db.rollback()
        print("Error in submit_history:", e)
        raise HTTPException(status_code=500, detail=str(e))
