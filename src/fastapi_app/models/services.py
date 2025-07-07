from sqlalchemy import Column, String, Text, UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID as PGUUID
import uuid

Base = declarative_base()

class Service(Base):
    __tablename__ = "services"
    
    service_id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    service_name = Column(String, nullable=False)
    service_category = Column(String)
    default_frequency = Column(String)
    description = Column(Text)
