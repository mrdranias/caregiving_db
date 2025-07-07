from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from uuid import UUID

from models.adl_answers import ADLAnswers
from models.iadl_answers import IADLAnswers
from models.patient_history import PatientHistory
from database import get_db

router = APIRouter(prefix="/hazards", tags=["hazards"])

@router.get("/by_patient/{patient_id}")
def get_hazards_by_patient(patient_id: str, db: Session = Depends(get_db)):
    """
    Returns a list of hazards (child or parent) for a patient, derived from ADL, IADL, and patient history codes.
    """
    from uuid import UUID as UUID_type
    try:
        uuid_obj = UUID_type(patient_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid patient_id format (must be UUID)")

    hazards = []
    # --- ADL ---
    adl = db.query(ADLAnswers).filter(ADLAnswers.patient_id == uuid_obj).order_by(ADLAnswers.date_completed.desc()).first()
    if adl:
        from sqlalchemy import text
        adl_map = db.execute(text("SELECT adl_item, score_min, score_max, hazard_subclass_id, hazard_class_id FROM adl_item_hazard_map")).fetchall()
        adl_fields = [
            ("feeding", adl.feeding), ("bathing", adl.bathing), ("grooming", adl.grooming), ("dressing", adl.dressing),
            ("toilet_use", adl.toilet_use), ("transfers", adl.transfers)
        ]
        for item, score in adl_fields:
            if score is None:
                continue
            for row in adl_map:
                if row[0] == item and row[1] <= score <= row[2]:
                    if row[3]:
                        hazards.append({"type": "adl", "item": item, "score": score, "hazard_subclass_id": row[3]})
                    elif row[4]:
                        hazards.append({"type": "adl", "item": item, "score": score, "hazard_class_id": row[4]})

    # --- IADL ---
    iadl = db.query(IADLAnswers).filter(IADLAnswers.patient_id == uuid_obj).order_by(IADLAnswers.date_completed.desc()).first()
    if iadl:
        iadl_map = db.execute(text("SELECT iadl_item, score_min, score_max, hazard_subclass_id, hazard_class_id FROM iadl_item_hazard_map")).fetchall()
        iadl_fields = [
            ("shopping", iadl.shopping), ("food_preparation", iadl.food_preparation), ("housekeeping", iadl.housekeeping),
            ("transportation", iadl.transportation), ("medication", iadl.medication), ("finances", iadl.finances)
        ]
        for item, score in iadl_fields:
            if score is None:
                continue
            for row in iadl_map:
                if row[0] == item and row[1] <= score <= row[2]:
                    if row[3]:
                        hazards.append({"type": "iadl", "item": item, "score": score, "hazard_subclass_id": row[3]})
                    elif row[4]:
                        hazards.append({"type": "iadl", "item": item, "score": score, "hazard_class_id": row[4]})

    # --- Patient History (Dx, Sx, Rx) ---
    history = db.query(PatientHistory).filter(PatientHistory.patient_id == uuid_obj).order_by(PatientHistory.created_at.desc()).first()
    if history:
        # Sx
        if history.sx_codes:
            sx_map = db.execute(text("SELECT sx_code, hazard_subclass_id, hazard_class_id FROM sx_code_hazard_map")).fetchall()
            for code in history.sx_codes:
                for row in sx_map:
                    if row[0] == code:
                        if row[1]:
                            hazards.append({"type": "sx", "code": code, "hazard_subclass_id": row[1]})
                        elif row[2]:
                            hazards.append({"type": "sx", "code": code, "hazard_class_id": row[2]})
        # Dx
        if history.dx_codes:
            dx_map = db.execute(text("SELECT dx_code, hazard_subclass_id, hazard_class_id FROM dx_code_hazard_map")).fetchall()
            for code in history.dx_codes:
                for row in dx_map:
                    if row[0] == code:
                        if row[1]:
                            hazards.append({"type": "dx", "code": code, "hazard_subclass_id": row[1]})
                        elif row[2]:
                            hazards.append({"type": "dx", "code": code, "hazard_class_id": row[2]})
        # Rx
        if history.rx_codes:
            rx_map = db.execute(text("SELECT rx_code, hazard_subclass_id, hazard_class_id FROM rx_code_hazard_map")).fetchall()
            for code in history.rx_codes:
                for row in rx_map:
                    if row[0] == code:
                        if row[1]:
                            hazards.append({"type": "rx", "code": code, "hazard_subclass_id": row[1]})
                        elif row[2]:
                            hazards.append({"type": "rx", "code": code, "hazard_class_id": row[2]})

    return {"patient_id": patient_id, "hazards": hazards}
