from sqlalchemy import Column, String, Text, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from .adl_answers import Base  # Use the same Base as other models

class Hazard(Base):
    __tablename__ = "hazards"
    hazard_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # summary_id = Column(UUID(as_uuid=True), ForeignKey("questionnaire_summary.summary_id", ondelete="CASCADE"))
    history_id = Column(UUID(as_uuid=True), ForeignKey("patient_history.history_id", ondelete="SET NULL"))
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.patient_id", ondelete="CASCADE"))
    description = Column(Text)
    hazard_type = Column(String)
    severity = Column(String)
    weight = Column(Integer)
