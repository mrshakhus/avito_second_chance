from copy import deepcopy

from src.exceptions import AbsentTenderException, AccessDeniedException, UserIsNotPresentException
from src.tenders.dao import EmployeeDAO, OrganizationResponsibleDAO, TenderDAO


async def authenticate_user(
    username: str,
    check_rights = False
):
    user = await EmployeeDAO.find_one_or_none(username=username)
    if user is None:
        raise UserIsNotPresentException
    
    user_info = dict(deepcopy(user))
    
    if check_rights:
        responsible = await OrganizationResponsibleDAO.find_one_or_none(user_id=user["id"])
        if responsible is None:
            raise AccessDeniedException
    
        user_info["organization_id"] = responsible["organization_id"]

    return user_info


async def ensure_tender_exists(
    tender_id: str
):
    tender = await TenderDAO.find_one_or_none(id=tender_id)
    if tender is None:
        raise AbsentTenderException
    
    return tender


    
