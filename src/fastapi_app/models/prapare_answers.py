"""
SQLAlchemy model for PRAPARE questionnaire responses (FHIR US-Core PRAPARE v2.3.0)
Maps to the prapare_answers table in the database
"""
from sqlalchemy import Column, Date, Integer, String, ForeignKey, JSON, ARRAY, Text, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from .adl_answers import Base  # Use shared Base

class PRAPAREAnswers(Base):
    __tablename__ = "prapare_answers"
    
    # Primary key and patient reference
    prapare_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.patient_id", ondelete="CASCADE"))
    date_completed = Column(Date, server_default='CURRENT_DATE')
    
    # 1. Personal Characteristics (1-5) - LOINC: 93025-5
    hispanic = Column(Integer)  # 0=No, 1=Yes, 2=Unknown, 3=Decline to answer (LOINC: 32624-9)
    race_asian = Column(Integer, default=0)  # 1=Yes, 0=No (LOINC: 32624-9)
    race_native_hawaiian = Column(Integer, default=0)  # 1=Yes, 0=No (LOINC: 32624-9)
    race_pacific_islander = Column(Integer, default=0)  # 1=Yes, 0=No (LOINC: 32624-9)
    race_black = Column(Integer, default=0)  # 1=Yes, 0=No (LOINC: 32624-9)
    race_white = Column(Integer, default=0)  # 1=Yes, 0=No (LOINC: 32624-9)
    race_american_indian = Column(Integer, default=0)  # 1=Yes, 0=No (LOINC: 32624-9)
    race_other = Column(Integer, default=0)  # 1=Yes, 0=No (LOINC: 32624-9)
    race_no_answer = Column(Integer, default=0)  # 1=Yes, 0=No (LOINC: 32624-9)
    
    # 2. Employment (6-7)
    farm_work = Column(Integer)  # 0=No, 1=Yes, 2=Decline to answer (LOINC: 63504-5)
    military_service = Column(Integer)  # 0=No, 1=Yes, 2=Decline to answer (LOINC: 63504-5)
    
    # 3. Language (8)
    primary_language = Column(Integer)  # 0=English, 1=Other, 2=Decline to answer (LOINC: 63504-5)
    
    # 4. Family & Home (9-11)
    household_size = Column(Integer)  # Number of household members (LOINC: 63504-5)
    housing_situation = Column(Integer)  # 0=Do not have housing, 1=Temporary housing, 2=Have housing, 3=Decline to answer (LOINC: 71802-3)
    housing_worry = Column(Integer)  # 0=Not at all worried, 1=Slightly worried, 2=worried, 3=Decline to answer (LOINC: 93027-1)
    
    # 5. Money & Resources (12-14)
    education_level = Column(Integer)  # 0=Less than high school, 1=High school/GED, 2=Some college, 3=Associate's degree, 4=Bachelor's degree, 5=Graduate degree, 6=Unknown, 7=Decline to answer (LOINC: 63504-5)
    employment_status = Column(Integer)  # 0=Unemployed, 1=Part-Time, 2=Full-Time, 3=Retired/Student, 4=Decline to answer (LOINC: 63504-5)
    
    # 6. Insurance (15)
    primary_insurance = Column(Integer, default=0)  # 0=None, 1=Medicaid, 2=Medicare, 3=CHIP, 4=Private, 5=VA, 6=Other, 7=No Answer
    
    annual_income = Column(Integer)  # 0=<$10,000, 1=$10,000-24,999, 2=$25,000-49,999, 3=$50,000-74,999, 4=$75,000+, 5=Unknown, 6=Decline to answer (LOINC: 63504-5)
    
    # 6. Material Security (16-17)
    # Unmet needs (16) - Multi-select (LOINC: 63504-5)
    unmet_food = Column(Integer, default=0)  # 1=Yes, 0=No
    unmet_clothing = Column(Integer, default=0)  # 1=Yes, 0=No
    unmet_utilities = Column(Integer, default=0)  # 1=Yes, 0=No
    unmet_childcare = Column(Integer, default=0)  # 1=Yes, 0=No
    unmet_healthcare = Column(Integer, default=0)  # 1=Yes, 0=No
    unmet_phone = Column(Integer, default=0)  # 1=Yes, 0=No
    unmet_other = Column(Integer, default=0)  # 1=Yes, 0=No
    unmet_no_answer = Column(Integer, default=0)  # 1=Yes, 0=No
    
    # Transportation (17) - LOINC: 93039-6
    transportation_barrier = Column(Integer)  # 0=No, 1=Yes (medical appointments), 2=Yes (non-medical appointments), 3=Unable to respond
    
    # 7. Social & Emotional Health (18-19)
    social_contact = Column(Integer)  # 0=Daily, 1=3 to 5 per week, 2=1-2 per week, 3=Less than once per week, 4=Decline to answer (LOINC: 63504-5)
    stress_level = Column(Integer)  # 0=None, 1=A little, 2=Some, 3=A lot, 4=Extremely, 5=Unknown, 6=Decline to answer (LOINC: 63504-5)
    
    # 8. Safety (20-22)
    incarceration_history = Column(Integer)  # 0=No, 1=Yes, 2=Decline to answer (LOINC: 63504-5)
    feel_safe = Column(Integer)  # 0=No, 1=Sometimes, 2=Yes, 3=Decline to answer (LOINC: 93035-4)
    domestic_violence = Column(Integer)  # 0=No, 1=Yes, 2=Decline to answer (LOINC: 63504-5)
    
    # 9. ACORN Food Security (23-25) - LOINC: 93037-0, 93038-8, 63504-5
    food_worry = Column(Integer)  # 0=Never true, 1=Sometimes true, 2=Often true, 3=Unknown, 4=Decline to answer
    food_didnt_last = Column(Integer)  # 0=Never true, 1=Sometimes true, 2=Often true, 3=Unknown, 4=Decline to answer
    need_food_help = Column(Integer)  # 0=No, 1=Yes, 2=Unknown, 3=Decline to answer
    
    # Metadata
    raw_responses = Column(JSON)  # Raw questionnaire responses (flexible JSON storage)
    z_codes = Column(ARRAY(Text))  # Generated Z-codes from responses
    created_at = Column(TIMESTAMP, server_default='NOW()')
    assessed_by = Column(Text)  # Clinician/assessor ID or name
    notes = Column(Text)  # Free-text notes
