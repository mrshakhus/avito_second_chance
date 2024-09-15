from typing import Optional
from uuid import UUID
from sqlalchemy import and_, asc, insert, select
from src.exceptions import AccessDeniedException
from src.dao.base import BaseDAO
from src.database import async_session_maker
from src.tenders.enums import TenderServiceType, TenderStatus
from src.tenders.models import OrganizationResponsible, Tender, Employee, TenderOldVersion
from src.logger import logger


class EmployeeDAO(BaseDAO):
    model = Employee


class OrganizationResponsibleDAO(BaseDAO):
    model = OrganizationResponsible


class TenderDAO(BaseDAO):
    model = Tender

    @classmethod
    async def add_tender(
        cls,
        name: str,
        description: str,
        serviceType: TenderServiceType,
        organizationId: str,
    ):
        async with async_session_maker() as session:
            add_new_tender = (
                insert(Tender)
                .values(
                    name=name,
                    description=description,
                    serviceType=serviceType,
                    status=TenderStatus.CREATED,
                    organizationId=organizationId,
                )
                .returning(
                    Tender.id,
                    Tender.name,
                    Tender.description,
                    Tender.status,
                    Tender.serviceType,
                    Tender.version,
                    Tender.createdAt
                )
            )

            result = await session.execute(add_new_tender)
            tender = result.mappings().one()

            add_new_tender_version = (
                insert(TenderOldVersion)
                .values(
                    tenderName=tender.name,
                    tenderDescription=tender.description,
                    tenderServiceType=tender.serviceType,
                    tenderId=tender.id,
                    tenderVersion=tender.version,
                )
            )
            await session.execute(add_new_tender_version)

            await session.commit()
            return tender
        

    @classmethod
    async def get_tenders(
        cls,
        limit = int,
        offset = int,
        service_type = Optional[list],
    ):
        async with async_session_maker() as session:
            get_needed_tenders = (
                select(
                    Tender.id,
                    Tender.name,
                    Tender.description,
                    Tender.status,
                    Tender.serviceType,
                    Tender.version,
                    Tender.createdAt
                )
                .where(
                    and_(
                        Tender.status == TenderStatus.PUBLISHED,
                        Tender.serviceType.in_(service_type) if service_type else True
                    )
                )
                .offset(offset)
                .limit(limit)
                .order_by(asc(Tender.name))
            )

            result = await session.execute(get_needed_tenders)
            tenders = result.mappings().all()
            return tenders
        

    @classmethod
    async def get_user_tenders(
        cls,
        user_id = UUID,
        limit = int,
        offset = int
    ):
        async with async_session_maker() as session:
            get_responsible_organization_id = (
                select(OrganizationResponsible.organization_id)
                .where(OrganizationResponsible.user_id == user_id)
            )

            result = await session.execute(get_responsible_organization_id)
            responsible_organization_id = result.scalars().one()
            print(responsible_organization_id)

            get_needed_tenders = (
                select(
                    Tender.id,
                    Tender.name,
                    Tender.description,
                    Tender.status,
                    Tender.serviceType,
                    Tender.version,
                    Tender.createdAt
                )
                .where(Tender.organizationId == responsible_organization_id)
                .offset(offset)
                .limit(limit)
                .order_by(asc(Tender.name))
                )

            result = await session.execute(get_needed_tenders)
            tenders = result.mappings().all()
            print(tenders)
            return tenders
        

    @classmethod
    async def get_tender_status(
        cls,
        tender_id: str
    ):
        async with async_session_maker() as session:
            get_tender_status = (
                select(Tender.status)
                .where(Tender.id == tender_id)
            )

            result = await session.execute(get_tender_status)
            tender_status = result.scalars().one()
            return tender_status
        

    @classmethod
    async def change_tender_status(
        cls,
        tender_id: str,
        tender_status: TenderStatus
    ):
        async with async_session_maker() as session:
            get_tender_status = (
                select(Tender)
                .where(Tender.id == tender_id)
            )

            result = await session.execute(get_tender_status)
            tender = result.scalars().one()
            tender.status = tender_status.value

            tender = tender.__dict__.copy()
            tender.pop('_sa_instance_state', None)

            await session.commit()
            return tender
        

    @classmethod
    async def change_tender_info(
        cls,
        tender_id: str,
        tender_name: str,
        tender_description: str,
        tender_service_type: TenderServiceType
    ):
        async with async_session_maker() as session:
            get_tender = (
                select(Tender)
                .where(Tender.id == tender_id)
            )
            result = await session.execute(get_tender)
            tender = result.scalars().one()

            if tender_name is not None:
                tender.name = tender_name

            if tender_description is not None:
                tender.description = tender_description

            if tender_service_type is not None:
                tender.serviceType = tender_service_type

            tender.version += 1

            add_new_tender_version = (
                insert(TenderOldVersion)
                .values(
                    tenderName=tender.name,
                    tenderDescription=tender.description,
                    tenderServiceType=tender.serviceType,
                    tenderId=tender.id,
                    tenderVersion=tender.version,
                )
            )
            await session.execute(add_new_tender_version)

            await session.commit()
            return tender
        

    @classmethod
    async def rollback_tender_version(
        cls,
        tender_id: str,
        tender_version: int
    ):
        async with async_session_maker() as session:
            get_tender = (
                select(Tender)
                .where(Tender.id == tender_id)
            )

            result = await session.execute(get_tender)
            tender = result.scalars().one()
            tender.version += 1

            get_old_tender_version = (
                select(TenderOldVersion)
                .where(
                    and_(
                        TenderOldVersion.tenderId == tender_id,
                        TenderOldVersion.tenderVersion == tender_version
                    )
                )
            )

            result = await session.execute(get_old_tender_version)
            old_tender = result.scalars().one()

            tender.name = old_tender.tenderName
            tender.description = old_tender.tenderDescription
            tender.serviceType = old_tender.tenderServiceType

            add_new_tender_version = (
                insert(TenderOldVersion)
                .values(
                    tenderName=tender.name,
                    tenderDescription=tender.description,
                    tenderServiceType=tender.serviceType,
                    tenderId=tender.id,
                    tenderVersion=tender.version,
                )
            )
            await session.execute(add_new_tender_version)
            tender = tender.__dict__.copy()
            tender.pop('_sa_instance_state', None)

            await session.commit()
            return tender