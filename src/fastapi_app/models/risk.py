from sqlalchemy import Column, String, Text, ForeignKey, Integer, Float
from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from .adl_answers import Base  # Use the same Base as other models

class Risk(Base):
    __tablename__ = "risks"
    risk_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    hazard_id = Column(UUID(as_uuid=True), ForeignKey("hazards.hazard_id", ondelete="CASCADE"))
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.patient_id", ondelete="CASCADE"))
    severity = Column(Float)  # QALY weight, 0-10
    likelihood = Column(Integer)  # Ordinal, 0-3
    risk_score = Column(Float)
    notes = Column(Text)
