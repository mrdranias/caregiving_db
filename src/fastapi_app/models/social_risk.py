from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from .adl_answers import Base  # Use shared Base


class SocialRisk(Base):
    __tablename__ = "social_risks"
    
    social_risk_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey('patients.patient_id'), nullable=False)
    social_hazard_code = Column(String(100), nullable=False)  # Maps to social_hazards or social_hazards_subclasses
    social_hazard_type = Column(String(50), nullable=False)   # 'class' or 'subclass'
    social_hazard_label = Column(String(255), nullable=False)
    social_hazard_description = Column(Text)
    
    # Risk assessment fields
    severity = Column(Float)      # 0-5 scale
    likelihood = Column(Integer)  # 0-6 scale (frequency)
    risk_score = Column(Float)    # severity × likelihood
    
    # Expert review
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
