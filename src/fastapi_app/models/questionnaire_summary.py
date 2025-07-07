from sqlalchemy import Column, String, Integer, Date, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import uuid
from .adl_answers import Base  # Use the same Base as other models

class QuestionnaireSummary(Base):
    __tablename__ = "questionnaire_summary"
    summary_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.patient_id", ondelete="CASCADE"))
    iadl_id = Column(UUID(as_uuid=True), ForeignKey("iadl_answers.iadl_id", ondelete="SET NULL"))
    adl_id = Column(UUID(as_uuid=True), ForeignKey("adl_answers.adl_id", ondelete="SET NULL"))
    type = Column(String)
    total_score = Column(Integer)
    date_completed = Column(Date)
