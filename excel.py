import json
import time
import uuid
import aiohttp
import asyncio
import re
import openpyxl
from datetime import datetime
from types import NoneType

from pydantic import BaseModel

from src.patient.schemas import PatientBase as pb

async def main():
    
    class PatientBase(pb):
        pass
        
    class PatientRecordsBase(BaseModel):
        visit: str | None = None
        
        diagnosis: str | None = None
        treatment: str | None = None

        patient_id: uuid.UUID | str
        
        
    class PatientRecordsCreateDB(PatientRecordsBase):
        pass 
    
    async def process_excel_file(file_path):
        wb = openpyxl.load_workbook(file_path)
        sheet = wb["Лист1"]

        async with aiohttp.ClientSession() as session:
            i = 0
            for row in sheet.iter_rows(min_row=2, max_row=5337, values_only=True):
                
                patient_id = str(uuid.uuid4())
                
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
                
                async with session.post("https://clinic.universal-hub.site/patient_router/create_patient", json=patient_data_json) as response:
                    text_response = await response.text()
                    json_response = json.loads(text_response)
                    patient_id = json_response.get("id")
                    await response.read()
                    print(f"Response status for patient {i}: {response.status}, {response.text}")                              
                
                
                
                
                # async with session.post("http://localhost:8000/patient_router/create_patient", json=patient_data_json) as response:
                #     text_response = await response.text()
                #     json_response = json.loads(text_response)
                #     patient_id = json_response.get("id")
                #     await response.read()
                    # print(f"Response status for patient {i}: {response.status}, {response.text}")
                    
                first_patient_record_data = PatientRecordsCreateDB(
                    diagnosis=diagnosis,
                    visit=str(row[9]),
                    treatment=row[10],

                    patient_id=patient_id,
                )
                
                last_patient_record_data = PatientRecordsCreateDB(
                    diagnosis=diagnosis,
                    visit=str(row[8]),
                    treatment=row[10],
                    
                    patient_id=patient_id,
                )
                
                first_patient_record_data_json = first_patient_record_data.model_dump()
                last_patient_record_data_json = last_patient_record_data.model_dump()
                
                async with session.post('https://clinic.universal-hub.site/patient_records_router/create_patient_record', json=first_patient_record_data_json) as response:
                    await response.read()
                    print(f"Response status for first patient record {i}: {response.status}, {response.text}")
                    
                async with session.post('https://clinic.universal-hub.site/patient_records_router/create_patient_record', json=last_patient_record_data_json) as response:
                    await response.read()
                    print(f"Response status for last patient record {i}: {response.status}, {response.text}")
                    
                # async with session.post('http://localhost:8000/patient_records_router/create_patient_record', json=first_patient_record_data_json) as response:
                #     await response.read()
                    # print(f"Response status for first patient record {i}: {response.status}, {response.text}")
                    
                # async with session.post('http://localhost:8000/patient_records_router/create_patient_record', json=last_patient_record_data_json) as response:
                #     await response.read()
                    # print(f"Response status for last patient record {i}: {response.status}, {response.text}")
                    
                    
                time.sleep(10)
        wb.close()

    excel_file_path = "C:\\Users\\user\\Desktop\\ключи\\Extrapiramidnaya_Patologia_1.xlsx"
    await process_excel_file(excel_file_path)

if __name__ == "__main__":
    asyncio.run(main())
