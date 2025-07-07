from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from uuid import UUID
from models.prapare_answers import PRAPAREAnswers
from models.prapare_schemas import PRAPAREQuestionnaireResponse
from database import get_db

router = APIRouter(prefix="/social_hazards", tags=["social_hazards"])

@router.get("/by_patient/{patient_id}")
def get_social_hazards_by_patient(patient_id: str, db: Session = Depends(get_db)):
    """
    Returns a list of social hazards for a patient, derived from PRAPARE assessment data.
    """
    from uuid import UUID as UUID_type
    try:
        uuid_obj = UUID_type(patient_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid patient_id format (must be UUID)")

    social_hazards = []
    
    # Get latest PRAPARE assessment
    prapare = db.query(PRAPAREAnswers).filter(PRAPAREAnswers.patient_id == uuid_obj).order_by(PRAPAREAnswers.date_completed.desc()).first()
    
    if prapare:
        from sqlalchemy import text
        # Get PRAPARE item to hazard mappings
        prapare_map = db.execute(text("SELECT prapare_item, score_min, score_max, social_hazard_subclass_id, social_hazard_class_id FROM prapare_item_hazard_map")).fetchall()
        
        # Define PRAPARE fields to check - includes ALL fields mapped in prapare_item_hazard_map
        prapare_fields = [
            # Demographics
            ("hispanic", prapare.hispanic),
            ("race_asian", 1 if prapare.race_asian else 0),
            ("race_native_hawaiian", 1 if prapare.race_native_hawaiian else 0),
            ("race_pacific_islander", 1 if prapare.race_pacific_islander else 0),
            ("race_black", 1 if prapare.race_black else 0),
            ("race_american_indian", 1 if prapare.race_american_indian else 0),
            
            # Work and Service
            ("military_service", prapare.military_service),
            ("farm_work", prapare.farm_work),
            
            # Language and Education
            ("primary_language", prapare.primary_language),
            ("education_level", prapare.education_level),
            
            # Housing
            ("housing_situation", prapare.housing_situation),
            ("housing_worry", prapare.housing_worry),
            ("household_size", prapare.household_size),  # Added - mapped to overcrowding
            
            # Insurance
            ("primary_insurance", prapare.primary_insurance),
            
            # Financial
            ("annual_income", prapare.annual_income),
            
            # Transportation and Employment
            ("transportation_barrier", prapare.transportation_barrier),
            ("employment_status", prapare.employment_status),
            
            # Unmet Needs (Material Security)
            ("unmet_food", prapare.unmet_food),
            ("unmet_clothing", prapare.unmet_clothing),
            ("unmet_utilities", prapare.unmet_utilities),
            ("unmet_childcare", prapare.unmet_childcare),
            ("unmet_healthcare", prapare.unmet_healthcare),
            ("unmet_phone", prapare.unmet_phone),
            ("unmet_other", prapare.unmet_other),
            
            # Social and Support
            ("social_contact", prapare.social_contact),
            ("stress_level", prapare.stress_level),
            
            # Safety
            ("feel_safe", prapare.feel_safe),
            ("domestic_violence", prapare.domestic_violence),
            ("incarceration_history", prapare.incarceration_history),  # Added - mapped to safety
            
            # ACORN Food Security (Critical Missing Fields)
            ("food_worry", prapare.food_worry),  # Added - mapped to food insecurity
            ("food_didnt_last", prapare.food_didnt_last),  # Added - mapped to food insecurity
            ("need_food_help", prapare.need_food_help)  # Added - mapped to food insecurity
        ]
        
        # Check each PRAPARE field against mapping rules
        for item, score in prapare_fields:
            if score is None:
                continue
                
            for row in prapare_map:
                if row[0] == item and row[1] <= score <= row[2]:
                    hazard_data = {
                        "type": "social",
                        "item": item,
                        "score": score,
                        "hazard_subclass_id": row[3] if row[3] else None,
                        "hazard_class_id": row[4] if row[4] else None
                    }
                    
                    # Get hazard descriptions
                    if row[3]:  # subclass
                        hazard_info = db.execute(text("""
                            SELECT subclass_id, label, description 
                            FROM social_hazards_subclasses 
                            WHERE subclass_id = :subclass_id
                        """), {"subclass_id": row[3]}).fetchone()
                        if hazard_info:
                            hazard_data["hazard_code"] = hazard_info[0]
                            hazard_data["hazard_label"] = hazard_info[1]
                            hazard_data["hazard_description"] = hazard_info[2]
                    
                    elif row[4]:  # class
                        hazard_info = db.execute(text("""
                            SELECT class_id, label, description 
                            FROM social_hazards 
                            WHERE class_id = :class_id
                        """), {"class_id": row[4]}).fetchone()
                        if hazard_info:
                            hazard_data["hazard_code"] = hazard_info[0]
                            hazard_data["hazard_label"] = hazard_info[1]
                            hazard_data["hazard_description"] = hazard_info[2]
                    
                    social_hazards.append(hazard_data)
    
    return {
        "patient_id": patient_id,
        "social_hazards": social_hazards,
        "total_hazards": len(social_hazards)
    }
