import uuid
from loguru import logger

from . import schemas, models
from .dao import PatientDAO

from ..auth.models import User

from ..utils import log_error_with_method_info


class PatientService:
    
    @classmethod
    async def create_patient(cls, patient_data: schemas.PatientCreate, user: User) -> models.Patient:
        try: 
            logger.info(f"Therapist {user.username} creates patient {patient_data.full_name}")
            db_patient = await PatientDAO.add(
                schemas.PatientCreateDB(
                    **patient_data.model_dump(),
                    therapist_id=user.id,
                ))
            
            logger.info(f"Patient: {db_patient}")
            return db_patient
            
        except Exception as e:
            log_error_with_method_info(e)
            
    @classmethod
    async def get_patient(cls, patient_id: uuid.UUID, user: User) -> models.Patient:
        try:
            patient = await PatientDAO.find_one_or_none(models.Patient.id==patient_id)
            logger.info(f"Therapist {user.username} retrieves patient data {patient.full_name}")
            return patient or {"message": "No patient was found"}
        
        except Exception as e:
            log_error_with_method_info(e)

    @classmethod
    async def get_all_patients(cls, *filter, user: User, offset: int, limit: int, **filter_by) -> list[models.Patient]:
        try:
            logger.info(f"Therapist {user.username} retrieves the list of all patients")
            patients = await PatientDAO.find_all(
                *filter, offset=offset, limit=limit, **filter_by
            )

            return patients or []
        
        except Exception as e:
            log_error_with_method_info(e)

    @classmethod
    async def get_all_patients_by_therapist(cls, *filter, user: User, offset: int, limit: int, **filter_by) -> list[models.Patient]:
        try:
            logger.info(f"Therapist {user.username} retrieves the list of all patients")
            patients = await PatientDAO.find_all(
                *filter, offset=offset, limit=limit, **filter_by
            )

            return patients or []
        
        except Exception as e:
            log_error_with_method_info(e)
            
    
    @classmethod
    async def update_patient(cls, patient_id: uuid.UUID, user: User, patient_in: schemas.PatientUpdate) -> models.Patient:
        try:
            logger.info(f"Therapist {user.username} modifies patient data {patient_id}")
            patient = await PatientDAO.update(models.Patient.id==patient_id, obj_in=patient_in)
            logger.info(f"Updated patient data: {patient}")
            
            return patient
        
        except Exception as e:
            log_error_with_method_info(e)
            
    @classmethod 
    async def delete_patient(cls, patient_id: uuid.UUID, user: User) -> dict:
        try:
            logger.info(f"Therapist {user.username} deletes patient {patient_id}")
            await PatientDAO.delete(models.Patient.id==patient_id)
            
            return {"message": f"Therapist {user.username} successfully deleted patient {patient_id}"}
        
        except Exception as e:
            log_error_with_method_info(e)
            
    @classmethod
    async def delete_all_patients(cls, user: User) -> dict:
        await PatientDAO.delete()
        return {"message": "success"}
