from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from uuid import UUID

from models.risk import Risk
from models.hazards import Hazard
from database import get_db
from pydantic import BaseModel

router = APIRouter(prefix="/risk", tags=["risk"])



class RiskCreateRequest(BaseModel):
    patient_id: UUID
    hazard_id: UUID
    severity: Optional[float] = None
    likelihood: Optional[int] = None
    risk_score: Optional[float] = None
    notes: Optional[str] = None

@router.post("/create")
def create_risk(risk: RiskCreateRequest, db: Session = Depends(get_db)):
    try:
        db_risk = Risk(
            patient_id=risk.patient_id,
            hazard_id=risk.hazard_id,
            severity=risk.severity,
            likelihood=risk.likelihood,
            risk_score=risk.risk_score,
            notes=risk.notes
        )
        db.add(db_risk)
        db.commit()
        db.refresh(db_risk)
        return {"risk_id": str(db_risk.risk_id), "patient_id": str(db_risk.patient_id), "status": "created"}
    except Exception as e:
        db.rollback()
        print("Error in create_risk:", e)
        raise HTTPException(status_code=500, detail=str(e))

class RiskUpdateRequest(BaseModel):
    severity: float = None
    likelihood: int = None
    risk_score: float = None
    notes: str = None

@router.post("/update/{risk_id}")
def update_risk(risk_id: str, update: RiskUpdateRequest, db: Session = Depends(get_db)):
    from uuid import UUID as UUID_type
    try:
        uuid_obj = UUID_type(risk_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid risk_id format (must be UUID)")
    risk = db.query(Risk).filter(Risk.risk_id == uuid_obj).first()
    if not risk:
        raise HTTPException(status_code=404, detail="Risk not found")
    if update.severity is not None:
        risk.severity = update.severity
    if update.likelihood is not None:
        risk.likelihood = update.likelihood
    # Always recalculate risk_score if either is present
    if (update.severity is not None or update.likelihood is not None):
        sev = update.severity if update.severity is not None else risk.severity
        freq = update.likelihood if update.likelihood is not None else risk.likelihood
        if sev is not None and freq is not None:
            try:
                risk.risk_score = float(sev) * float(freq)
            except Exception:
                risk.risk_score = None
    if update.notes is not None:
        risk.notes = update.notes
    db.commit()
    db.refresh(risk)
    return {"risk_id": str(risk.risk_id), "status": "updated"}

@router.get("/by_patient/{patient_id}")
def get_risks_by_patient(patient_id: str, db: Session = Depends(get_db)):
    try:
        uuid_obj = UUID(patient_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid patient_id format (must be UUID)")
    risks = db.query(Risk).filter(Risk.patient_id == uuid_obj).all()
    result = []
    for r in risks:
        hazard = db.query(Hazard).filter(Hazard.hazard_id == r.hazard_id).first()
        hazard_code = None
        hazard_description = None
        if hazard:
            hazard_description = hazard.description
            hazard_code = getattr(hazard, 'hazard_code', None) or getattr(hazard, 'hazard_type', None)
        # Use patient-specific severity and likelihood from risk row
        severity = r.severity
        likelihood = r.likelihood
        # Compute risk_score as severity * likelihood if both are present
        risk_score = None
        try:
            if severity is not None and likelihood is not None:
                risk_score = float(severity) * float(likelihood)
        except Exception:
            risk_score = None
        result.append({
            "risk_id": str(r.risk_id),
            "hazard_code": hazard_code,
            "hazard_description": hazard_description,
            "severity": severity,
            "likelihood": likelihood,
            "risk_score": risk_score
        })
    return {"patient_id": patient_id, "risks": result}

@router.post("/auto_generate/{patient_id}")
def auto_generate_risks(patient_id: str, db: Session = Depends(get_db)):
    """
    Compute hazards for the patient and upsert a risk for each (no likelihood/risk_score assigned).
    """
    from uuid import UUID as UUID_type
    try:
        uuid_obj = UUID_type(patient_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid patient_id format (must be UUID)")

    # --- Hazard computation logic (same as /hazards/by_patient) ---
    from models.adl_answers import ADLAnswers
    from models.iadl_answers import IADLAnswers
    from models.patient_history import PatientHistory
    hazards = []
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

    # --- Upsert risk records ---
    from models.risk import Risk
    from sqlalchemy import and_
    created = []
    from models.hazards import Hazard
    
    print(f"DEBUG: Found {len(hazards)} hazards for patient {patient_id}")
    for i, hz in enumerate(hazards):
        print(f"DEBUG: Processing hazard {i+1}: {hz}")
        
        # Pick a unique hazard identifier (subclass or class)
        hazard_identifier = hz.get("hazard_subclass_id") or hz.get("hazard_class_id")
            
        if not hazard_identifier:
            print(f"DEBUG: Skipping hazard {i+1} - no identifier")
            continue
            
        print(f"DEBUG: Using hazard_identifier: {hazard_identifier}")
        
        # Find or create a Hazard row for this patient and hazard_identifier
        hazard_row = db.query(Hazard).filter(
            Hazard.patient_id == uuid_obj,
            Hazard.hazard_type == hazard_identifier
        ).first()
        if not hazard_row:
            print(f"DEBUG: Creating new Hazard row for {hazard_identifier}")
            hazard_row = Hazard(
                patient_id=uuid_obj,
                hazard_type=hazard_identifier,
                description=hz.get("item") or hz.get("code") or "",
                severity=None,
                weight=None
            )
            db.add(hazard_row)
            db.commit()
            db.refresh(hazard_row)
        else:
            print(f"DEBUG: Found existing Hazard row for {hazard_identifier}")
            
        hazard_uuid = hazard_row.hazard_id
        # Check if a Risk already exists for this patient + hazard_uuid
        existing = db.query(Risk).filter(and_(Risk.patient_id == uuid_obj, Risk.hazard_id == hazard_uuid)).first()
        if not existing:
            print(f"DEBUG: Creating new Risk for hazard {hazard_identifier}")
            db_risk = Risk(
                patient_id=uuid_obj,
                hazard_id=hazard_uuid,
                severity=None,
                likelihood=None,
                risk_score=None,
                notes=None
            )
            db.add(db_risk)
            db.commit()
            db.refresh(db_risk)
            created.append({"hazard_id": str(hazard_uuid), "risk_id": str(db_risk.risk_id)})
        else:
            print(f"DEBUG: Risk already exists for hazard {hazard_identifier}")
    
    print(f"DEBUG: Created {len(created)} new risk records")
    
    return {
        "patient_id": str(uuid_obj),
        "message": f"Generated {len(created)} risk records.",
        "created": created
    }
