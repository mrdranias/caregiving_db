from sqlalchemy import Column, Date, Integer, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy.ext.declarative import declarative_base
from .adl_answers import Base  # Use the same Base as other models

class IADLAnswers(Base):
    __tablename__ = "iadl_answers"
    iadl_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.patient_id", ondelete="CASCADE"))
    date_completed = Column(Date)
    telephone = Column(Integer)
    shopping = Column(Integer)
    food_preparation = Column(Integer)
    housekeeping = Column(Integer)
    laundry = Column(Integer)
    transportation = Column(Integer)
    medication = Column(Integer)
    finances = Column(Integer)
    answers = Column(JSON)
