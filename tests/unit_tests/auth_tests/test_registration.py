# import pytest

# from httpx import AsyncClient

# @pytest.mark.parametrize("username,role,password,status_code",[
#     ("string", "therapist", "string", 201),
#     ("string", "therapist", "string", 409),
#     ("string1", "explorer", "string1", 201),
#     ("string2", "not-existing-role", "string2", 422),
# ])
# async def test_registration(username, role, password, status_code, ac: AsyncClient):
#     json={
#         "username": username,
#         "role": role,
#         "password": password
#     }
#     response = await ac.post("/auth/registration", json=json)
#     assert response.status_code == status_code
