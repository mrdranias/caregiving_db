"""
SQLAlchemy models for Community Resources - SDOH-responsive parent/child class structure
Following established parent/child pattern (like hazard_classes/hazard_subclasses)
"""
from sqlalchemy import Column, String, Text, Boolean, Integer, ForeignKey, DateTime, Date, Float
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class ResourceClasses(Base):
    """Parent class for community resource types - maps to PRAPARE SDOH domains"""
    __tablename__ = "resource_classes"
    
    class_id = Column(String(20), primary_key=True)  # 'HOUSING', 'FOOD', 'TRANSPORT', etc.
    class_name = Column(String(100), nullable=False)
    description = Column(Text)
    sdoh_domain = Column(String(50))  # Maps to PRAPARE assessment domains
    icon = Column(String(50))  # UI icon reference
    sort_order = Column(Integer, default=0)
    
    # Relationship to child classes
    subclasses = relationship("ResourceSubclasses", back_populates="parent_class")

class ResourceSubclasses(Base):
    """Child class for specific community resource types"""
    __tablename__ = "resource_subclasses"
    
    subclass_id = Column(String(30), primary_key=True)  # 'HOUSING_EMERGENCY', 'FOOD_PANTRY', etc.
    parent_class_id = Column(String(20), ForeignKey("resource_classes.class_id"), nullable=False)
    subclass_name = Column(String(100), nullable=False)
    description = Column(Text)
    
    # PRAPARE response mapping
    prapare_question_codes = Column(JSONB)  # LOINC codes this resource addresses
    eligibility_criteria = Column(JSONB)    # Standard eligibility requirements
    typical_wait_time_days = Column(Integer)
    
    # Relationships
    parent_class = relationship("ResourceClasses", back_populates="subclasses")
    resources = relationship("CommunityResources", back_populates="resource_subclass")

class CommunityResources(Base):
    """Actual community resource instances/providers"""
    __tablename__ = "community_resources"
    
    resource_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resource_subclass_id = Column(String(30), ForeignKey("resource_subclasses.subclass_id"), nullable=False)
    
    # Basic Information
    name = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Contact Information
    address = Column(Text)
    city = Column(String(100))
    state = Column(String(2), default='NC')
    zip_code = Column(String(10))
    phone = Column(String(20))
    website = Column(String(255))
    email = Column(String(255))
    
    # Service Details
    services_offered = Column(JSONB)  # Detailed service descriptions
    cost_info = Column(Text)  # "Free", "Sliding scale", "$X/month", etc.
    operating_hours = Column(JSONB)  # Structured hours of operation
    seasonal_availability = Column(Boolean, default=False)
    appointment_required = Column(Boolean, default=False)
    
    # Geographic and Access
    latitude = Column(Float)
    longitude = Column(Float)
    service_area_miles = Column(Integer, default=25)
    transportation_provided = Column(Boolean, default=False)
    
    # Administrative
    active = Column(Boolean, default=True)
    verified_date = Column(Date)
    capacity_current = Column(Integer)  # Current availability
    capacity_max = Column(Integer)      # Maximum capacity
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    resource_subclass = relationship("ResourceSubclasses", back_populates="resources")
    patient_connections = relationship("SdohResourceConnections", back_populates="resource")

class SdohResourceConnections(Base):
    """Maps patients to community resources based on SDOH assessment results"""
    __tablename__ = "sdoh_resource_connections"
    
    connection_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.patient_id", ondelete="CASCADE"), nullable=False)
    resource_id = Column(UUID(as_uuid=True), ForeignKey("community_resources.resource_id", ondelete="CASCADE"), nullable=False)
    prapare_id = Column(UUID(as_uuid=True), ForeignKey("prapare_answers.prapare_id", ondelete="CASCADE"))
    
    # Connection details
    connection_type = Column(String(20), default='referral')  # 'referral', 'enrollment', 'waitlist'
    priority_level = Column(String(10))  # 'high', 'medium', 'low'
    referral_date = Column(Date, default=func.current_date())
    connection_status = Column(String(20), default='pending')  # 'pending', 'active', 'completed', 'declined'
    
    # Follow-up tracking
    follow_up_needed = Column(Boolean, default=True)
    follow_up_date = Column(Date)
    outcome_notes = Column(Text)
    satisfaction_rating = Column(Integer)  # 1-5 scale
    
    # Metadata
    referred_by = Column(String(100))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    patient = relationship("Patient")
    resource = relationship("CommunityResources", back_populates="patient_connections")
    prapare_assessment = relationship("PrapareAnswers")

class SdohResourceMap(Base):
    """Maps PRAPARE assessment responses to appropriate community resource types"""
    __tablename__ = "sdoh_resource_map"
    
    prapare_question_code = Column(String(20), primary_key=True)  # LOINC code from PRAPARE
    response_code = Column(String(20), primary_key=True)          # Specific response code
    resource_subclass_id = Column(String(30), ForeignKey("resource_subclasses.subclass_id"), primary_key=True)
    
    # Mapping details
    priority_score = Column(Integer, default=1)  # 1=highest priority, 5=lowest
    eligibility_filter = Column(JSONB)  # Additional criteria (age, income, etc.)
    notes = Column(Text)
    
    # Relationship
    resource_subclass = relationship("ResourceSubclasses")
