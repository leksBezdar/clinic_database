import re
import openpyxl

import datetime as dt
from datetime import datetime

from types import NoneType

from src.api.service import PatientManager
from src.api import schemas


async def main():
    patient_manager = PatientManager()
    patient_crud = patient_manager.patient_crud
    async def process_excel_file(file_path):
        wb = openpyxl.load_workbook(file_path)
        sheet = wb["Лист1"]
        
        bp = "Нет"
        ischemia = "Нет"
        dep = "Нет"
        
        for row in sheet.iter_rows(min_row=2, max_row=5337, values_only=True):
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
                        file.write(str(birthday)+'    '+str(e)+'    ' +'\n')
                        continue

            if type(birthday_date) == dt.date and birthday_date != 0:
                age = datetime.now().year - birthday_date.year
            else:
                age = 0

            if diagnosis:
                bp = "Да" if re.search(r'\bбп\b', diagnosis, flags=re.IGNORECASE) else "Нет"
                ischemia = "Да" if re.search(r'\bишемия\b', diagnosis, flags=re.IGNORECASE) else "Нет"
                dep = "Да" if re.search(r'\bд[эе]п\b', diagnosis, flags=re.IGNORECASE) else "Нет"

            inhabited_locality = "Неопределено"
            if living_place:
                living_place = living_place.strip()
                inhabited_locality = "Город" if living_place.startswith(('г', 'Г')) else "Село"

            patient_data = schemas.PatientCreateDB(
                birthday=str(birthday_date),
                full_name=row[0],
                gender=row[1],
                age=age,
                inhabited_locality=inhabited_locality,
                living_place=living_place,
                job_title=row[6],
                diagnosis=diagnosis,
                last_visit=str(row[8]),
                first_visit=str(row[9]),
                treatment=row[10],
                bp=bp,
                ischemia=ischemia,
                dep=dep,
            )
            await patient_crud.create_patient(patient_data)

        wb.close()



    excel_file_path = "C:\\Users\\user\\Desktop\\ключи\\Extrapiramidnaya_Patologia_1.xlsx"
    await process_excel_file(excel_file_path)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())