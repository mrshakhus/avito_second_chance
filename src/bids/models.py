from sqlalchemy import UUID, Column, ForeignKey, Integer, String, TIMESTAMP, func
from sqlalchemy.dialects.postgresql import ENUM
from src.database import Base


bid_status = ENUM('Created', 'Published', 'Canceled', name="bid_status")
author_type = ENUM('Organization', 'User', name="author_type")

class Bid(Base):
    __tablename__ = 'bid'

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4())
    name = Column(String(100), nullable=False)
    description = Column(String(500), nullable=False)
    status = Column(bid_status, nullable=False)
    tenderId = Column(UUID(as_uuid=True), ForeignKey('tender.id', ondelete='CASCADE'), nullable=False)
    authorType = Column(author_type, nullable=False)
    authorId = Column(UUID(as_uuid=True), ForeignKey('employee.id', ondelete='CASCADE'), nullable=False)
    version = Column(Integer, server_default="1", nullable=False)
    createdAt = Column(TIMESTAMP, server_default=func.current_timestamp())


class BidOldVersion(Base):
    __tablename__ = 'bid_old_version'

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4())
    bidName = Column(String(100), nullable=False)
    bidDescription = Column(String(500), nullable=False)
    bidId = Column(UUID(as_uuid=True), ForeignKey('bid.id', ondelete='CASCADE'), nullable=False)
    bidVersion = Column(Integer, nullable=False)
    createdAt = Column(TIMESTAMP, server_default=func.current_timestamp())


class BidApproval(Base):
    __tablename__ = 'bid_approval'

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4())
    bidId = Column(UUID(as_uuid=True), ForeignKey('bid.id', ondelete='CASCADE'), nullable=False)
    approveCount = Column(Integer, server_default='0', nullable=False)
    createdAt = Column(TIMESTAMP, server_default=func.current_timestamp())


class BidFeedback(Base):
    __tablename__ = 'bid_feedback'

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4())
    bidId = Column(UUID(as_uuid=True), ForeignKey('bid.id', ondelete='CASCADE'), nullable=False)
    description = Column(String(1000), nullable=False)
    createdAt = Column(TIMESTAMP, server_default=func.current_timestamp())