from copy import deepcopy
from uuid import UUID
from src.bids.enums import BidStatus
from src.bids.dao import BidDAO
from src.exceptions import AbsentBidException, AccessDeniedException, UserIsNotPresentException
from src.tenders.dao import EmployeeDAO, OrganizationResponsibleDAO


async def authenticate_user(
    username: str = None,
    user_id: UUID = None,
    check_rights: bool = False
):
    user = None

    if username:
        user = await EmployeeDAO.find_one_or_none(username=username)

    if user_id:
        user = await EmployeeDAO.find_one_or_none(id=user_id)

    if user is None:
        raise UserIsNotPresentException
    
    user_info = dict(deepcopy(user))
    
    if check_rights:
        responsible = await OrganizationResponsibleDAO.find_one_or_none(user_id=user["id"])
        if responsible is None:
            raise AccessDeniedException
    
        user_info["organization_id"] = responsible["organization_id"]

    return user_info


async def ensure_bid_exists(
    bid_id: str,
    check_status: bool = False
):
    bid = await BidDAO.find_one_or_none(id=bid_id)

    if bid is None:
        raise AbsentBidException
    
    if check_status:
        if bid["status"] != BidStatus.PUBLISHED:
            raise AbsentBidException
    
    return bid