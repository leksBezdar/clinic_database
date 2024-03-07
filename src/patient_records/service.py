import uuid
from loguru import logger
from sqlalchemy import and_

from . import schemas, models, exceptions
from .dao import PatientRecordsDAO

from ..auth.models import User
from ..auth.schemas import UserRole


class PatientRecordsService:               
    
    @classmethod
    async def create_patient_record(cls, patient_record_data: schemas.PatientRecordsCreate, user: User) -> models.PatientRecord:
        try:
            if user.role == UserRole.therapist.value:
                logger.info(f"Терапевт {user.username} создает запись о пациенте {patient_record_data.patient_id}")
                db_patient_record = await PatientRecordsDAO.add(
                    schemas.PatientRecordsCreateDB(
                        therapist_id=user.id,
                        **patient_record_data.model_dump(),
                    ))
                
                logger.info(f"Запись о пациенте: {db_patient_record}")
                return db_patient_record
            
            raise exceptions.Forbidden
        
        except Exception as e:
            logger.opt(exception=e).critical(f"Непредвиденная ошибка в методе PatientService.create_patient: {e}")

    @classmethod        
    async def get_patient_records(cls, user: User, patient_id: uuid.UUID, offset: int, limit: int, **filter_by) -> list[models.PatientRecord]:
        try: 
            logger.info(f"Пользователь {user.username} с ролью {user.role} получает данные о записях пациента {patient_id}")
            patient_records = await PatientRecordsDAO.find_all(
                models.PatientRecord.patient_id==patient_id,
                offset=offset,
                limit=limit
            )   

            return await cls.__format_patient_data(user=user, patient_records=patient_records)
        
        except Exception as e:
            logger.opt(exception=e).critical(f"Непредвиденная ошибка в методе PatientService.get_patient_records: {e}")
    
    @classmethod        
    async def get_one_patient_record(cls, user: User, patient_record_id: uuid.UUID, **filter_by) -> models.PatientRecord:
        try: 
            logger.info(f"Пользователь {user.username} с ролью {user.role} получает данные о записе пациента {patient_record_id}")
            patient_record = await PatientRecordsDAO.find_one_or_none(
                and_(
                    models.PatientRecord.patient_id==patient_record_id,
                    models.PatientRecord.id==patient_record_id
                    )
                )
            if patient_record:
                return await cls.__format_patient_data(user=user, patient_records=list(patient_record))
            return None
        
        except Exception as e:
            logger.opt(exception=e).critical(f"Непредвиденная ошибка в методе PatientService.get_one_patient_record: {e}")

    @classmethod
    async def get_all_patient_records(cls, *filter, user: User, offset: int, limit: int, **filter_by) -> list[models.PatientRecord]:
        try:
            logger.info(f"Пользователь {user.username} с ролью {user.role} получает все записи о пациентах")
            patient_records = await PatientRecordsDAO.find_all(*filter, offset=offset, limit=limit, **filter_by)
            formatted_patient_data = await cls.__format_patient_data(user=user, patient_records=patient_records)
            
            return formatted_patient_data
        
        except Exception as e:
            logger.opt(exception=e).critical(f"Непредвиденная ошибка в методе PatientService.get_all_patient_records: {e}")
            
                
    @classmethod
    async def get_all_patient_records_by_therapist(cls, *filter, user: User, offset: int, limit: int, **filter_by) -> list[models.PatientRecord]:
        try: 
            logger.info(f"Терапев {user.username} получает список всех своих пациентов")
            therapist_patients = await PatientRecordsDAO.find_all(
                *filter, offset=offset, limit=limit, **filter_by
            )
            
            return therapist_patients
        
        except Exception as e:
            logger.opt(exception=e).critical(f"Непредвиденная ошибка в методе PatientService.get_all_patients_by_therapist: {e}")           
                

    @classmethod
    async def update_patient_record(cls, user: User, patient_record_id: int, patient_in: schemas.PatientRecordsUpdate) -> models.PatientRecord:
        try:
            if user.role == UserRole.therapist.value:  
                logger.info(f"Терапевт {user.username} обновляет запись пациента {patient_record_id}")
                patient_record = await PatientRecordsDAO.update(models.PatientRecord.id==patient_record_id, obj_in=patient_in)
                logger.info(f"Обновленная запись пациента: {patient_record}")
                return patient_record
            
            raise exceptions.Forbidden
        
        except Exception as e:
            logger.opt(exception=e).critical(f"Непредвиденная ошибка в методе PatientService.update_patient_record: {e}")

    @classmethod
    async def delete_patient_record(cls, user: User, patient_record_id: int) -> dict:
        try:
            logger.info(f"Терапевт {user.username} удаляет запись пациента {patient_record_id}")
            if user.role == UserRole.therapist.value: 
                await PatientRecordsDAO.delete(models.PatientRecord.id==patient_record_id)
                status_message = f"Терапевт {user.username} удалил запись пациента {patient_record_id} успешно"
                logger.info(status_message)
                return {"Message": status_message}
            
            raise exceptions.Forbidden
        
        except Exception as e:
            logger.opt(exception=e).critical(f"Непредвиденная ошибка в методе PatientService.delete_patient_record: {e}")

    @classmethod
    async def __format_patient_data(cls, user: User, patient_records: list[models.PatientRecord]) -> list:
        try:
            logger.info(f"Форматирование данных для пользователя {user.username} с ролью {user.role}")
            if user.role == UserRole.therapist.value:
                return patient_records
            elif user.role == UserRole.therapist.value                                                    :
                return await cls.__format_patient_data_for_explorer(patient_records)
            
            else: 
                logger.opt().critical(f"Непредвиденная роль пользователя {user.username}: {user.role}")
                raise ValueError
        
        except Exception as e:
            logger.opt(exception=e).critical(f"Непредвиденная ошибка в методе PatientService.__format_patient_data method: {e}")

    @staticmethod
    async def __format_patient_data_for_explorer(patient_records: list[models.PatientRecord]) -> list:
        try:
            
            formatted_patient_records = []
        
            for patient in patient_records:
                patient_dict = patient.__dict__
        
                patient_data = {
                    "id": patient_dict.get("id"),
                    "therapist_id": patient_dict.get("therapist_id"),
                    "diagnosis": patient_dict.get("diagnosis"),
                    "treatment": patient_dict.get("treatment"),
                    "bp": patient_dict.get("bp"),
                    "ischemia": patient_dict.get("ischemia"),
                    "dep": patient_dict.get("dep")
                }
        
                formatted_patient_records.append(schemas.ExplorerPatientDTO(**patient_data))
            
            logger.info(f"Возвращение измененных данных для пользователя с ролью исследователь")    
                
            return formatted_patient_records
        
        except Exception as e:
            logger.opt(exception=e).critical(f"Непредвиденная ошибка в методе PatientService.__format_patient_data_for_explorer method: {e}")
