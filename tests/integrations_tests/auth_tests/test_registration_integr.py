import pytest
from httpx import AsyncClient


@pytest.mark.parametrize(
    "username,role,password,status_code",
    [
        ("string1", "therapist", "string1", 201),
        # ("string1", "explorer", "string1", 409),
        # ("string2", "not-existing-role", "string2", 422),
    ],
)
async def test_registration(username, role, password, status_code, ac: AsyncClient):
    json = {"username": username, "role": role, "password": password}
    response = await ac.post("v1/auth/registration", json=json)
    assert response.status_code == status_code

    if response.status_code == 201:
        response = await ac.post("v1/auth/login", json={"username": username, "password": password})
        assert response.status_code == 200
        assert response.cookies["access_token"]
        token_value = response.cookies["access_token"]
        token_value = token_value[1:]
        token_value = token_value[:-1]
        access_token = {"access_token": token_value}

        if response.status_code == 200:
            json = {
                "full_name": "string",
                "birthday": "string",
                "gender": "string",
                "job_title": "string",
                "living_place": "string",
                "inhabited_locality": "string",
                "bp": "Нет",
                "ischemia": "Нет",
                "dep": "Нет",
            }
            response = await ac.post("v1/patient/create", cookies=access_token, json=json)
