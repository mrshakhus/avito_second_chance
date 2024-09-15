from datetime import datetime
import json
from httpx import AsyncClient
import pytest

from src.tenders.enums import TenderServiceType
from tenders.dao import TenderDAO


# async def test_get_tenders(
#     ac: AsyncClient
# ):
#     response = await ac.get("/api/tenders", params={
#         "limit": 5,
#         "offset": 0,
#         "service_type": [TenderServiceType.DELIVERY.value]
#     })

#     assert response.status_code == 200

#     assert len(response.json()) == 3

#     print(response.json())

#     for tender in response.json():
#         print(tender)


# async def test_get_tenders(
#     ac: AsyncClient
# ):
#     response = await ac.post("/api/tenders/new", json={
#         "name": "Тендер 1",
#         "description": "Описание тендера",
#         "serviceType": "Construction",
#         "organizationId": "946bd3dd-3ab8-4c5c-b84b-7b36e5aeea65",
#         "creatorUsername": "usmanov",
#     })

#     assert response.status_code == 200
    
#     tender = response.json()
#     assert len(tender["id"]) == 36
#     assert tender["name"] == "Тендер 1"
#     assert tender["description"] == "Описание тендера"
#     assert tender["serviceType"] == "Construction"
#     assert tender["status"] == "Created"
#     assert tender["version"] == 1
#     assert datetime.strptime(tender["createdAt"], "%Y-%m-%dT%H:%M:%S.%f")

#     print(datetime.strptime(tender["createdAt"], "%Y-%m-%dT%H:%M:%S.%f"))
#     print(response.json())


# async def test_get_user_tenders(
#     ac: AsyncClient
# ):
#     response = await ac.get("/api/tenders/my", params={
#         "username": "begmatov",
#         "limit": 5,
#         "offset": 0
#     })

#     assert response.status_code == 200
    
#     assert len(response.json()) == 1

#     print(response.json())


# async def test_change_tender_info(
#     ac: AsyncClient
# ):
#     tenderId = "5852152d-3d30-461e-9500-0a0a491e80d7"
#     username = "petrov"
#     response = await ac.patch(f"/api/tenders/{tenderId}/edit?username={username}", json={
#         "name": "Строительство современного ТРЦ",
#         "description": "Проектирование и строительство современного ТРЦ на окраине города."
#     })

#     assert response.status_code == 200
    
#     tender = response.json()
#     assert tender["name"] == "Строительство современного ТРЦ"
#     assert tender["description"] == "Проектирование и строительство современного ТРЦ на окраине города."
#     assert tender["version"] == 3

#     print(response.json())


async def test_rollback_tender_version(
    ac: AsyncClient
):
    tenderId = "5852152d-3d30-461e-9500-0a0a491e80d7"
    version = 1
    response = await ac.put(f"/api/tenders/{tenderId}/rollback/{version}", params={
        "username": "petrov"
    })

    assert response.status_code == 200
    
    tender = response.json()
    assert tender["name"] == "Строительство торгового центра"
    assert tender["description"] == "Проектирование и строительство нового торгового центра на окраине города."
    assert tender["version"] == 3

    print(response.json())