import openpyxl
from src.api.service import PatientManager
from src.api import schemas
from datetime import datetime


async def create_patient(patient_data):
    # Здесь должен быть код для отправки данных пациента
    print("Отправка данных пациента:", patient_data)


async def main():
    patient_manager = PatientManager()
    patient_crud = patient_manager.patient_crud
    async def process_excel_file(file_path):
        wb = openpyxl.load_workbook(file_path)
        sheet = wb["Лист1"]

        for row in sheet.iter_rows(min_row=2, max_row=5337, values_only=True):
            birthday = row[2]

            if isinstance(birthday, datetime):
                birthday_date = birthday
            else:
                try:
                    birthday_date = datetime.strptime(birthday, '%d.%m.%Y')
                except ValueError:
                    try:
                        birthday_date = datetime.strptime(birthday, '%Y')
                    except ValueError:
                        birthday_date = datetime.now()
                except Exception as e:
                    with open("bugs.txt", "w") as file:
                        file.write(str(birthday) + "\n")
                        continue

            if isinstance(birthday_date, datetime):
                age = datetime.now().year - birthday_date.year
            else:
                age = 0

            patient_data = schemas.PatientCreateDB(
                birthday=str(birthday),
                full_name=row[0],
                gender=row[1],
                age=age,
                inhabited_locality=row[4],
                living_place=row[5],
                job_title=row[6],
                diagnosis=row[7],
                last_visit=str(row[8]),
                first_visit=str(row[9]),
                treatment=row[10],
            )
            await patient_crud.create_patient(patient_data)

        wb.close()

    excel_file_path = "C:\\Users\\user\\Desktop\\ключи\\Extrapiramidnaya_Patologia_1.xlsx"
    await process_excel_file(excel_file_path)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())