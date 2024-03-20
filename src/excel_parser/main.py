import asyncio
import re
import uuid
from datetime import datetime
from types import NoneType

import aiohttp
import openpyxl
from pydantic import BaseModel


class PatientBase(BaseModel):
    full_name: str
    birthday: str | None = None
    gender: str
    job_title: str | None = None
    living_place: str | None = None
    inhabited_locality: str | None = None

    bp: bool = False
    ischemia: bool = False
    dep: bool = False


class PatientRecordsBase(BaseModel):
    visit: str | None = None

    diagnosis: str | None = None
    treatment: str | None = None

    patient_id: uuid.UUID | str


BASE_URL = "https://clinic.universal-hub.site"  # noqa
# BASE_URL = "http://localhost:8000" # noqa
excel_file_path = "C:\\Users\\user\\Desktop\\ключи\\Extrapiramidnaya_Patologia_1.xlsx"

therapist_login_data = {"username": "string", "password": "string"}


async def main():
    async def process_excel_file(file_path):
        wb = openpyxl.load_workbook(file_path)
        sheet = wb["Лист1"]

        async with aiohttp.ClientSession(cookie_jar=aiohttp.CookieJar(unsafe=True)) as session:
            async with session.post(f"{BASE_URL}/auth/login", json=therapist_login_data) as response:
                if response.status != 200:
                    (f"Failed to authenticate: {response.status}")
                    return

                cookies = session.cookie_jar.filter_cookies(BASE_URL)

                for i, row in enumerate(sheet.iter_rows(min_row=2, max_row=5337, values_only=True), start=1):
                    birthday = row[2]
                    diagnosis = row[7]
                    living_place = row[5]

                    if isinstance(birthday, datetime):
                        birthday_date = birthday.date()
                    elif isinstance(birthday, NoneType) or birthday == "-" or birthday == "нет даты":
                        birthday_date = 0
                    else:
                        try:
                            birthday_date = datetime.strptime(birthday, "%d.%m.%Y").date()
                        except TypeError:
                            try:
                                birthday_date = datetime.strptime(str(birthday), "%Y").date().year
                            except ValueError:
                                birthday_date = datetime.now().date()
                        except Exception as e:
                            with open("bugs.txt", "a+") as file:
                                file.write(str(birthday) + "    " + str(e) + "    " + "\n")
                                continue

                    if diagnosis:
                        bp = True if re.search(r"\bбп\b", diagnosis, flags=re.IGNORECASE) else False
                        ischemia = True if re.search(r"\bишемия\b", diagnosis, flags=re.IGNORECASE) else False
                        dep = True if re.search(r"\bд[эе]п\b", diagnosis, flags=re.IGNORECASE) else False

                    inhabited_locality = "Неопределено"
                    if living_place:
                        living_place = living_place.strip()
                        inhabited_locality = "Город" if living_place.startswith(("г", "Г")) else "Село"

                    patient_data = PatientBase(
                        birthday=str(birthday_date),
                        gender=row[1],
                        full_name=row[0],
                        living_place=living_place,
                        job_title=row[6],
                        inhabited_locality=inhabited_locality,
                        dep=dep,
                        bp=bp,
                        ischemia=ischemia,
                    )

                    patient_data_json = patient_data.model_dump()

                    async with session.post(
                        f"{BASE_URL}/patient/create", json=patient_data_json, cookies=cookies
                    ) as response:
                        if response.status != 200:
                            print(f"Failed to create patient {i}: {response.status}")
                            continue

                        patient_id = (await response.json()).get("id")

                    first_patient_record_data = PatientRecordsBase(
                        diagnosis=diagnosis,
                        visit=str(row[9]),
                        treatment=row[10],
                        patient_id=patient_id,
                    )

                    last_patient_record_data = PatientRecordsBase(
                        diagnosis=diagnosis,
                        visit=str(row[8]),
                        treatment=row[10],
                        patient_id=patient_id,
                    )

                    first_patient_record_data_json = first_patient_record_data.model_dump()
                    last_patient_record_data_json = last_patient_record_data.model_dump()

                    async with session.post(
                        f"{BASE_URL}/patient_records/create",
                        json=first_patient_record_data_json,
                        cookies=cookies,
                    ) as response:
                        if response.status != 200:
                            print(f"Failed to create first patient record {i}: {response.status}")
                            continue

                    async with session.post(
                        f"{BASE_URL}/patient_records/create",
                        json=last_patient_record_data_json,
                        cookies=cookies,
                    ) as response:
                        if response.status != 200:
                            print(f"Failed to create last patient record {i}: {response.status}")
                            continue

        wb.close()

    await process_excel_file(excel_file_path)


if __name__ == "__main__":
    asyncio.run(main())
