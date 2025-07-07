from sqlalchemy import Column, String, Text, UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
import uuid

Base = declarative_base()

class Contractor(Base):
    __tablename__ = "contractors"
    
    contractor_id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    contact_info = Column(JSONB)
    qualifications = Column(Text)
