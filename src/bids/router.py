from fastapi import APIRouter, Query

from src.exceptions import AbsentVersionException, AccessDeniedException
from src.bids.enums import BidDecision, BidStatus
from src.bids.dao import BidDAO
from src.bids.dependencies import authenticate_user, ensure_bid_exists
from src.bids.schemas import Bid, BidFeedback, ChangeBidInfo, NewBidInfo
from src.tenders.dependencies import ensure_tender_exists


router = APIRouter(
    prefix="/bids",
    tags=["Предложения"]
)

    
@router.post(
    "/new", 
    status_code=200,
    summary="Создание нового предложения",
    description="Создание предложения для существующего тендера.",
    response_model=Bid
)
async def add_bid(
    bid_info: NewBidInfo
):
    await authenticate_user(user_id=bid_info.authorId, check_rights=True)
    await ensure_tender_exists(bid_info.tenderId)

    #тут id у организаций должны быть разными, т.к. это предложение
    #то есть user_info["organization_id"] != tender["organizationId"]

    #несмотря на то, что в возвращаемом словаре есть 
    #лишний ключ, валидация все равно проходит
    
    bid = await BidDAO.add_bid(
        name = bid_info.name,
        description = bid_info.description,
        tenderId = bid_info.tenderId,
        authorType = bid_info.authorType,
        authorId = bid_info.authorId,
    )
    return bid


@router.get(
    "/my", 
    status_code=200,
    summary="Получение списка ваших предложений",
    description="""Получение списка предложений текущего пользователя.
        \nДля удобства использования включена поддержка пагинации.""",
    response_model=list[Bid]
)
async def get_user_bids(
    username: str,
    limit: int = Query(5, gt=0),
    offset: int = Query(0, ge=0),    
):
    user_info = await authenticate_user(username=username)

    bids = await BidDAO.get_user_bids(
        user_id = user_info["id"],
        limit = limit,
        offset = offset
    )
    return bids


@router.get(
    "/{tenderId}/list", 
    status_code=200,
    summary="Получение списка предложений для тендера",
    description="Получение предложений, связанных с указанным тендером.",
    response_model=list[Bid]
)
async def get_tender_bids(
    tenderId: str,
    username: str,
    limit: int = Query(5, gt=0),
    offset: int = Query(0, ge=0),    
):
    await authenticate_user(username=username)
    await ensure_tender_exists(tenderId)
    #Тут зачем то нужно выводить ошибку того, что предложение не найдено
    #И еще почему то может быть недостаточно прав, почему?

    bids = await BidDAO.get_tender_bids(
        tender_id = tenderId,
        limit = limit,
        offset = offset
    )
    return bids


@router.get(
    "/{bidId}/status", 
    status_code=200,
    summary="Получение текущего статуса предложения",
    description="Получить статус предложения по его уникальному идентификатору.",
    response_model=BidStatus
)
async def get_bid_status(
    bidId: str,
    username: str  
):
    user_info = await authenticate_user(username=username, check_rights=True)
    bid = await ensure_bid_exists(bid_id=bidId)
    author_info = await authenticate_user(user_id=bid["authorId"], check_rights=True)

    #Статус могут смотреть ответсвенные той организации, 
    #где было создано предложение
    if user_info["organization_id"] != author_info["organization_id"]:
        raise AccessDeniedException
    
    bid_status = await BidDAO.get_bid_status(bidId)
    return bid_status


@router.put(
    "/{bidId}/status", 
    status_code=200,
    summary="Изменение статуса предложения",
    description="Изменить статус предложения по его уникальному идентификатору.",
    response_model=Bid
)
async def change_bid_status(
    bidId: str,
    status: BidStatus,
    username: str  
):
    user_info = await authenticate_user(username=username)
    bid = await ensure_bid_exists(bid_id=bidId)

    #Лишь автора предложения может менять статус
    if user_info["id"] != bid["authorId"]:
        raise AccessDeniedException

    bid = await BidDAO.change_bid_status(
        bid_id = bidId,
        bid_status = status
    )
    return bid


@router.patch(
    "/{bidId}/edit", 
    status_code=200,
    summary="Редактирование параметров предложения",
    description="Редактирование существующего предложения.",
    response_model=Bid
)
async def change_bid_info(
    bidId: str,
    username: str,
    changed_fields: ChangeBidInfo 
):
    user_info = await authenticate_user(username=username)
    bid = await ensure_bid_exists(bid_id=bidId)

    #Лишь автора предложения может редактировать его
    if user_info["id"] != bid["authorId"]:
        raise AccessDeniedException
    
    bid = await BidDAO.change_bid_info(
        bid_id = bidId,
        bid_name = changed_fields.name,
        bid_description = changed_fields.description
    )
    return bid


@router.put(
    "/{bidId}/rollback/{version}", 
    status_code=200,
    summary="Откат версии предложения",
    description="Откатить параметры предложения к указанной версии. Это считается новой правкой, поэтому версия инкрементируется.",
    response_model=Bid
)
async def rollback_bid_version(
    bidId: str,
    version: int,
    username: str 
):
    user_info = await authenticate_user(username, check_rights=True)
    bid = await ensure_bid_exists(bidId)

    if bid["version"] < version:
        raise AbsentVersionException

    #Лишь автора предложения может откатывать его версию
    if user_info["id"] != bid["authorId"]:
        raise AccessDeniedException
    
    bid = await BidDAO.rollback_bid_version(
        bid_id = bidId,
        bid_version = version
    )

    return bid


@router.put(
    "/{bidId}/submit_decision", 
    status_code=200,
    summary="Отправка решения по предложению",
    description="Отправить решение (одобрить или отклонить) по предложению.",
    response_model=Bid
)
async def submit_bid_decision(
    bidId: str,
    decision: BidDecision,
    username: str 
):
    user_info = await authenticate_user(username=username, check_rights=True)
    bid = await ensure_bid_exists(bid_id=bidId, check_status=True)
    tender = await ensure_tender_exists(bid["tenderId"])

    #Принимать решения по принятию/отказу предложения могут
    #ответсвенные той организации, где было создан ТЕНДЕР
    if user_info["organization_id"] != tender["organizationId"]:
        raise AccessDeniedException
    
    #Достаточно одного отказа, чтобы закрыть предложение
    if decision == BidDecision.REJECTED:
        bid = await BidDAO.cancel_bid(bidId)
        return bid

    bid = await BidDAO.increment_approve_count(
        bid_id = bidId,
        tender_id = tender["id"]
    )
    return bid
    

@router.put(
    "/{bidId}/feedback", 
    status_code=200,
    summary="Отправка отзыва по предложению",
    description="Отправить отзыв по предложению.",
    response_model=Bid
)
async def leave_feedback(
    bidId: str,
    bidFeedback: str,
    username: str 
):
    user_info = await authenticate_user(username=username, check_rights=True)
    bid = await ensure_bid_exists(bid_id=bidId, check_status=True)
    tender = await ensure_tender_exists(bid["tenderId"])

    #Оставлять отзыв по предложению могут
    #ответсвенные той организации, где было создан ТЕНДЕР
    if user_info["organization_id"] != tender["organizationId"]:
        raise AccessDeniedException
    
    bid = await BidDAO.leave_feedback(
        bid_id = bidId,
        bid_feedback = bidFeedback
    )
    return bid


@router.get(
    "/{tenderId}/reviews", 
    status_code=200,
    summary="Просмотр отзывов на прошлые предложения",
    description="Ответственный за организацию может посмотреть прошлые отзывы на предложения автора, который создал предложение для его тендера.",
    response_model=list[BidFeedback]
)
async def get_feedback(
    tenderId: str,
    authorUsername: str,
    requesterUsername: str,
    limit: int = Query(5, gt=0),
    offset: int = Query(0, ge=0)
):
    user_info = await authenticate_user(username=requesterUsername, check_rights=True)
    tender = await ensure_tender_exists(tenderId)

    author_info = await authenticate_user(username=authorUsername)

    #Смотреть отзывы могут
    #ответсвенные той организации, где было создан ТЕНДЕР
    if user_info["organization_id"] != tender["organizationId"]:
        raise AccessDeniedException
    
    feedback = await BidDAO.get_feedback(
        author_id = author_info["id"],
        tender_id = tenderId,
        limit = limit,
        offset = offset
    )
    return feedback






# @router.put(
#     "/TEMPORARY"
# )
# async def submit_bid_decision(
#     bidIds: list[str]
# ):
#     for bidId in bidIds:
#         await BidDAO.TEMPORARY(bidId)
#         print("OK")

#     return "ok"
    
    
    





