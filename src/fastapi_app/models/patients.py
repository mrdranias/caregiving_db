from sqlalchemy import Column, Date, String, JSON
from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy.ext.declarative import declarative_base

from .adl_answers import Base  # Ensure same Base is used

class Patients(Base):
    __tablename__ = "patients"
    patient_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)
    dob = Column(Date)
    gender = Column(String)
    phone = Column(String)
    email = Column(String)
