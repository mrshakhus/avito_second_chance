from datetime import datetime

import json
from httpx import ASGITransport, AsyncClient, patch
import pytest
from sqlalchemy import insert, text
from src.config import settings
from src.database import Base, async_session_maker, engine

from src.bids.models import *
from src.tenders.models import *

from fastapi.testclient import TestClient
from src.main import app as fastapi_app


@pytest.fixture(scope="session", autouse=True)
async def prepare_database():
    assert settings.MODE == "TEST"

    async with engine.begin() as conn:
        await conn.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"'))
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    def open_mock_json(model: str):
        with open(f"src/tests/mock_{model}.json", mode="r", encoding="utf-8") as file:
            return json.load(file)
        
    organization = open_mock_json("organization")
    tender = open_mock_json("tender")
    employee = open_mock_json("employee")
    organization_responsible = open_mock_json("organization_responsible")
    tender_old_version = open_mock_json("tender_old_version")

    async with async_session_maker() as session:
        add_organization = insert(Organization).values(organization)
        add_tender = insert(Tender).values(tender)
        add_employee = insert(Employee).values(employee)
        add_organization_responsible = insert(OrganizationResponsible).values(organization_responsible)
        add_tender_old_version = insert(TenderOldVersion).values(tender_old_version)

        await session.execute(add_organization)
        await session.execute(add_tender)
        await session.execute(add_employee)
        await session.execute(add_organization_responsible)
        await session.execute(add_tender_old_version)

        await session.commit()


# Взято из документации к pytest-asyncio
# @pytest.fixture(scope="session")
# def event_loop():
#     """Create an instance of the default event loop for each test case."""
#     loop = asyncio.new_event_loop()
#     yield loop
#     loop.close() 



@pytest.fixture(scope="session")
def test_app():
    # Create a test instance of the app
    fastapi_app.dependency_overrides = {}
    yield fastapi_app

@pytest.fixture(scope="session")
async def ac(test_app):
    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    
@pytest.fixture(scope="function")
async def session():
    async with async_session_maker() as session:
        yield session






