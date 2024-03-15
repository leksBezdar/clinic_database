import uuid
from loguru import logger

from ..auth.schemas import UserRole

from . import schemas, models
from .dao import PatientDAO

from ..auth.models import User

from ..utils import log_error_with_method_info


class PatientService:
    
    @classmethod
    async def create_patient(cls, patient_data: schemas.PatientCreate, user: User) -> models.Patient:
        try: 
            logger.info(f"Терапевт {user.username} создает пациента {patient_data.full_name}")
            db_patient = await PatientDAO.add(
                schemas.PatientCreateDB(
                    **patient_data.model_dump(),
                    therapist_id=user.id,
                ))
            
            logger.info(f"Пациент: {db_patient}")
            return db_patient
            
        except Exception as e:
            log_error_with_method_info(e)
            
    @classmethod
    async def get_patient(cls, patient_id: uuid.UUID, user: User) -> models.Patient:
        try:
            patient = await PatientDAO.find_one_or_none(models.Patient.id==patient_id)
            logger.info(f"Терапевт {user.username} получает данные пациента {patient.full_name}")
            return patient or {"message": "Пациент не найден"}
        
        except Exception as e:
            log_error_with_method_info(e)

    @classmethod
    async def get_all_patients(cls, *filter, user: User, offset: int, limit: int, **filter_by) -> list[models.Patient]:
        try:
            logger.info(f"Терапевт {user.username} получает список всех пациентов")
            patients = await PatientDAO.find_all(
                *filter, offset=offset, limit=limit, **filter_by
            )
            formatted_patients = await cls.__format_patient_data(user=user, patient_records=patients)
            return formatted_patients or []
        
        except Exception as e:
            log_error_with_method_info(e)

    @classmethod
    async def get_all_patients_by_therapist(cls, *filter, user: User, offset: int, limit: int, **filter_by) -> list[models.Patient]:
        try:
            logger.info(f"Терапевт {user.username} получает список всех пациентов")
            patients = await PatientDAO.find_all(
                *filter, offset=offset, limit=limit, **filter_by
            )

            return patients or []
        
        except Exception as e:
            log_error_with_method_info(e)
            
    
    @classmethod
    async def update_patient(cls, patient_id: uuid.UUID, user: User, patient_in: schemas.PatientUpdate) -> models.Patient:
        try:
            logger.info(f"Терапевт {user.username} изменяет данные пациента {patient_id}")
            patient = await PatientDAO.update(models.Patient.id==patient_id, obj_in=patient_in)
            logger.info(f"Обновленные данные пациента: {patient}")
            
            return patient
        
        except Exception as e:
            log_error_with_method_info(e)
            
    @classmethod 
    async def delete_patient(cls, patient_id: uuid.UUID, user: User) -> dict:
        try:
            logger.info(f"Терапевт {user.username} удаляет пациента {patient_id}")
            await PatientDAO.delete(models.Patient.id==patient_id)
            
            return {"message": f"Терапевт {user.username} успешно удалил пациента {patient_id}"}
        
        except Exception as e:
            log_error_with_method_info(e)
            
    @classmethod
    async def delete_all_patients(cls, user: User) -> dict:
        await PatientDAO.delete()
        return {"message": "успех"}
    
    
    @classmethod
    async def __format_patient_data(cls, user: User, patient_records: list[models.Patient]) -> list:
        try:        
            if user.role == UserRole.therapist.value:
                return patient_records
            elif user.role == UserRole.explorer.value:
                logger.info(f"Форматирование данных для пользователя {user.username} с ролью {user.role}")
                return await cls.__format_patient_data_for_explorer(patient_records)
            
            else: 
                logger.opt().critical(f"Неожиданная роль пользователя {user.username}: {user.role}")
                raise ValueError
        
        except Exception as e:
            log_error_with_method_info(e)

    @classmethod
    async def __format_patient_data_for_explorer(cls, patient_records: list[models.Patient]) -> list:
        try: 
            formatted_patient_records = []

            for patient_record in patient_records:
                patient_record = schemas.Patient(**patient_record.__dict__)                       
                formatted_record = await cls.__get_data_into_explorer_dto_scheme(patient_record=patient_record)
                
                if len(patient_records) == 1:
                    return formatted_record

                formatted_patient_records.append(formatted_record)
                
            logger.info(f"Возвращение отформатированных данных для пользователя с ролью исследователя")        
            return formatted_patient_records
        
        except Exception as e:
            log_error_with_method_info(e)
            
    @staticmethod
    async def __get_data_into_explorer_dto_scheme(patient_record: schemas.Patient) -> schemas.ExplorerPatientDTO:
        try:
            
            patient_record = patient_record.model_dump()
            
            return schemas.ExplorerPatientDTO(**patient_record)
        
        except Exception as e:
            log_error_with_method_info(e)
