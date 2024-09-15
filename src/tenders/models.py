import uuid
from sqlalchemy import UUID, Column, DateTime, ForeignKey, Integer, String, TIMESTAMP, Text, func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ENUM
from src.database import Base


class Employee(Base):
    __tablename__ = 'employee'
    
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4())
    username = Column(String(50), unique=True, nullable=False)
    first_name = Column(String(50))
    last_name = Column(String(50))
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp())

    organization_responsible = relationship('OrganizationResponsible', back_populates='user')


organization_type = ENUM('IE', 'LLC', 'JSC', name='organization_type')

class Organization(Base):
    __tablename__ = 'organization'

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4())
    name = Column(String(100), nullable=False)
    description = Column(Text)
    type = Column(organization_type)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp())

    organization_responsible = relationship('OrganizationResponsible', back_populates='organization')


class OrganizationResponsible(Base):
    __tablename__ = 'organization_responsible'
    
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4())
    organization_id = Column(UUID(as_uuid=True), ForeignKey('organization.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('employee.id', ondelete='CASCADE'), nullable=False)

    organization = relationship('Organization', back_populates='organization_responsible')
    user = relationship('Employee', back_populates='organization_responsible')


service_type = ENUM('Construction', 'Delivery', 'Manufacture', name="service_type")
tender_status = ENUM('Created', 'Published', 'Closed', name="tender_status")

class Tender(Base):
    __tablename__ = 'tender'

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4())
    name = Column(String(100), nullable=False)
    description = Column(String(500), nullable=False)
    serviceType = Column(service_type, nullable=False)
    status = Column(tender_status, nullable=False)
    organizationId = Column(UUID(as_uuid=True), ForeignKey('organization.id', ondelete='CASCADE'), nullable=False)
    version = Column(Integer, server_default="1", nullable=False)
    createdAt = Column(TIMESTAMP, server_default=func.current_timestamp())


service_type_old = ENUM('Construction', 'Delivery', 'Manufacture', name="service_type_old")

class TenderOldVersion(Base):
    __tablename__ = 'tender_old_version'

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4())
    tenderName = Column(String(100), nullable=False)
    tenderDescription = Column(String(500), nullable=False)
    tenderServiceType = Column(service_type_old, nullable=False)
    tenderId = Column(UUID(as_uuid=True), ForeignKey('tender.id', ondelete='CASCADE'), nullable=False)
    tenderVersion = Column(Integer, nullable=False)
    createdAt = Column(TIMESTAMP, server_default=func.current_timestamp())
