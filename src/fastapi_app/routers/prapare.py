"""
PRAPARE FastAPI Router
Handles integer-coded PRAPARE questionnaire submission with domain scoring
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional, Dict, Any
from datetime import date, datetime
import uuid
import json

from models.prapare_answers import PRAPAREAnswers
from models.patients import Patients
from models.prapare_schemas import PRAPARESubmission, PRAPAREQuestionnaireResponse, PRAPAREDomainScores
from database import get_db

router = APIRouter(prefix="/prapare", tags=["PRAPARE"])

def calculate_prapare_domain_scores(prapare_data: PRAPARESubmission) -> Dict[str, int]:
    """Calculate PRAPARE domain scores from integer-coded responses (0-4 scale per domain)"""
    
    # Housing Stability (0-4 scale)
    housing_score = 0
    if prapare_data.housing_situation == 0:  # No housing
        housing_score += 4
    elif prapare_data.housing_worry == 1:  # Worried about housing
        housing_score += 2
    
    # Food Security (0-4 scale) - Based on income and unmet needs
    food_score = 0
    # Check if any unmet needs are present (food, clothing, utilities, childcare, healthcare, phone, other)
    has_unmet_needs = any([
        prapare_data.unmet_food == 1,
        prapare_data.unmet_clothing == 1,
        prapare_data.unmet_utilities == 1,
        prapare_data.unmet_childcare == 1,
        prapare_data.unmet_healthcare == 1,
        prapare_data.unmet_phone == 1,
        prapare_data.unmet_other == 1
    ])
    
    if has_unmet_needs:
        food_score += 2
    if prapare_data.annual_income is not None and prapare_data.annual_income < 2:  # Income < $25,000
        food_score += 2
    
    # Transportation Access (0-4 scale)
    transport_score = 0
    if prapare_data.transportation_barrier == 1:  # Has transport barriers
        transport_score += 4
    
    # Financial Strain (0-4 scale)
    financial_score = 0
    if prapare_data.annual_income is not None and prapare_data.annual_income < 2:  # Less than $25,000 (codes 0,1)
        financial_score += 3
    elif prapare_data.annual_income is not None and prapare_data.annual_income < 3:  # Less than $50,000 (code 2)
        financial_score += 2
    if prapare_data.employment_status == 0:  # Unemployed
        financial_score += 1
    
    # Employment/Education (0-4 scale)
    employment_score = 0
    if prapare_data.employment_status == 0:  # Unemployed
        employment_score += 3
    if prapare_data.education_level == 1:  # Less than high school
        employment_score += 2
    
    # Social Isolation (0-4 scale)
    social_score = 0
    if prapare_data.social_contact == 1:  # Low social contact
        social_score += 3
    if prapare_data.stress_level >= 4:  # High stress
        social_score += 1
    
    # Interpersonal Safety (0-4 scale)
    safety_score = 0
    if prapare_data.feel_safe == 0:  # Doesn't feel safe
        safety_score += 3
    if prapare_data.domestic_violence == 1:  # Has domestic violence history
        safety_score += 4
    
    # Cap scores at 4
    return {
        "housing_stability": min(housing_score, 4),
        "food_security": min(food_score, 4),
        "transportation_access": min(transport_score, 4),
        "financial_strain": min(financial_score, 4),
        "employment_education": min(employment_score, 4),
        "social_isolation": min(social_score, 4),
        "interpersonal_safety": min(safety_score, 4)
    }

def generate_prapare_z_codes(prapare_data: PRAPARESubmission, domain_scores: Dict[str, int]) -> List[str]:
    """Generate ICD-10 Z-codes based on integer-coded PRAPARE responses"""
    z_codes = []
    
    # Housing-related Z-codes
    if prapare_data.housing_situation == 0:  # No housing
        z_codes.append('Z59.0')  # Homelessness
    elif prapare_data.housing_worry == 1:  # Worried about housing
        z_codes.append('Z59.1')  # Inadequate housing
    
    # Food insecurity
    if domain_scores.get('food_security', 0) >= 2:
        z_codes.append('Z59.4')  # Lack of adequate food and safe drinking water
    
    # Transportation
    if prapare_data.transportation_barrier == 1:
        z_codes.append('Z59.3')  # Problems related to transportation
    
    # Education
    if prapare_data.education_level == 1:  # Less than high school
        z_codes.append('Z55.9')  # Problems related to education and literacy
    
    # Employment
    if prapare_data.employment_status == 0:  # Unemployed
        z_codes.append('Z56.9')  # Unspecified problems related to employment
    
    # Social isolation
    if domain_scores.get('social_isolation', 0) >= 3:
        z_codes.append('Z60.2')  # Problems related to living alone
    
    # Safety concerns
    if prapare_data.domestic_violence == 1:
        z_codes.append('Z91.4')  # Personal history of psychological trauma
    if prapare_data.feel_safe == 0:
        z_codes.append('Z60.4')  # Social exclusion and rejection
    
    return z_codes

@router.post("/submit", response_model=PRAPAREQuestionnaireResponse)
async def submit_prapare_assessment(
    request: PRAPARESubmission,
    db: Session = Depends(get_db)
):
    """Submit a PRAPARE assessment with integer-coded responses"""
    
    # Verify patient exists
    patient = db.query(Patients).filter(Patients.patient_id == request.patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    # Calculate domain scores
    domain_scores = calculate_prapare_domain_scores(request)
    total_score = sum(domain_scores.values())
    
    # Generate Z-codes
    z_codes = generate_prapare_z_codes(request, domain_scores)
    
    # Check if a PRAPARE assessment already exists for this patient and date
    existing_assessment = db.query(PRAPAREAnswers).filter(
        PRAPAREAnswers.patient_id == request.patient_id,
        PRAPAREAnswers.date_completed == date.today()
    ).first()
    
    if existing_assessment:
        # Update existing assessment
        existing_assessment.hispanic = request.hispanic
        existing_assessment.race_asian = request.race_asian
        existing_assessment.race_native_hawaiian = request.race_native_hawaiian
        existing_assessment.race_pacific_islander = request.race_pacific_islander
        existing_assessment.race_black = request.race_black
        existing_assessment.race_white = request.race_white
        existing_assessment.race_american_indian = request.race_american_indian
        existing_assessment.race_other = request.race_other
        existing_assessment.race_no_answer = request.race_no_answer
        existing_assessment.farm_work = request.farm_work
        existing_assessment.military_service = request.military_service
        existing_assessment.primary_language = request.primary_language
        existing_assessment.housing_situation = request.housing_situation
        existing_assessment.housing_worry = request.housing_worry
        existing_assessment.primary_insurance = request.primary_insurance
        existing_assessment.annual_income = request.annual_income
        existing_assessment.unmet_food = request.unmet_food
        existing_assessment.unmet_clothing = request.unmet_clothing
        existing_assessment.unmet_utilities = request.unmet_utilities
        existing_assessment.unmet_childcare = request.unmet_childcare
        existing_assessment.unmet_healthcare = request.unmet_healthcare
        existing_assessment.unmet_phone = request.unmet_phone
        existing_assessment.unmet_other = request.unmet_other
        existing_assessment.unmet_no_answer = request.unmet_no_answer
        existing_assessment.transportation_barrier = request.transportation_barrier
        existing_assessment.social_contact = request.social_contact
        existing_assessment.stress_level = request.stress_level
        existing_assessment.incarceration_history = request.incarceration_history
        existing_assessment.feel_safe = request.feel_safe
        existing_assessment.domestic_violence = request.domestic_violence
        existing_assessment.education_level = request.education_level
        existing_assessment.employment_status = request.employment_status
        existing_assessment.raw_responses = request.raw_responses
        existing_assessment.z_codes = z_codes
        existing_assessment.assessed_by = request.assessed_by
        existing_assessment.notes = request.notes
        
        db.add(existing_assessment)
        db.commit()
        db.refresh(existing_assessment)
        prapare_answers = existing_assessment
    else:
        # Create new PRAPARE answers record
        prapare_answers = PRAPAREAnswers(
            patient_id=request.patient_id,
            date_completed=date.today(),
            
            # Demographics - integer coded
            hispanic=request.hispanic,
            race_asian=request.race_asian,
            race_native_hawaiian=request.race_native_hawaiian,
            race_pacific_islander=request.race_pacific_islander,
            race_black=request.race_black,
            race_white=request.race_white,
            race_american_indian=request.race_american_indian,
            race_other=request.race_other,
            race_no_answer=request.race_no_answer,
            
            # Work/Service
            farm_work=request.farm_work,
            military_service=request.military_service,
            
            # Social/Cultural
            primary_language=request.primary_language,
            
            # Housing
            housing_situation=request.housing_situation,
            housing_worry=request.housing_worry,
            
            # Insurance
            primary_insurance=request.primary_insurance,
            annual_income=request.annual_income,
            
            # Economic
            annual_pretax_income=request.annual_pretax_income,
            transportation_barrier=request.transportation_barrier,
            
            # Education/Employment
            education_level=request.education_level,
            employment_status=request.employment_status,
            
            # Social Needs
            social_contact=request.social_contact,
            stress_level=request.stress_level,
            feel_safe=request.feel_safe,
            domestic_violence=request.domestic_violence,
            
            # Raw responses and Z-codes
            raw_responses=request.raw_responses,
            z_codes=z_codes,
            assessed_by=request.assessed_by,
            notes=request.notes
        )
        
        # Save new PRAPARE answers
        db.add(prapare_answers)
        db.commit()
        db.refresh(prapare_answers)
    
    # Create or update questionnaire summary with domain scores
    questionnaire_summary = db.execute(
        text("SELECT * FROM questionnaire_summary WHERE patient_id = :patient_id AND prapare_id IS NOT NULL"),
        {'patient_id': request.patient_id}
    ).first()
    
    if questionnaire_summary:
        # Update existing summary
        db.execute(text("""
            UPDATE questionnaire_summary SET
                prapare_id = :prapare_id,
                housing_stability_score = :housing_stability,
                food_security_score = :food_security,
                transportation_score = :transportation_access,
                social_isolation_score = :social_isolation,
                economic_security_score = :financial_strain,
                education_employment_score = :employment_education
            WHERE patient_id = :patient_id AND prapare_id IS NOT NULL
        """), {
            'patient_id': request.patient_id,
            'prapare_id': prapare_answers.prapare_id,
            'housing_stability': domain_scores.get('housing_stability'),
            'food_security': domain_scores.get('food_security'),
            'transportation_access': domain_scores.get('transportation_access'),
            'financial_strain': domain_scores.get('financial_strain'),
            'employment_education': domain_scores.get('employment_education'),
            'social_isolation': domain_scores.get('social_isolation')
        })
    else:
        # Create new summary
        db.execute(text("""
            INSERT INTO questionnaire_summary (
                patient_id, prapare_id, 
                housing_stability_score, food_security_score, 
                transportation_score, economic_security_score,
                education_employment_score, social_isolation_score
            ) VALUES (
                :patient_id, :prapare_id,
                :housing_stability, :food_security,
                :transportation_access, :financial_strain,
                :employment_education, :social_isolation
            )
        """), {
            'patient_id': request.patient_id,
            'prapare_id': prapare_answers.prapare_id,
            'housing_stability': domain_scores.get('housing_stability'),
            'food_security': domain_scores.get('food_security'),
            'transportation_access': domain_scores.get('transportation_access'),
            'financial_strain': domain_scores.get('financial_strain'),
            'employment_education': domain_scores.get('employment_education'),
            'social_isolation': domain_scores.get('social_isolation')
        })
    
    db.commit()
    
    # Return response with proper defaults for all required fields
    return PRAPAREQuestionnaireResponse(
        prapare_id=str(prapare_answers.prapare_id),
        patient_id=str(prapare_answers.patient_id),
        date_completed=prapare_answers.date_completed,
        assessed_by=prapare_answers.assessed_by or "",
        notes=prapare_answers.notes or "",
        hispanic=prapare_answers.hispanic if prapare_answers.hispanic is not None else 3,  # Default: Decline to answer
        race_asian=prapare_answers.race_asian or False,
        race_native_hawaiian=prapare_answers.race_native_hawaiian or False,
        race_pacific_islander=prapare_answers.race_pacific_islander or False,
        race_black=prapare_answers.race_black or False,
        race_white=prapare_answers.race_white or False,
        race_american_indian=prapare_answers.race_american_indian or False,
        race_other=prapare_answers.race_other or False,
        race_no_answer=prapare_answers.race_no_answer or False,
        farm_work=prapare_answers.farm_work if prapare_answers.farm_work is not None else 2,  # Default: Decline to answer
        military_service=prapare_answers.military_service if prapare_answers.military_service is not None else 2,  # Default: Decline to answer
        primary_language=prapare_answers.primary_language if prapare_answers.primary_language is not None else 2,  # Default: Decline to answer
        household_size=prapare_answers.household_size if prapare_answers.household_size is not None else 1,  # Default: 1 person
        housing_situation=prapare_answers.housing_situation if prapare_answers.housing_situation is not None else 3,  # Default: Decline to answer
        housing_worry=prapare_answers.housing_worry if prapare_answers.housing_worry is not None else 3,  # Default: Decline to answer
        education_level=prapare_answers.education_level if prapare_answers.education_level is not None else 7,  # Default: Decline to answer
        employment_status=prapare_answers.employment_status if prapare_answers.employment_status is not None else 4,  # Default: Decline to answer
        primary_insurance=prapare_answers.primary_insurance if prapare_answers.primary_insurance is not None else 7,  # Default: No Answer
        annual_income=prapare_answers.annual_income if prapare_answers.annual_income is not None else 6,  # Default: Decline to answer
        unmet_food=prapare_answers.unmet_food or False,
        unmet_clothing=prapare_answers.unmet_clothing or False,
        unmet_utilities=prapare_answers.unmet_utilities or False,
        unmet_childcare=prapare_answers.unmet_childcare or False,
        unmet_healthcare=prapare_answers.unmet_healthcare or False,
        unmet_phone=prapare_answers.unmet_phone or False,
        unmet_other=prapare_answers.unmet_other or False,
        unmet_no_answer=prapare_answers.unmet_no_answer or False,
        transportation_barrier=prapare_answers.transportation_barrier if prapare_answers.transportation_barrier is not None else 3,  # Default: Unable to respond
        social_contact=prapare_answers.social_contact if prapare_answers.social_contact is not None else 4,  # Default: Decline to answer
        stress_level=prapare_answers.stress_level if prapare_answers.stress_level is not None else 6,  # Default: Decline to answer
        incarceration_history=prapare_answers.incarceration_history if prapare_answers.incarceration_history is not None else 2,  # Default: Decline to answer
        feel_safe=prapare_answers.feel_safe if prapare_answers.feel_safe is not None else 3,  # Default: Decline to answer
        domestic_violence=prapare_answers.domestic_violence if prapare_answers.domestic_violence is not None else 2,  # Default: Decline to answer
        food_worry=prapare_answers.food_worry if prapare_answers.food_worry is not None else 4,  # Default: Decline to answer
        food_didnt_last=prapare_answers.food_didnt_last if prapare_answers.food_didnt_last is not None else 4,  # Default: Decline to answer
        need_food_help=prapare_answers.need_food_help if prapare_answers.need_food_help is not None else 3,  # Default: Decline to answer
        raw_responses=prapare_answers.raw_responses or {},
        z_codes=z_codes
    )

@router.get("/by_patient/{patient_id}", response_model=Optional[PRAPAREQuestionnaireResponse])
async def get_patient_prapare(
    patient_id: str,
    db: Session = Depends(get_db)
):
    """Get latest PRAPARE assessment for a patient (questionnaire data only, no scoring)"""
    
    try:
        patient_uuid = uuid.UUID(patient_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid patient ID format"
        )
    
    try:
        # Query the database for the most recent PRAPARE answers
        prapare_answers = db.query(PRAPAREAnswers).filter(
            PRAPAREAnswers.patient_id == patient_uuid
        ).order_by(PRAPAREAnswers.date_completed.desc()).first()
        
        if not prapare_answers:
            return None
        
        # Prepare response data with proper defaults for required fields
        response_data = {
            "prapare_id": str(prapare_answers.prapare_id) if prapare_answers.prapare_id else None,
            "patient_id": str(prapare_answers.patient_id),
            "date_completed": prapare_answers.date_completed,
            "assessed_by": prapare_answers.assessed_by or "Gradio User",
            "notes": prapare_answers.notes or "",
            "hispanic": prapare_answers.hispanic if prapare_answers.hispanic is not None else 2,  # Default to Unknown
            "race_asian": bool(prapare_answers.race_asian or False),
            "race_native_hawaiian": bool(prapare_answers.race_native_hawaiian or False),
            "race_pacific_islander": bool(prapare_answers.race_pacific_islander or False),
            "race_black": bool(prapare_answers.race_black or False),
            "race_white": bool(prapare_answers.race_white or False),
            "race_american_indian": bool(prapare_answers.race_american_indian or False),
            "race_other": bool(prapare_answers.race_other or False),
            "race_no_answer": bool(prapare_answers.race_no_answer or False),
            "farm_work": prapare_answers.farm_work if prapare_answers.farm_work is not None else 2,  # Default to Decline to answer
            "military_service": prapare_answers.military_service if prapare_answers.military_service is not None else 2,  # Default to Decline to answer
            "primary_language": prapare_answers.primary_language if prapare_answers.primary_language is not None else 0,  # Default to English
            "household_size": prapare_answers.household_size or 1,  # Default to 1 if not set
            "housing_situation": prapare_answers.housing_situation if prapare_answers.housing_situation is not None else 3,  # Default to Decline to answer
            "housing_worry": prapare_answers.housing_worry if prapare_answers.housing_worry is not None else 3,  # Default to Decline to answer
            "primary_insurance": prapare_answers.primary_insurance or 0,  # Default to None
            "annual_income": prapare_answers.annual_income or 5,  # Default to Unknown
            "education_level": prapare_answers.education_level if prapare_answers.education_level is not None else 6,  # Default to Unknown
            "employment_status": prapare_answers.employment_status if prapare_answers.employment_status is not None else 4,  # Default to Decline to answer
            "transportation_barrier": prapare_answers.transportation_barrier or 0,  # Default to No
            "social_contact": prapare_answers.social_contact if prapare_answers.social_contact is not None else 4,  # Default to Decline to answer
            "stress_level": prapare_answers.stress_level if prapare_answers.stress_level is not None else 6,  # Default to Decline to answer
            "incarceration_history": prapare_answers.incarceration_history if hasattr(prapare_answers, 'incarceration_history') else 2,  # Default to Decline to answer
            "feel_safe": prapare_answers.feel_safe if prapare_answers.feel_safe is not None else 3,  # Default to Decline to answer
            "domestic_violence": prapare_answers.domestic_violence or 0,  # Default to No
            "food_worry": prapare_answers.food_worry if hasattr(prapare_answers, 'food_worry') else 4,  # Default to Decline to answer
            "food_didnt_last": prapare_answers.food_didnt_last if hasattr(prapare_answers, 'food_didnt_last') else 4,  # Default to Decline to answer
            "need_food_help": prapare_answers.need_food_help if hasattr(prapare_answers, 'need_food_help') else 3,  # Default to Decline to answer
            "raw_responses": prapare_answers.raw_responses or {},
            "z_codes": prapare_answers.z_codes or []
        }
        
        # Add unmet needs fields if they exist in the model
        for field in ['unmet_food', 'unmet_clothing', 'unmet_utilities', 'unmet_childcare', 
                     'unmet_healthcare', 'unmet_phone', 'unmet_other', 'unmet_no_answer']:
            if hasattr(prapare_answers, field):
                response_data[field] = bool(getattr(prapare_answers, field, False))
        
        # Create and return the response model
        return PRAPAREQuestionnaireResponse(**response_data)
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving PRAPARE data: {str(e)}"
        )

@router.get("/summary/{patient_id}", response_model=Optional[PRAPAREQuestionnaireResponse])
async def get_patient_prapare_summary(
    patient_id: str,
    db: Session = Depends(get_db)
):
    """Get latest PRAPARE assessment summary for a patient (questionnaire data only, no scoring)"""
    
    try:
        patient_uuid = uuid.UUID(patient_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid patient ID format"
        )
    
    try:
        # Get most recent PRAPARE answers
        prapare_answers = db.query(PRAPAREAnswers).filter(
            PRAPAREAnswers.patient_id == patient_uuid
        ).order_by(PRAPAREAnswers.date_completed.desc()).first()
        
        if not prapare_answers:
            return None
            
        # Prepare response data with proper defaults for required fields
        response_data = {
            "prapare_id": str(prapare_answers.prapare_id) if prapare_answers.prapare_id else None,
            "patient_id": str(prapare_answers.patient_id),
            "date_completed": prapare_answers.date_completed,
            "assessed_by": prapare_answers.assessed_by or "Gradio User",
            "notes": prapare_answers.notes or "",
            "hispanic": prapare_answers.hispanic if prapare_answers.hispanic is not None else 2,  # Default to Unknown
            "race_asian": bool(prapare_answers.race_asian or False),
            "race_native_hawaiian": bool(prapare_answers.race_native_hawaiian or False),
            "race_pacific_islander": bool(prapare_answers.race_pacific_islander or False),
            "race_black": bool(prapare_answers.race_black or False),
            "race_white": bool(prapare_answers.race_white or False),
            "race_american_indian": bool(prapare_answers.race_american_indian or False),
            "race_other": bool(prapare_answers.race_other or False),
            "race_no_answer": bool(prapare_answers.race_no_answer or False),
            "farm_work": prapare_answers.farm_work if prapare_answers.farm_work is not None else 2,  # Default to Decline to answer
            "military_service": prapare_answers.military_service if prapare_answers.military_service is not None else 2,  # Default to Decline to answer
            "primary_language": prapare_answers.primary_language if prapare_answers.primary_language is not None else 0,  # Default to English
            "household_size": prapare_answers.household_size or 1,  # Default to 1 if not set
            "housing_situation": prapare_answers.housing_situation if prapare_answers.housing_situation is not None else 3,  # Default to Decline to answer
            "housing_worry": prapare_answers.housing_worry if prapare_answers.housing_worry is not None else 3,  # Default to Decline to answer
            "primary_insurance": prapare_answers.primary_insurance or 0,  # Default to None
            "annual_income": prapare_answers.annual_income or 5,  # Default to Unknown
            "education_level": prapare_answers.education_level if prapare_answers.education_level is not None else 6,  # Default to Unknown
            "employment_status": prapare_answers.employment_status if prapare_answers.employment_status is not None else 4,  # Default to Decline to answer
            "transportation_barrier": prapare_answers.transportation_barrier or 0,  # Default to No
            "social_contact": prapare_answers.social_contact if prapare_answers.social_contact is not None else 4,  # Default to Decline to answer
            "stress_level": prapare_answers.stress_level if prapare_answers.stress_level is not None else 6,  # Default to Decline to answer
            "incarceration_history": prapare_answers.incarceration_history if hasattr(prapare_answers, 'incarceration_history') else 2,  # Default to Decline to answer
            "feel_safe": prapare_answers.feel_safe if prapare_answers.feel_safe is not None else 3,  # Default to Decline to answer
            "domestic_violence": prapare_answers.domestic_violence or 0,  # Default to No
            "food_worry": prapare_answers.food_worry if hasattr(prapare_answers, 'food_worry') else 4,  # Default to Decline to answer
            "food_didnt_last": prapare_answers.food_didnt_last if hasattr(prapare_answers, 'food_didnt_last') else 4,  # Default to Decline to answer
            "need_food_help": prapare_answers.need_food_help if hasattr(prapare_answers, 'need_food_help') else 3,  # Default to Decline to answer
            "raw_responses": prapare_answers.raw_responses or {},
            "z_codes": prapare_answers.z_codes or []
        }
        
        # Add unmet needs fields if they exist in the model
        for field in ['unmet_food', 'unmet_clothing', 'unmet_utilities', 'unmet_childcare', 
                     'unmet_healthcare', 'unmet_phone', 'unmet_other', 'unmet_no_answer']:
            if hasattr(prapare_answers, field):
                response_data[field] = bool(getattr(prapare_answers, field, False))
        
        return PRAPAREQuestionnaireResponse(**response_data)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
