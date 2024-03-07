import uuid
from loguru import logger

from . import schemas, models
from .dao import PatientDAO

from ..auth.models import User


class PatientService:
    
    @classmethod
    async def create_patient(cls, patient_data: schemas.PatientCreate, user: User) -> models.Patient:
        try: 
            logger.info(f"Теравепт {user.username} создает пациента {patient_data.full_name}")
            db_patient = await PatientDAO.add(
                schemas.PatientCreate(
                    **patient_data.model_dump(),
                ))
            
            logger.info(f"Пациент: {db_patient}")
            return db_patient
            
        except Exception as e:
            logger.opt(exception=e).critical(f"Непредвиденная ошибка в методе PatientService.create_patient: {e}")
            
    @classmethod
    async def get_patient(cls, patient_id: uuid.UUID, user: User) -> models.Patient:
        try:
            patient = await PatientDAO.find_one_or_none(models.Patient.id==patient_id)
            logger.info(f"Терапевт {user.username} получает данные пациента {patient.full_name}")
            return patient
        
        except Exception as e:
            logger.opt(exception=e).critical(f"Непредвиденная ошибка в методе PatientService.get_patient: {e}")

    @classmethod
    async def get_all_patients(cls, *filter, user: User, offset: int, limit: int, **filter_by) -> list[models.Patient]:
        try:
            logger.info(f"Теравепт {user.username} получает список всех пациентов")
            patients = await PatientDAO.find_all(
                *filter, offset=offset, limit=limit, **filter_by
            )

            return patients
        
        except Exception as e:
            logger.opt(exception=e).critical(f"Непредвиденная ошибка в методе PatientService.get_all_patients: {e}")
            
    
    @classmethod
    async def update_patient(cls, patient_id: uuid.UUID, user: User, patient_in: schemas.PatientUpdate) -> models.Patient:
        try:
            logger.info(f"Терапевт {user.username} изменяет данные пациента {patient_id}")
            patient = await PatientDAO.update(models.Patient.id==patient_id, obj_in=patient_in)
            logger.info(f"Новые данные пациента: {patient}")
            
            return patient
        
        except Exception as e:
            logger.opt(exception=e).critical(f"Непредвиденная ошибка в методе PatientService.update_patient: {e}")
            
    @classmethod 
    async def delete_patient(cls, patient_id: uuid.UUID, user: User) -> dict:
        try:
            logger.info(f"Терапевт {user.username} удаляет пациента {patient_id}")
            await PatientDAO.delete(models.Patient.id==patient_id)
            
            return {"message": f"Терапевт {user.username} удалил пациента {patient_id} успешно"}
        
        except Exception as e:
            logger.opt(exception=e).critical(f"Непредвиденная ошибка в методе PatientService.delete_patient: {e}")

            