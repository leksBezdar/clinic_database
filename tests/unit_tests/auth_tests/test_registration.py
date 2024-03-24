import pytest
from httpx import AsyncClient


@pytest.mark.parametrize(
    "username,role,password,status_code",
    [
        ("unit_reg", "therapist", "unit_reg", 201),
        ("unit_reg", "therapist", "unit_reg", 409),
        ("unit_reg1", "explorer", "unit_reg1", 201),
        ("unit_reg2", "not-existing-role", "unit_reg2", 422),
    ],
)
async def test_registration(username, role, password, status_code, ac: AsyncClient):
    json = {"username": username, "role": role, "password": password}
    response = await ac.post("/auth/registration", json=json)
    assert response.status_code == status_code
