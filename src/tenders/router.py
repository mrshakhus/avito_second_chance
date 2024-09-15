from typing import Optional
from fastapi import APIRouter, Query

from src.exceptions import AbsentVersionException, AccessDeniedException
from src.tenders.enums import TenderServiceType, TenderStatus
from src.tenders.schemas import ChangeTenderInfo, NewTenderInfo, Tender
from src.tenders.dao import TenderDAO
from src.tenders.dependencies import authenticate_user, ensure_tender_exists

router = APIRouter(
    prefix="/tenders",
    tags=["Тендеры"]
)

    
@router.get(
    "", 
    status_code=200,
    summary="Получение списка тендеров",
    description="""Список тендеров с возможностью фильтрации по типу услуг.
        \nЕсли фильтры не заданы, возвращаются все тендеры.
    """,
    response_model=list[Tender]
)
async def get_tenders(
    limit: int = Query(5, gt=0),
    offset: int = Query(0, ge=0),
    service_type: Optional[list[TenderServiceType]] = Query(None)
):
    tenders = await TenderDAO.get_tenders(
        limit=limit,
        offset=offset,
        service_type=service_type
    )
    return tenders


@router.post(
    "/new", 
    status_code=200,
    summary="Создание нового тендера",
    description="Создание нового тендера с заданными параметрами.",
    response_model=Tender
)
async def create_new_tender(
    tender_info: NewTenderInfo
):
    await authenticate_user(tender_info.creatorUsername, check_rights=True)

    tender = await TenderDAO.add_tender(
        name = tender_info.name,
        description = tender_info.description,
        serviceType = tender_info.serviceType,
        organizationId = tender_info.organizationId
    )
    return tender


@router.get(
    "/my", 
    status_code=200,
    summary="Получить тендеры пользователя",
    description="""Получение списка тендеров текущего пользователя.
        \nДля удобства использования включена поддержка пагинации.
    """,
    response_model=list[Tender]
)
async def get_user_tenders(
    username: str,
    limit: int = Query(5, gt=0),
    offset: int = Query(0, ge=0)
):
    user = await authenticate_user(username, check_rights=True)

    tenders = await TenderDAO.get_user_tenders(
        user_id = user["id"],
        limit = limit,
        offset = offset
    )
    return tenders


@router.get(
    "/{tenderId}/status", 
    status_code=200,
    summary="Получение текущего статуса тендера",
    description="Получить статус тендера по его уникальному идентификатору.",
    response_model=TenderStatus
)
async def get_tender_status(
    tenderId: str,
    username: str
):
    user_info = await authenticate_user(username, check_rights=True)
    tender = await ensure_tender_exists(tenderId)

    #Статус могут смотреть ответсвенные лишь той организации, 
    #где был создан тендер
    if user_info["organization_id"] != tender["organizationId"]:
        raise AccessDeniedException

    tenders_status = await TenderDAO.get_tender_status(tender_id = tenderId)
    return tenders_status


@router.put(
    "/{tenderId}/status", 
    status_code=200,
    summary="Изменить статус тендера",
    description="Изменить статус тендера по его идентификатору.",
    response_model=Tender
)
async def change_tender_status(
    tenderId: str,
    status: TenderStatus,
    username: str
):
    user_info = await authenticate_user(username, check_rights=True)
    tender = await ensure_tender_exists(tenderId)

    #Статус тендера могут менять все ответсвенные этой организации
    if user_info["organization_id"] != tender["organizationId"]:
        raise AccessDeniedException
    
    chaged_tender = await TenderDAO.change_tender_status(
        tender_id = tenderId,
        tender_status=status
    )
    
    return chaged_tender


@router.patch(
    "/{tenderId}/edit", 
    status_code=200,
    summary="Редактирование тендера",
    description="Изменение параметров существующего тендера.",
    response_model=Tender
)
async def change_tender_info(
    tenderId: str,
    username: str,
    changed_fields: ChangeTenderInfo
):
    user_info = await authenticate_user(username, check_rights=True)
    tender = await ensure_tender_exists(tenderId)

    #Редактировать тендер могут менять все ответсвенные этой организации
    if user_info["organization_id"] != tender["organizationId"]:
        raise AccessDeniedException
    
    changed_tender = await TenderDAO.change_tender_info(
        tender_id = tenderId,
        tender_name = changed_fields.name,
        tender_description = changed_fields.description,
        tender_service_type = changed_fields.serviceType,
    )
    return changed_tender


@router.put(
    "/{tenderId}/rollback/{version}", 
    status_code=200,
    summary="Откат версии тендера",
    description="Откатить параметры тендера к указанной версии. Это считается новой правкой, поэтому версия инкрементируется.",
    response_model=Tender
)
async def rollback_tender_version(
    tenderId: str,
    version: int,
    username: str
):
    user_info = await authenticate_user(username, check_rights=True)
    tender = await ensure_tender_exists(tenderId)

    if tender["version"] < version:
        raise AbsentVersionException

    #Редактировать тендер могут менять все ответсвенные этой организации
    if user_info["organization_id"] != tender["organizationId"]:
        raise AccessDeniedException
    
    tender = await TenderDAO.rollback_tender_version(
        tender_id = tenderId,
        tender_version = version
    )

    return tender