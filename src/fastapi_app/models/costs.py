from sqlalchemy import Column, String, ForeignKey, DECIMAL, UUID, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID as PGUUID
import uuid

Base = declarative_base()

class Cost(Base):
    __tablename__ = "costs"
    
    cost_id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    contractor_id = Column(PGUUID(as_uuid=True), ForeignKey("contractors.contractor_id", ondelete="CASCADE"), nullable=False)
    service_id = Column(PGUUID(as_uuid=True), ForeignKey("services.service_id", ondelete="CASCADE"), nullable=False)
    amount = Column(DECIMAL(12, 2))
    billing_cycle = Column(String)
    payer = Column(String)
    
    __table_args__ = (UniqueConstraint('contractor_id', 'service_id', name='_contractor_service_uc'),)
