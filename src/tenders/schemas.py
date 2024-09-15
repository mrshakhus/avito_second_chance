from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field

from src.tenders.enums import TenderServiceType, TenderStatus


#для списка тендеров
class Tender(BaseModel):
    # id: str = Field(max_length=100)
    id: UUID
    name: str = Field(max_length=100)
    description: str = Field(max_length=500)
    serviceType: TenderServiceType
    status: TenderStatus
    # organizationId: str = Field(max_length=100)
    version: int = Field(1, ge=1)
    # createdAt: str
    createdAt: datetime


#для введения данных по тендеру для создания
class NewTenderInfo(BaseModel):
    name: str = Field(max_length=100)
    description: str = Field(max_length=500)
    serviceType: TenderServiceType
    organizationId: str = Field(max_length=100)
    creatorUsername: str = Field(max_length=50)


#для введения данных для изменения тендера
class ChangeTenderInfo(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    serviceType: Optional[TenderServiceType] = None



# class tenderId(BaseModel):
#     tenderId: str = Field(max_length=100)

# class tenderName(BaseModel):
#     tenderName: str = Field(max_length=100)

# class tenderDescription(BaseModel):
#     tenderDescription: str = Field(max_length=500)

# class organizationId(BaseModel):
#     organizationId: str = Field(max_length=100)

# class tenderVersion(BaseModel):
#     tenderVersion: int = Field(1, ge=1)


# class tender(BaseModel):
#     id: tenderId
#     name: tenderName
#     description: tenderDescription
#     serviceType: tenderServiceType
#     status: tenderStatus
#     organizationId: organizationId
#     version: tenderVersion
#     createdAt: str