from sqlalchemy import Column, Date, Integer, JSON, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class ADLAnswers(Base):
    __tablename__ = "adl_answers"
    adl_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.patient_id", ondelete="CASCADE"))
    date_completed = Column(Date)
    feeding = Column(Integer)
    bathing = Column(Integer)
    grooming = Column(Integer)
    dressing = Column(Integer)
    bowels = Column(Integer)
    bladder = Column(Integer)
    toilet_use = Column(Integer)
    transfers = Column(Integer)
    mobility = Column(Integer)
    stairs = Column(Integer)
    answers = Column(JSON)
