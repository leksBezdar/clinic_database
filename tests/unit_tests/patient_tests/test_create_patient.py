import pytest
from httpx import AsyncClient


@pytest.mark.parametrize(
    "full_name,birthday,gender,job_title,living_place,inhabited_locality,bp,ischemia,dep",
    [*[("string", "string", "string", "string", "string", "string", False, False, False)] * 8],
)
async def test_create_patient(
    full_name,
    birthday,
    gender,
    job_title,
    living_place,
    inhabited_locality,
    bp,
    ischemia,
    dep,
    authenticated_ac: AsyncClient,
):
    response = await authenticated_ac.post(
        "/patient/create",
        json={
            "full_name": full_name,
            "birthday": birthday,
            "gender": gender,
            "job_title": job_title,
            "living_place": living_place,
            "inhabited_locality": inhabited_locality,
            "bp": bp,
            "ischemia": ischemia,
            "dep": dep,
        },
    )

    assert response.status_code == 200
