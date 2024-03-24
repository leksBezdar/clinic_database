import pytest
from httpx import AsyncClient


@pytest.mark.parametrize(
    "username,role,password,status_code_reg,status_code_login",
    [
        ("integr_reg_login", "therapist", "integr_reg_login", 201, 200),
        ("integr_reg1", "explorer", "integr_reg1", 201, 200),
        ("integr_reg2", "not-existing-role", "integr_reg2", 422, 401),
    ],
)
async def test_login(username, role, password, status_code_reg, status_code_login, ac: AsyncClient):
    json = {"username": username, "role": role, "password": password}
    response = await ac.post("auth/registration", json=json)
    assert response.status_code == status_code_reg

    json = {"username": username, "password": password}
    response = await ac.post("auth/login", json=json)
    assert response.status_code == status_code_login
