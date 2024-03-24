import asyncio

import pytest
from httpx import AsyncClient
from sqlalchemy import *  # noqa

from src.auth.models import *  # noqa
from src.base import Base  # noqa
from src.config import settings
from src.conftest import *  # Нужно для переопределения settings.MODE, иначе DSN определится раньше. Должна стоять выше импорта src.config. # noqa
from src.database import async_engine
from src.main import app as fastapi_app
from src.patient.models import *  # noqa
from src.patient_records.models import *  # noqa


@pytest.fixture(autouse=True, scope="session")
async def prepare_database():
    assert settings.MODE == "TEST"

    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def authenticated_ac():
    async with AsyncClient(app=fastapi_app, base_url="http://test") as ac:
        response = await ac.post(
            "/auth/registration",
            json={"username": "authenticated_user", "role": "therapist", "password": "authenticated_user"},
        )
        assert response.status_code == 201

        response = await ac.post(
            "/auth/login", json={"username": "authenticated_user", "password": "authenticated_user"}
        )
        assert response.status_code == 200
        assert ac.cookies["access_token"]
        yield ac


@pytest.fixture(scope="function")
async def ac():
    async with AsyncClient(app=fastapi_app, base_url="http://test") as ac:
        yield ac
