from sqlalchemy import Column, String, Text, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .adl_answers import Base  # Use the same Base as other models

from sqlalchemy import ARRAY

class PatientHistory(Base):
    __tablename__ = "patient_history"
    history_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.patient_id", ondelete="CASCADE"))
    dx_codes = Column(ARRAY(Text))  # Array of diagnosis codes
    tx_codes = Column(ARRAY(Text))  # Array of treatment codes
    rx_codes = Column(ARRAY(Text))  # Array of medication codes
    sx_codes = Column(ARRAY(Text))  # Array of symptom codes
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
