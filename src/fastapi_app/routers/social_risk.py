from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from uuid import UUID

from models.social_risk import SocialRisk
from database import get_db
from pydantic import BaseModel
import requests
import os

router = APIRouter(prefix="/social_risk", tags=["social_risk"])

class SocialRiskCreateRequest(BaseModel):
    patient_id: UUID
    social_hazard_code: str
    social_hazard_type: str
    social_hazard_label: str
    social_hazard_description: Optional[str] = None
    severity: Optional[float] = None
    likelihood: Optional[int] = None
    risk_score: Optional[float] = None
    notes: Optional[str] = None

@router.post("/create")
def create_social_risk(risk: SocialRiskCreateRequest, db: Session = Depends(get_db)):
    try:
        db_risk = SocialRisk(
            patient_id=risk.patient_id,
            social_hazard_code=risk.social_hazard_code,
            social_hazard_type=risk.social_hazard_type,
            social_hazard_label=risk.social_hazard_label,
            social_hazard_description=risk.social_hazard_description,
            severity=risk.severity,
            likelihood=risk.likelihood,
            risk_score=risk.risk_score,
            notes=risk.notes
        )
        db.add(db_risk)
        db.commit()
        db.refresh(db_risk)
        return {"social_risk_id": str(db_risk.social_risk_id), "patient_id": str(db_risk.patient_id), "status": "created"}
    except Exception as e:
        db.rollback()
        print("Error in create_social_risk:", e)
        raise HTTPException(status_code=500, detail=str(e))

class SocialRiskUpdateRequest(BaseModel):
    severity: Optional[float] = None
    likelihood: Optional[int] = None
    risk_score: Optional[float] = None
    notes: Optional[str] = None

@router.post("/update/{social_risk_id}")
def update_social_risk(social_risk_id: str, update: SocialRiskUpdateRequest, db: Session = Depends(get_db)):
    try:
        from uuid import UUID as UUID_type
        uuid_obj = UUID_type(social_risk_id)
        
        db_risk = db.query(SocialRisk).filter(SocialRisk.social_risk_id == uuid_obj).first()
        if not db_risk:
            raise HTTPException(status_code=404, detail="Social risk not found")
        
        # Update fields
        if update.severity is not None:
            db_risk.severity = update.severity
        if update.likelihood is not None:
            db_risk.likelihood = update.likelihood
        if update.risk_score is not None:
            db_risk.risk_score = update.risk_score
        if update.notes is not None:
            db_risk.notes = update.notes
            
        db.commit()
        db.refresh(db_risk)
        return {"social_risk_id": str(db_risk.social_risk_id), "status": "updated"}
    except Exception as e:
        db.rollback()
        print("Error in update_social_risk:", e)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/by_patient/{patient_id}")
def get_social_risks_by_patient(patient_id: str, db: Session = Depends(get_db)):
    try:
        from uuid import UUID as UUID_type
        uuid_obj = UUID_type(patient_id)
        
        risks = db.query(SocialRisk).filter(SocialRisk.patient_id == uuid_obj).all()
        
        result = []
        for risk in risks:
            result.append({
                "social_risk_id": str(risk.social_risk_id),
                "patient_id": str(risk.patient_id),
                "social_hazard_code": risk.social_hazard_code,
                "social_hazard_type": risk.social_hazard_type,
                "social_hazard_label": risk.social_hazard_label,
                "social_hazard_description": risk.social_hazard_description,
                "severity": risk.severity,
                "likelihood": risk.likelihood,
                "risk_score": risk.risk_score,
                "notes": risk.notes,
                "created_at": risk.created_at.isoformat() if risk.created_at else None,
                "updated_at": risk.updated_at.isoformat() if risk.updated_at else None
            })
        
        return {"social_risks": result, "total": len(result)}
    except Exception as e:
        print("Error in get_social_risks_by_patient:", e)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/auto_generate/{patient_id}")
def auto_generate_social_risks(patient_id: str, db: Session = Depends(get_db)):
    """
    Compute social hazards for the patient and upsert a social risk for each (no likelihood/risk_score assigned).
    """
    try:
        from uuid import UUID as UUID_type
        uuid_obj = UUID_type(patient_id)
        
        # Get social hazards for this patient
        API_URL = os.getenv("API_URL", "http://localhost:8000")
        resp = requests.get(f"{API_URL}/social_hazards/by_patient/{patient_id}")
        
        if not resp.ok:
            raise HTTPException(status_code=500, detail="Failed to fetch social hazards")
        
        hazards_data = resp.json()
        social_hazards = hazards_data.get("social_hazards", [])
        
        created_count = 0
        updated_count = 0
        
        for hazard in social_hazards:
            hazard_code = hazard.get("hazard_code")
            hazard_type = "subclass" if hazard.get("hazard_subclass_id") else "class"
            hazard_label = hazard.get("hazard_label", "Unknown")
            hazard_description = hazard.get("hazard_description", "")
            
            if not hazard_code:
                continue
            
            # Check if social risk already exists
            existing_risk = db.query(SocialRisk).filter(
                SocialRisk.patient_id == uuid_obj,
                SocialRisk.social_hazard_code == hazard_code
            ).first()
            
            if existing_risk:
                # Update existing risk metadata
                existing_risk.social_hazard_label = hazard_label
                existing_risk.social_hazard_description = hazard_description
                updated_count += 1
            else:
                # Create new risk
                new_risk = SocialRisk(
                    patient_id=uuid_obj,
                    social_hazard_code=hazard_code,
                    social_hazard_type=hazard_type,
                    social_hazard_label=hazard_label,
                    social_hazard_description=hazard_description,
                    severity=None,  # Expert will set
                    likelihood=None,  # Expert will set
                    risk_score=None,  # Expert will set
                    notes=""
                )
                db.add(new_risk)
                created_count += 1
        
        db.commit()
        
        return {
            "patient_id": patient_id,
            "created": created_count,
            "updated": updated_count,
            "total_hazards": len(social_hazards)
        }
    
    except Exception as e:
        db.rollback()
        print("Error in auto_generate_social_risks:", e)
        raise HTTPException(status_code=500, detail=str(e))
