"""
PRAPARE Pydantic Schemas (FHIR US-Core PRAPARE v2.3.0)
Request/response models for PRAPARE questionnaire endpoints
"""

from pydantic import BaseModel, Field, validator, field_validator
from typing import List, Optional, Dict, Any, Literal
from datetime import date, datetime
import uuid

class PRAPARESubmission(BaseModel):
    """PRAPARE questionnaire submission with structured responses aligned with FHIR US-Core PRAPARE v2.3.0"""
    
    # Required fields
    patient_id: uuid.UUID = Field(..., description="Patient UUID")
    date_completed: date = Field(default_factory=date.today, description="Date assessment was completed")
    assessed_by: str = Field(default="Gradio User", description="Name/ID of person conducting assessment")
    
    # 1. Personal Characteristics (1-5) - LOINC: 93025-5
    hispanic: Literal[0, 1, 2, 3] = Field(..., description="Hispanic/Latino: 0=No, 1=Yes, 2=Unknown, 3=Decline to answer (LOINC: 32624-9)")
    race_asian: bool = Field(False, description="Asian: True=Yes, False=No (LOINC: 32624-9)")
    race_native_hawaiian: bool = Field(False, description="Native Hawaiian: True=Yes, False=No (LOINC: 32624-9)")
    race_pacific_islander: bool = Field(False, description="Pacific Islander: True=Yes, False=No (LOINC: 32624-9)")
    race_black: bool = Field(False, description="Black/African American: True=Yes, False=No (LOINC: 32624-9)")
    race_white: bool = Field(False, description="White: True=Yes, False=No (LOINC: 32624-9)")
    race_american_indian: bool = Field(False, description="American Indian/Alaska Native: True=Yes, False=No (LOINC: 32624-9)")
    race_other: bool = Field(False, description="Other race: True=Yes, False=No (LOINC: 32624-9)")
    race_no_answer: bool = Field(False, description="Prefer not to answer race: True=Yes, False=No (LOINC: 32624-9)")
    
    # 2. Employment (6-7)
    farm_work: Literal[0, 1, 2] = Field(..., description="Farm work: 0=No, 1=Yes, 2=Decline to answer (LOINC: 63504-5)")
    military_service: Literal[0, 1, 2] = Field(..., description="Military service: 0=No, 1=Yes, 2=Decline to answer (LOINC: 63504-5)")
    
    # 3. Language (8)
    primary_language: Literal[0, 1, 2] = Field(..., description="Primary language: 0=English, 1=Other, 2=Decline to answer (LOINC: 63504-5)")
    
    # 4. Family & Home (9-11)
    household_size: int = Field(..., ge=1, le=20, description="Number of people in household (LOINC: 63504-5)")
    housing_situation: Literal[0, 1, 2, 3] = Field(..., description="Housing situation: 0=Do not have housing, 1=Temporary housing, 2=Have housing, 3=Decline to answer (LOINC: 71802-3)")
    housing_worry: Literal[0, 1, 2, 3] = Field(..., description="Housing worry: 0=Not at all worried, 1=Slightly worried, 2=Worried, 3=Decline to answer (LOINC: 93027-1)")
    
    # 5. Money & Resources (12-14)
    education_level: Literal[0, 1, 2, 3, 4, 5, 6, 7] = Field(..., description="Education level: 0=Less than high school, 1=High school/GED, 2=Some college, 3=Associate's degree, 4=Bachelor's degree, 5=Graduate degree, 6=Unknown, 7=Decline to answer (LOINC: 63504-5)")
    employment_status: Literal[0, 1, 2, 3, 4] = Field(..., description="Employment status: 0=Unemployed, 1=Part-Time, 2=Full-Time, 3=Retired/Student, 4=Decline to answer (LOINC: 63504-5)")
    
    # 6. Insurance (15)
    primary_insurance: Literal[0, 1, 2, 3, 4, 5, 6, 7] = Field(..., description="Primary insurance: 0=None, 1=Medicaid, 2=Medicare, 3=CHIP, 4=Private, 5=VA, 6=Other, 7=No Answer")
    annual_income: Literal[0, 1, 2, 3, 4, 5, 6] = Field(..., description="Annual income: 0=<$10,000, 1=$10,000-24,999, 2=$25,000-49,999, 3=$50,000-74,999, 4=$75,000+, 5=Unknown, 6=Decline to answer (LOINC: 63504-5)")
    
    # 6. Material Security (16-17)
    # Unmet needs (16) - Multi-select (LOINC: 63504-5)
    unmet_food: bool = Field(False, description="Food: True=Unmet need, False=No")
    unmet_clothing: bool = Field(False, description="Clothing: True=Unmet need, False=No")
    unmet_utilities: bool = Field(False, description="Utilities: True=Unmet need, False=No")
    unmet_childcare: bool = Field(False, description="Childcare: True=Unmet need, False=No")
    unmet_healthcare: bool = Field(False, description="Healthcare: True=Unmet need, False=No")
    unmet_phone: bool = Field(False, description="Phone: True=Unmet need, False=No")
    unmet_other: bool = Field(False, description="Other: True=Unmet need, False=No")
    unmet_no_answer: bool = Field(False, description="Prefer not to answer: True=Yes, False=No")
    
    # Transportation (17) - LOINC: 93039-6
    transportation_barrier: Literal[0, 1, 2, 3] = Field(..., description="Transportation barrier: 0=No, 1=Yes (medical appointments), 2=Yes (non-medical appointments), 3=Unable to respond")
    
    # 7. Social & Emotional Health (18-19)
    social_contact: Literal[0, 1, 2, 3, 4] = Field(..., description="Social contact: 0=Daily, 1=3 to 5 per week, 2=1-2 per week, 3=Less than once per week, 4=Decline to answer (LOINC: 63504-5)")
    stress_level: Literal[0, 1, 2, 3, 4, 5, 6] = Field(..., description="Stress level: 0=None, 1=A little, 2=Some, 3=A lot, 4=Extremely, 5=Unknown, 6=Decline to answer (LOINC: 63504-5)")
    
    # 8. Safety (20-22)
    incarceration_history: Literal[0, 1, 2] = Field(..., description="Incarceration history: 0=No, 1=Yes, 2=Decline to answer (LOINC: 63504-5)")
    feel_safe: Literal[0, 1, 2, 3] = Field(..., description="Feel safe: 0=No, 1=Sometimes, 2=Yes, 3=Decline to answer (LOINC: 93035-4)")
    domestic_violence: Literal[0, 1, 2] = Field(..., description="Domestic violence: 0=No, 1=Yes, 2=Decline to answer (LOINC: 63504-5)")
    
    # 9. ACORN Food Security (23-25) - LOINC: 93037-0, 93038-8, 63504-5
    food_worry: Literal[0, 1, 2, 3, 4] = Field(..., description="Worried food would run out: 0=Never true, 1=Sometimes true, 2=Often true, 3=Unknown, 4=Decline to answer")
    food_didnt_last: Literal[0, 1, 2, 3, 4] = Field(..., description="Food didn't last: 0=Never true, 1=Sometimes true, 2=Often true, 3=Unknown, 4=Decline to answer")
    need_food_help: Literal[0, 1, 2, 3] = Field(..., description="Need food help: 0=No, 1=Yes, 2=Unknown, 3=Decline to answer")
    
    # Metadata
    raw_responses: Dict[str, Any] = Field(default_factory=dict, description="Raw questionnaire responses")
    z_codes: List[str] = Field(default_factory=list, description="Generated Z-codes from responses")
    notes: Optional[str] = Field(None, max_length=2000, description="Additional clinical notes (max 2000 chars)")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Record creation timestamp")
    
    @field_validator('household_size')
    def validate_household_size(cls, v):
        if v < 1 or v > 20:
            raise ValueError('Household size must be between 1 and 20')
        return v
    
    # Address validation removed as it's not part of the PRAPARE form

class PRAPAREQuestionnaireResponse(PRAPARESubmission):
    """PRAPARE questionnaire response data for form display/editing"""
    prapare_id: Optional[uuid.UUID] = None
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "patient_id": "123e4567-e89b-12d3-a456-426614174000",
                "date_completed": "2023-01-01",
                "assessed_by": "Dr. Smith",
                "hispanic": 0,
                "race_asian": False,
                "race_native_hawaiian": False,
                "race_pacific_islander": False,
                "race_black": False,
                "race_white": True,
                "race_american_indian": False,
                "race_other": False,
                "race_no_answer": False,
                "farm_work": 0,
                "military_service": 0,
                "primary_language": 0,
                "household_size": 2,
                "housing_situation": 0,
                "housing_worry": 0,
                "education_level": 4,
                "employment_status": 0,
                "primary_insurance": 0,
                "annual_income": 3,
                "unmet_food": False,
                "unmet_clothing": False,
                "unmet_utilities": False,
                "unmet_childcare": False,
                "unmet_healthcare": False,
                "unmet_phone": False,
                "unmet_other": False,
                "unmet_no_answer": False,
                "transportation_barrier": 0,
                "social_contact": 0,
                "stress_level": 1,
                "incarceration_history": 0,
                "feel_safe": 3,
                "domestic_violence": 0,
                "food_worry": 0,
                "food_didnt_last": 0,
                "need_food_help": 0,
                "notes": "Patient reports stable living conditions and good social support.",
                "created_at": "2023-01-01T12:00:00Z"
            }
        }

class PRAPAREResponse(PRAPAREQuestionnaireResponse):
    """Response model with domain scoring and FHIR US-Core PRAPARE results"""
    domain_scores: Dict[str, int] = Field(default_factory=dict, description="Domain scores for each SDOH category (0-4 scale)")
    total_score: int = Field(0, description="Total SDOH risk score (0-28 scale)")
    risk_level: Literal["Low", "Moderate", "High"] = Field(..., description="Overall SDOH risk level")
    
    class Config:
        json_schema_extra = {
            "example": {
                "prapare_id": "123e4567-e89b-12d3-a456-426614174000",
                "patient_id": "123e4567-e89b-12d3-a456-426614174000",
                "date_completed": "2023-01-01",
                "domain_scores": {
                    "housing_stability": 0,
                    "food_security": 0,
                    "transportation_access": 0,
                    "financial_strain": 1,
                    "employment_education": 0,
                    "social_isolation": 0,
                    "interpersonal_safety": 0
                },
                "total_score": 1,
                "risk_level": "Low"
            }
        }

class PRAPAREDomainScores(BaseModel):
    """PRAPARE domain scores for questionnaire_summary table
    
    Scores are on a 0-4 scale for each domain, with 0=No risk and 4=High risk
    """
    patient_id: uuid.UUID = Field(..., description="Patient UUID")
    questionnaire_type: Literal["PRAPARE"] = "PRAPARE"
    assessment_date: date = Field(default_factory=date.today, description="Date of assessment")
    
    # Domain scores (0-4 scale)
    housing_stability: int = Field(..., ge=0, le=4, description="Housing stability domain score 0-4")
    food_security: int = Field(..., ge=0, le=4, description="Food security domain score 0-4")
    transportation_access: int = Field(..., ge=0, le=4, description="Transportation access domain score 0-4")
    financial_strain: int = Field(..., ge=0, le=4, description="Financial strain domain score 0-4")
    employment_education: int = Field(..., ge=0, le=4, description="Employment/education domain score 0-4")
    social_isolation: int = Field(..., ge=0, le=4, description="Social isolation domain score 0-4")
    interpersonal_safety: int = Field(..., ge=0, le=4, description="Interpersonal safety domain score 0-4")
    
    # Computed scores
    total_score: int = Field(..., ge=0, le=28, description="Total SDOH risk score (sum of all domains)")
    risk_level: Literal["Low", "Moderate", "High"] = Field(..., description="Overall SDOH risk level")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "patient_id": "123e4567-e89b-12d3-a456-426614174000",
                "questionnaire_type": "PRAPARE",
                "assessment_date": "2023-01-01",
                "housing_stability": 0,
                "food_security": 0,
                "transportation_access": 0,
                "financial_strain": 1,
                "employment_education": 0,
                "social_isolation": 0,
                "interpersonal_safety": 0,
                "total_score": 1,
                "risk_level": "Low"
            }
        }
        
    @classmethod
    def from_prapare_answers(cls, prapare: 'PRAPAREAnswers') -> 'PRAPAREDomainScores':
        """Calculate domain scores from PRAPARE answers using standard PRAPARE scoring algorithm"""
        # Initialize domain scores
        domain_scores = {
            'patient_id': prapare.patient_id,
            'assessment_date': prapare.date_completed or date.today(),
            'housing_stability': 0,
            'food_security': 0,
            'transportation_access': 0,
            'financial_strain': 0,
            'employment_education': 0,
            'social_isolation': 0,
            'interpersonal_safety': 0
        }
        
        # Calculate housing stability score (0-4)
        if prapare.housing_situation in [1, 2]:  # Temporary housing or homeless
            domain_scores['housing_stability'] = 4
        elif prapare.housing_situation == 3:  # Other
            domain_scores['housing_stability'] = 2
            
        # Add housing worry (increases score)
        if prapare.housing_worry in [3, 4]:  # Very or extremely worried
            domain_scores['housing_stability'] = min(4, domain_scores['housing_stability'] + 2)
        elif prapare.housing_worry in [1, 2]:  # Slightly or moderately worried
            domain_scores['housing_stability'] = min(4, domain_scores['housing_stability'] + 1)
        
        # Calculate food security score (0-4) from ACORN questions
        food_security = 0
        if prapare.food_worry in [1, 2]:  # Sometimes/often true
            food_security += 1
        if prapare.food_didnt_last in [1, 2]:  # Sometimes/often true
            food_security += 1
        if prapare.need_food_help == 1:  # Yes
            food_security += 2
        domain_scores['food_security'] = min(4, food_security)
        
        # Calculate transportation access score (0-4)
        if prapare.transportation_barrier in [1, 2]:  # Yes (medical or non-medical)
            domain_scores['transportation_access'] = 4
        
        # Calculate financial strain score (0-4)
        if prapare.annual_income == 0:  # <$10,000
            domain_scores['financial_strain'] = 4
        elif prapare.annual_income == 1:  # $10,000-24,999
            domain_scores['financial_strain'] = 3
        elif prapare.annual_income == 2:  # $25,000-49,999
            domain_scores['financial_strain'] = 2
        elif prapare.annual_income == 3:  # $50,000-74,999
            domain_scores['financial_strain'] = 1
            
        # Add unmet needs (each adds to financial strain)
        unmet_needs = sum([
            prapare.unmet_food,
            prapare.unmet_clothing,
            prapare.unmet_utilities,
            prapare.unmet_childcare,
            prapare.unmet_healthcare,
            prapare.unmet_phone,
            prapare.unmet_other
        ])
        domain_scores['financial_strain'] = min(4, domain_scores['financial_strain'] + unmet_needs)
        
        # Calculate employment/education score (0-4)
        if prapare.employment_status == 1:  # Unemployed
            domain_scores['employment_education'] = 3
        elif prapare.employment_status == 2:  # Unable to work
            domain_scores['employment_education'] = 4
        elif prapare.employment_status == 0:  # Employed
            domain_scores['employment_education'] = 0
            
        # Add education level (lower education = higher risk)
        if prapare.education_level <= 1:  # Less than high school or high school/GED
            domain_scores['employment_education'] = min(4, domain_scores['employment_education'] + 2)
        elif prapare.education_level == 2:  # Some college
            domain_scores['employment_education'] = min(4, domain_scores['employment_education'] + 1)
        
        # Calculate social isolation score (0-4)
        if prapare.social_contact >= 3:  # A few times a year or less
            domain_scores['social_isolation'] = 3
            if prapare.social_contact == 4:  # Never
                domain_scores['social_isolation'] = 4
        
        # Add stress level
        if prapare.stress_level >= 3:  # A lot or extremely stressed
            domain_scores['social_isolation'] = min(4, domain_scores['social_isolation'] + 1)
        
        # Calculate interpersonal safety score (0-4)
        if prapare.domestic_violence == 1:  # Yes to domestic violence
            domain_scores['interpersonal_safety'] = 4
        elif prapare.feel_safe <= 1:  # Never or sometimes feel safe
            domain_scores['interpersonal_safety'] = 3
        elif prapare.incarceration_history == 1:  # History of incarceration
            domain_scores['interpersonal_safety'] = min(4, domain_scores['interpersonal_safety'] + 2)
        
        # Calculate total score and risk level
        total_score = sum([
            domain_scores['housing_stability'],
            domain_scores['food_security'],
            domain_scores['transportation_access'],
            domain_scores['financial_strain'],
            domain_scores['employment_education'],
            domain_scores['social_isolation'],
            domain_scores['interpersonal_safety']
        ])
        
        # Determine risk level based on total score
        if total_score >= 15:
            risk_level = "High"
        elif total_score >= 8:
            risk_level = "Moderate"
        else:
            risk_level = "Low"
        
        domain_scores['total_score'] = total_score
        domain_scores['risk_level'] = risk_level
        
        return cls(**domain_scores)
