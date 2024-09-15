from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field

from src.bids.enums import BidAuthorType, BidStatus


"""
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Доставка товаров Алексей",
  "status": "Created",
  "authorType": "User",
  "authorId": "61a485f0-e29b-41d4-a716-446655440000",
  "version": 1,
  "createdAt": "2006-01-02T15:04:05Z07:00"
""" 
class Bid(BaseModel):
    id: UUID
    name: str = Field(max_length=100)
    # description: str = Field(max_length=500)
    status: BidStatus
    # tenderId: UUID
    authorType: BidAuthorType
    authorId: UUID
    version: int = Field(1, ge=1)
    createdAt: datetime


class NewBidInfo(BaseModel):
    name: str = Field(max_length=100)
    description: str = Field(max_length=500)
    tenderId: UUID
    authorType: BidAuthorType
    authorId: UUID


class ChangeBidInfo(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=500)


class BidFeedback(BaseModel):
    id: UUID
    description: str = Field(max_length=1000)
    createdAt: datetime