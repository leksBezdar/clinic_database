from . import schemas, models
from .dao import PatientDAO

from ..auth.service import AuthService, UserService
from ..auth.models import User


class PatientCRUD:

    async def create_patient(self, patient_data: schemas.PatientCreate, user: User) -> models.Patient:

        db_patient = await PatientDAO.add(
            schemas.PatientCreateDB(
                therapist_id=user.id,
                **patient_data.model_dump(),
            ))

        return db_patient

    async def get_patient_records(self, user: User, patient_id, offset: int, limit: int, **filter_by) -> list[models.Patient]:
        
        patient_records = await PatientDAO.find_all(
            models.Patient.id==patient_id,
            offset=offset,
            limit=limit
        )   
        
        return patient_records
        
    async def get_all_patient_records(self, *filter, user: User, offset: int, limit: int, **filter_by) -> list[models.Patient]:
        
        patient_records = await PatientDAO.find_all(*filter, offset=offset, limit=limit, **filter_by)

        formatted_patient_data = await self.__format_patient_data(user=user, patient_records=patient_records)
        
        return formatted_patient_data
    
    async def update_patient_record(self, user: User, patient_id: int, patient_in: schemas.PatientUpdate) -> models.Patient:
        
        patient_record = await PatientDAO.update(models.Patient.id==patient_id, obj_in=patient_in)

        return patient_record
    
    async def delete_patient_record(self, user: User, patient_id: int) -> dict:
        
        await PatientDAO.delete(models.Patient.id==patient_id)
        
        return {"Message": f"Therapist {user.id} deleted pathient record {patient_id} successfully"}

    async def __format_patient_data(self, user: User, patient_records: list[models.Patient]) -> list:

        if user.role == "therapist":
            print(1)
            return patient_records
        elif user.role == "explorer":
            return await self.__format_patient_data_for_explorer(patient_records)

    async def __format_patient_data_for_explorer(self, patient_records: list[models.Patient]) -> list:
        formatted_patient_records = []
    
        for patient in patient_records:
            patient_dict = patient.__dict__
    
            patient_data = {
                "id": patient_dict.get("id"),
                "therapist_id": patient_dict.get("therapist_id"),
                "gender": patient_dict.get("gender"),
                "inhabited_locality": patient_dict.get("inhabited_locality"),
                "diagnosis": patient_dict.get("diagnosis"),
                "treatment": patient_dict.get("treatment"),
                "bp": patient_dict.get("bp"),
                "ischemia": patient_dict.get("ischemia"),
                "dep": patient_dict.get("dep")
            }
    
            formatted_patient_records.append(schemas.ExplorerPatientDTO(**patient_data))
            return formatted_patient_records

class PatientManager:
    def __init__(self):
        self.patient_crud = PatientCRUD()
