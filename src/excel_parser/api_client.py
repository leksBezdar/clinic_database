from http.cookies import SimpleCookie

import aiohttp
from aiohttp import ClientSession
from constants import BASE_URL, THERAPIST_LOGIN_DATA
from schemas import PatientBase, PatientRecordsBase


class APIClient:

    @staticmethod
    async def authenticate(session: ClientSession) -> None:
        async with session.post(f"{BASE_URL}/auth/login", json=THERAPIST_LOGIN_DATA) as response:
            if response.status != 200:
                print(f"Failed to authenticate: {response.status}")
                return False
            return True

    @classmethod
    async def create_patient(cls, session: ClientSession, cookies: SimpleCookie, patient_data: PatientBase):
        patient_data_json = patient_data.model_dump()
        async with session.post(
            f"{BASE_URL}/patient/create", json=patient_data_json, cookies=cookies
        ) as response:
            if response.status != 200:
                await cls.write_error_to_file(await response.json())
                await cls.write_error_to_file(patient_data)

            res_json = await response.json()
            return res_json

    @classmethod
    async def write_error_to_file(cls, error_message):
        with open("error_log.txt", "a+") as file:
            file.write(str(error_message))
            file.write("\n")

    @classmethod
    async def create_patient_record(
        cls, session: ClientSession, cookies: SimpleCookie, patient_record_data: PatientRecordsBase
    ):
        patient_record_data_json = patient_record_data.model_dump()
        async with session.post(
            f"{BASE_URL}/patient_records/create", json=patient_record_data_json, cookies=cookies
        ) as response:
            if response.status != 200:
                print(f"Failed to create patient record: {response.status}")
            res_json = await response.json()
            return res_json

    @staticmethod
    async def close_session(session: ClientSession) -> None:
        if session:
            await session.close()


class APIFactory:
    @staticmethod
    async def create_session() -> ClientSession:
        return aiohttp.ClientSession(cookie_jar=aiohttp.CookieJar(unsafe=True))
