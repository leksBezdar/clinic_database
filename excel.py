import aiohttp
import asyncio
import json
import re
import openpyxl
from datetime import datetime
from types import NoneType
import datetime as dt

from pydantic import BaseModel
# from src.api.service import PatientManager
# from src.api import schemas

async def main():
    # patient_manager = PatientManager()
    # patient_crud = patient_manager.patient_crud
    
    class PatientBase(BaseModel):
        birthday: str | None = None
        gender: str
        full_name: str
        living_place: str | None = None
        job_title: str | None = None
        inhabited_locality: str | None = None
        diagnosis: str | None = None
        first_visit: str | None = None
        last_visit: str | None = None
        treatment: str | None = None
        bp: str = "Нет"
        ischemia: str = "Нет"
        dep: str = "Нет"


    class PatientCreate(PatientBase):
      pass

    async def process_excel_file(file_path):
        wb = openpyxl.load_workbook(file_path)
        sheet = wb["Лист1"]

        async with aiohttp.ClientSession() as session:
            i = 0
            for row in sheet.iter_rows(min_row=2, max_row=5337, values_only=True):
                i += 1
                birthday = row[2]
                diagnosis = row[7]
                living_place = row[5]

                if isinstance(birthday, datetime):
                    birthday_date = birthday.date()
                elif isinstance(birthday, NoneType) or birthday == "-" or birthday == "нет даты":
                    birthday_date = 0
                else:
                    try:
                        birthday_date = datetime.strptime(birthday, '%d.%m.%Y').date()
                    except TypeError:
                        try:
                            birthday_date = datetime.strptime(str(birthday), '%Y').date().year
                        except ValueError:
                            birthday_date = datetime.now().date()
                    except Exception as e:
                        with open("bugs.txt", "a+") as file:
                            file.write(str(birthday) + '    ' + str(e) + '    ' + '\n')
                            continue

                if diagnosis:
                    bp = "Да" if re.search(r'\bбп\b', diagnosis, flags=re.IGNORECASE) else "Нет"
                    ischemia = "Да" if re.search(r'\bишемия\b', diagnosis, flags=re.IGNORECASE) else "Нет"
                    dep = "Да" if re.search(r'\bд[эе]п\b', diagnosis, flags=re.IGNORECASE) else "Нет"

                inhabited_locality = "Неопределено"
                if living_place:
                    living_place = living_place.strip()
                    inhabited_locality = "Город" if living_place.startswith(('г', 'Г')) else "Село"

                patient_data = PatientCreate(
                    birthday=str(birthday_date),
                    gender=row[1],
                    full_name=row[0],
                    living_place=living_place,
                    job_title=row[6],
                    inhabited_locality=inhabited_locality,
                    diagnosis=diagnosis,
                    last_visit=str(row[8]),
                    first_visit=str(row[9]),
                    treatment=row[10],
                    bp=bp,
                    ischemia=ischemia,
                    dep=dep,
                )

                patient_data_json = patient_data.model_dump()

                async with session.post('https://clinic.universal-hub.site/create_patient_record', json=patient_data_json) as response:
                    print(f"Response status for patient {i}: {response.status}, {response.text}")

        wb.close()

    excel_file_path = "C:\\Users\\user\\Desktop\\ключи\\Extrapiramidnaya_Patologia_1.xlsx"
    await process_excel_file(excel_file_path)

if __name__ == "__main__":
    asyncio.run(main())
