import openpyxl
from src.api.service import PatientManager
from src.api import schemas


async def main():
    patient_manager = PatientManager()
    patient_crud = patient_manager.patient_crud

    async def process_excel_file(file_path):
        wb = openpyxl.load_workbook(file_path)
        sheet = wb["Лист1"]

        for row in sheet.iter_rows(min_row=2, max_row=11, values_only=True):
            patient_data = schemas.PatientCreateDB(
                full_name=row[0],
                gender=row[1],
                birthday=row[2], 
                age=row[3],
                inhabited_locality=row[4],
                living_place=row[5],
                job_title=row[6],
                diagnosis=row[7],
                last_visit=row[8],
                first_visit=row[9],
                treatment=row[10]
            )

            await patient_crud.create_patient(patient_data)

        wb.close()

    excel_file_path = "C:\\Users\\user\\Desktop\\ключи\\Extrapiramidnaya_Patologia_1.xlsx"
    await process_excel_file(excel_file_path)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())