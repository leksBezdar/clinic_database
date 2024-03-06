from . import schemas, models, exceptions
from .dao import PatientDAO

from ..auth.models import User
from ..auth.schemas import UserRole


class PatientService:

    @classmethod
    async def create_patient(cls, patient_data: schemas.PatientCreate, user: User) -> models.Patient:
        
        if user.role == UserRole.therapist.value:
            db_patient = await PatientDAO.add(
                schemas.PatientCreateDB(
                    therapist_id=user.id,
                    **patient_data.model_dump(),
                ))
            
            return db_patient
        
        raise exceptions.Forbidden

    # @classmethod
    # async def get_patient_records(cls, user: User, patient_id, offset: int, limit: int, **filter_by) -> list[models.Patient]:
        
    #     patient_records = await PatientDAO.find_all(
    #         models.Patient.id==patient_id,
    #         offset=offset,
    #         limit=limit
    #     )   
        
    #     formatted_patient_data = await cls.__format_patient_data(user=user, patient_records=patient_records) 
    #     return formatted_patient_data
        
    @classmethod
    async def get_all_patient_records(cls, *filter, user: User, offset: int, limit: int, **filter_by) -> list[models.Patient]:
        
        if user.role in [role.value for role in list(UserRole)]:
        
            patient_records = await PatientDAO.find_all(*filter, offset=offset, limit=limit, **filter_by)
            formatted_patient_data = await cls.__format_patient_data(user=user, patient_records=patient_records)

            return formatted_patient_data
        
        raise exceptions.Forbidden
    
    @classmethod
    async def update_patient_record(cls, user: User, patient_id: int, patient_in: schemas.PatientUpdate) -> models.Patient:
        
        if user.role == UserRole.therapist.value:  
            patient_record = await PatientDAO.update(models.Patient.id==patient_id, obj_in=patient_in)
            return patient_record
        
        raise exceptions.Forbidden
    
    @classmethod
    async def delete_patient_record(cls, user: User, patient_id: int) -> dict:
        
        if user.role == "therapist": 
            await PatientDAO.delete(models.Patient.id==patient_id)
            return {"Message": f"Therapist {user.id} deleted pathient record {patient_id} successfully"}
        
        raise exceptions.Forbidden

    @classmethod
    async def __format_patient_data(cls, user: User, patient_records: list[models.Patient]) -> list:

        if user.role == "therapist":
            return patient_records
        elif user.role == "explorer":
            return await cls.__format_patient_data_for_explorer(patient_records)

    @staticmethod
    async def __format_patient_data_for_explorer(patient_records: list[models.Patient]) -> list:
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
