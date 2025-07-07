from sqlalchemy import Column, String, ForeignKey, DECIMAL, UUID, Date, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.sql import func
import uuid

Base = declarative_base()

class HomeCarePlan(Base):
    __tablename__ = "home_care_plan"
    
    plan_id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(PGUUID(as_uuid=True), ForeignKey("patients.patient_id", ondelete="CASCADE"), nullable=False)
    risk_id = Column(PGUUID(as_uuid=True), ForeignKey("risks.risk_id", ondelete="CASCADE"), nullable=False)
    service_id = Column(PGUUID(as_uuid=True), ForeignKey("services.service_id", ondelete="CASCADE"), nullable=False)
    contractor_id = Column(PGUUID(as_uuid=True), ForeignKey("contractors.contractor_id", ondelete="CASCADE"), nullable=False)
    cost_id = Column(PGUUID(as_uuid=True), ForeignKey("costs.cost_id", ondelete="CASCADE"), nullable=False)
    frequency = Column(String)
    custom_cost = Column(DECIMAL(12, 2))
    start_date = Column(Date)
    end_date = Column(Date)
    status = Column(String, default='planned')
    notes = Column(Text)
    created_at = Column(DateTime, server_default=func.current_timestamp())
    updated_at = Column(DateTime, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
