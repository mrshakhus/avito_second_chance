from typing import Optional
from uuid import UUID
from sqlalchemy import and_, asc, insert, select
from src.bids.enums import BidAuthorType, BidDecision, BidStatus
from src.bids.models import Bid, BidApproval, BidFeedback, BidOldVersion
from src.exceptions import AccessDeniedException
from src.dao.base import BaseDAO
from src.database import async_session_maker
from src.tenders.enums import TenderServiceType, TenderStatus
from src.tenders.models import OrganizationResponsible, Tender, Employee, TenderOldVersion
from src.logger import logger


class BidDAO(BaseDAO):
    model = Bid

    @classmethod
    async def add_bid(
        cls,
        name: str,
        description: str,
        tenderId: UUID,
        authorType: BidAuthorType,
        authorId: UUID
    ):
        async with async_session_maker() as session:
            add_new_bid = (
                insert(Bid)
                .values(
                    name = name,
                    description = description,
                    status = BidStatus.CREATED,
                    tenderId = tenderId,
                    authorType = authorType,
                    authorId = authorId,
                )
                .returning(
                    Bid.id,
                    Bid.name,
                    Bid.description,
                    Bid.status,
                    Bid.authorType,
                    Bid.authorId,
                    Bid.version,
                    Bid.createdAt
                )
            )

            result = await session.execute(add_new_bid)
            bid = result.mappings().one()

            add_new_bid_version = (
                insert(BidOldVersion)
                .values(
                    bidName=bid.name,
                    bidDescription=bid.description,
                    bidId=bid.id,
                    bidVersion=bid.version,
                )
            )
            await session.execute(add_new_bid_version)

            add_bid_approval = (
                insert(BidApproval)
                .values(bidId=bid.id)
            )
            await session.execute(add_bid_approval)

            await session.commit()
            return bid
        

    @classmethod
    async def get_user_bids(
        cls,
        user_id = UUID,
        limit = int,
        offset = int
    ):
        async with async_session_maker() as session:
            get_needed_bids = (
                select(
                    Bid.id,
                    Bid.name,
                    Bid.status,
                    Bid.authorType,
                    Bid.authorId,
                    Bid.version,
                    Bid.createdAt
                )
                .where(Bid.authorId == user_id)
                .offset(offset)
                .limit(limit)
                .order_by(asc(Bid.name))
            )

            result = await session.execute(get_needed_bids)
            bids = result.mappings().all()
            return bids
        

    @classmethod
    async def get_tender_bids(
        cls,
        tender_id = str,
        limit = int,
        offset = int
    ):
        async with async_session_maker() as session:
            get_needed_bids = (
                select(
                    Bid.id,
                    Bid.name,
                    Bid.status,
                    Bid.authorType,
                    Bid.authorId,
                    Bid.version,
                    Bid.createdAt
                )
                .where(
                    and_(
                        Bid.tenderId == tender_id,
                        Bid.status == BidStatus.PUBLISHED
                        #может сделать для автора и ответственных 
                        #в его организации сделать по другому?
                    )
                )
                .offset(offset)
                .limit(limit)
                .order_by(asc(Bid.name))
            )

            result = await session.execute(get_needed_bids)
            bids = result.mappings().all()
            return bids
        

    @classmethod
    async def get_bid_status(
        cls,
        bid_id: str
    ):
        async with async_session_maker() as session:
            get_bid_status = (
                select(Bid.status)
                .where(Bid.id == bid_id)
            )

            result = await session.execute(get_bid_status)
            tender_status = result.scalars().one()
            return tender_status
        

    @classmethod
    async def change_bid_status(
        cls,
        bid_id: str,
        bid_status: BidStatus
    ):
        async with async_session_maker() as session:
            get_bid_status = (
                select(Bid)
                .where(Bid.id == bid_id)
            )

            result = await session.execute(get_bid_status)
            bid = result.scalars().one()
            bid.status = bid_status.value

            bid = bid.__dict__.copy()
            bid.pop('_sa_instance_state', None)

            await session.commit()
            return bid
        

    @classmethod
    async def change_bid_info(
        cls,
        bid_id: str,
        bid_name: str,
        bid_description: str,
    ):
        async with async_session_maker() as session:
            get_bid = (
                select(Bid)
                .where(Bid.id == bid_id)
            )
            result = await session.execute(get_bid)
            bid = result.scalars().one()

            if bid_name is not None:
                bid.name = bid_name

            if bid_description is not None:
                bid.description = bid_description

            bid.version += 1

            add_new_bid_version = (
                insert(BidOldVersion)
                .values(
                    bidName=bid.name,
                    bidDescription=bid.description,
                    bidId=bid.id,
                    bidVersion=bid.version,
                )
            )
            await session.execute(add_new_bid_version)

            bid = bid.__dict__.copy()
            bid.pop('_sa_instance_state', None)

            await session.commit()
            return bid
        

    @classmethod
    async def rollback_bid_version(
        cls,
        bid_id: str,
        bid_version: int
    ):
        async with async_session_maker() as session:
            get_bid = (
                select(Bid)
                .where(Bid.id == bid_id)
            )
            result = await session.execute(get_bid)
            bid = result.scalars().one()
            bid.version += 1

            get_old_bid_version = (
                select(BidOldVersion)
                .where(
                    and_(
                        BidOldVersion.bidId == bid_id,
                        BidOldVersion.bidVersion == bid_version
                    )
                )
            )
            result = await session.execute(get_old_bid_version)
            old_tender = result.scalars().one()

            bid.name = old_tender.bidName
            bid.description = old_tender.bidDescription

            add_new_bid_version = (
                insert(BidOldVersion)
                .values(
                    bidName=bid.name,
                    bidDescription=bid.description,
                    bidId=bid.id,
                    bidVersion=bid.version,
                )
            )
            await session.execute(add_new_bid_version)
            bid = bid.__dict__.copy()
            bid.pop('_sa_instance_state', None)

            await session.commit()
            return bid
        

    @classmethod
    async def cancel_bid(
        cls,
        bid_id: str
    ):
        async with async_session_maker() as session:
            get_bid = (
                select(Bid)
                .where(Bid.id == bid_id)
            )
            result = await session.execute(get_bid)
            bid = result.scalars().one()
            bid.status = BidStatus.CANCELED

            await session.commit()
            return bid
        

    @classmethod
    async def increment_approve_count(
        cls,
        bid_id: str,
        tender_id: UUID
    ):
        async with async_session_maker() as session:
            get_bid_decision = (
                select(BidApproval)
                .where(BidApproval.bidId == bid_id)
            )
            result = await session.execute(get_bid_decision)
            bid_decision = result.scalars().one()
            bid_decision.approveCount += 1

            if bid_decision.approveCount >= 3:
                get_tender = (
                    select(Tender)
                    .where(Tender.id == tender_id)
                )
                result = await session.execute(get_tender)
                tender = result.scalars().one()
                tender.status = TenderStatus.CLOSED

            get_bid = (
                select(Bid)
                .where(Bid.id == bid_id)
            )
            result = await session.execute(get_bid)
            bid = result.scalars().one()
            bid = bid.__dict__.copy()
            bid.pop('_sa_instance_state', None)

            await session.commit()
            return bid
        

    @classmethod
    async def leave_feedback(
        cls,
        bid_id: str,
        bid_feedback: str
    ):
        async with async_session_maker() as session:
            add_feedback = (
                insert(BidFeedback)
                .values(
                    bidId = bid_id,
                    description = bid_feedback
                )
            )
            await session.execute(add_feedback)

            get_bid = (
                select(Bid)
                .where(Bid.id == bid_id)
            )
            result = await session.execute(get_bid)
            bid = result.scalars().one()
            bid = bid.__dict__.copy()
            bid.pop('_sa_instance_state', None)

            await session.commit()
            return bid


    @classmethod
    async def get_feedback(
        cls,
        author_id: UUID,
        tender_id: str,
        limit: int,
        offset: int,
    ):
        async with async_session_maker() as session:
            get_bid = (
                select(Bid)
                .where(
                    and_(
                        Bid.authorId == author_id,
                        Bid.tenderId == tender_id
                    )
                )
            )
            result = await session.execute(get_bid)
            bid = result.scalars().one()

            get_feedback = (
                select(BidFeedback)
                .where(BidFeedback.bidId == bid.id)
                .offset(offset)
                .limit(limit)
            )
            result = await session.execute(get_feedback)
            feedback = result.scalars().all()

            return feedback


        





    # #TODO Потом отсюда убрать!!
    # @classmethod
    # async def TEMPORARY(
    #     cls,
    #     bid_id: str
    # ):
    #     async with async_session_maker() as session:
    #         add_bid_approval = (
    #             insert(BidApproval)
    #             .values(bidId=bid_id)
    #         )
    #         await session.execute(add_bid_approval)
    #         await session.commit()

