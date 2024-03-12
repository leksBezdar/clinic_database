import uuid
from loguru import logger
from sqlalchemy import and_

from . import schemas, models
from .dao import PatientRecordsDAO

from ..auth.models import User
from ..auth.schemas import UserRole
from ..patient.dao import PatientDAO
from ..patient.models import Patient


class PatientRecordsService:               
    
    @classmethod
    async def create_patient_record(cls, patient_record_data: schemas.PatientRecordsCreate, user: User) -> models.PatientRecord:
        try:
            logger.info(f"Therapist {user.username} creates a record about patient {patient_record_data.patient_id}")
            db_patient_record = await cls.__create_patient_record_db(patient_record_data)
            logger.info(f"Patient record: {db_patient_record}")
            return db_patient_record
            
        except Exception as e:
            logger.opt(exception=e).critical(f"Unexpected error in method PatientService.create_patient: {e}")

    @staticmethod
    async def __create_patient_record_db(patient_record_data: schemas.PatientRecordsCreate) -> models.PatientRecord:
        return await PatientRecordsDAO.add(
                schemas.PatientRecordsCreateDB(
                    **patient_record_data.model_dump(),
                ))           

    @classmethod        
    async def get_patient_records(cls, user: User, patient_id: uuid.UUID, offset: int, limit: int, **filter_by) -> list[models.PatientRecord]:
        try: 
            logger.info(f"User {user.username} with role {user.role} retrieves data about patient records {patient_id}")
            patient_records = await PatientRecordsDAO.find_all(
                models.PatientRecord.id==patient_id,
                offset=offset,
                limit=limit,
                **filter_by
            )

            return await cls.__format_patient_data(user=user, patient_records=patient_records)
        
        except Exception as e:
            logger.opt(exception=e).critical(f"Unexpected error in method PatientService.get_patient_records: {e}")
    
    @classmethod        
    async def get_one_patient_record(cls, user: User, patient_id: uuid.UUID, patient_record_id: uuid.UUID, **filter_by) -> models.PatientRecord:
        try: 
            logger.info(f"User {user.username} with role {user.role} retrieves data about patient record {patient_record_id}")
            patient_record = await PatientRecordsDAO.find_one_or_none(
                and_(
                    models.PatientRecord.patient_id==patient_id,
                    models.PatientRecord.id==patient_record_id
                    ),
                **filter_by
                ),
            if patient_record[0]: # BaseDAO.find_one_or_none returns tuple so we need to get the value from it
                list_patient_record = [] 
                list_patient_record.append(patient_record[0]) # __format_patient_data require list[PatientRecord]
                return await cls.__format_patient_data(user=user, patient_records=list_patient_record)
            return None
        
        except Exception as e:
            logger.opt(exception=e).critical(f"Unexpected error in method PatientService.get_one_patient_record: {e}")

    @classmethod
    async def get_all_patient_records(cls, *filter, user: User, offset: int, limit: int, **filter_by) -> list[models.PatientRecord]:
        try:
            logger.info(f"User {user.username} with role {user.role} retrieves all patient records")
            patient_records = await PatientRecordsDAO.find_all(*filter, offset=offset, limit=limit, **filter_by)
            formatted_patient_data = await cls.__format_patient_data(user=user, patient_records=patient_records)
            
            return formatted_patient_data
        
        except Exception as e:
            logger.opt(exception=e).critical(f"Unexpected error in method PatientService.get_all_patient_records: {e}")
            
                
    @classmethod
    async def get_all_patient_records_by_therapist(cls, *filter, user: User, offset: int, limit: int, **filter_by) -> list[models.PatientRecord]:
        try: 
            logger.info(f"Therapist {user.username} retrieves the list of all their patients")
            therapist_patients = await PatientRecordsDAO.find_all(*filter, offset=offset, limit=limit, **filter_by)
            return therapist_patients

        except Exception as e:
            logger.opt(exception=e).critical(f"Unexpected error in method PatientService.get_all_patients_by_therapist: {e}")           
                

    @classmethod
    async def update_patient_record(cls, user: User, patient_record_id: int, patient_in: schemas.PatientRecordsUpdate) -> models.PatientRecord:
        try:
            logger.info(f"Therapist {user.username} updates patient record {patient_record_id}")
            patient_record = await PatientRecordsDAO.update(models.PatientRecord.id==patient_record_id, obj_in=patient_in)
            logger.info(f"Updated patient record: {patient_record}")
            
            return patient_record      
        
        except Exception as e:
            logger.opt(exception=e).critical(f"Unexpected error in method PatientService.update_patient_record: {e}")

    @classmethod
    async def delete_patient_record(cls, user: User, patient_record_id: int) -> dict:
        try:
            logger.info(f"Therapist {user.username} deletes patient record {patient_record_id}")
            
            await PatientRecordsDAO.delete(models.PatientRecord.id==patient_record_id)
            status_message = f"Therapist {user.username} successfully deleted patient record {patient_record_id}"
            logger.info(status_message)
            
            return {"Message": status_message}
            
        except Exception as e:
            logger.opt(exception=e).critical(f"Unexpected error in method PatientService.delete_patient_record: {e}")

    @classmethod
    async def __format_patient_data(cls, user: User, patient_records: list[models.PatientRecord]) -> list:
        try:        
            if user.role == UserRole.therapist.value:
                return patient_records
            elif user.role == UserRole.explorer.value:
                logger.info(f"Formatting data for user {user.username} with role {user.role}")
                return await cls.__format_patient_data_for_explorer(patient_records)
            
            else: 
                logger.opt().critical(f"Unexpected user role {user.username}: {user.role}")
                raise ValueError
        
        except Exception as e:
            logger.opt(exception=e).critical(f"Unexpected error in method PatientService.__format_patient_data method: {e}")

    @classmethod
    async def __format_patient_data_for_explorer(cls, patient_records: list[models.PatientRecord]) -> list:
        try: 
            formatted_patient_records = []

            for patient_record in patient_records:
                patient_record = schemas.PatientRecords(**patient_record.__dict__)                       
                formatted_record = await cls.__get_data_into_explorer_dto_scheme(patient_record=patient_record)
                
                if len(patient_records) == 1:
                    return formatted_record

                formatted_patient_records.append(formatted_record)
                
            logger.info(f"Returning formatted data for user with explorer role")        
            return formatted_patient_records
        
        except Exception as e:
            logger.opt(exception=e).critical(f"Unexpected error in method PatientService.__format_patient_data_for_explorer method: {e}")
            
    @staticmethod
    async def __get_data_into_explorer_dto_scheme(patient_record: schemas.PatientRecords) -> schemas.ExplorerPatientDTO:
        patient = await PatientDAO.find_one_or_none(Patient.id==patient_record.patient_id)
        patient_data = patient_record.model_dump()
        
        patient_data.update({
        "bp": patient.bp,
        "ishcemia": patient.ischemia,
        "dep": patient.dep,
        "birthday": patient.birthday,
        "gender": patient.gender,
        "inhabited_locality": patient.inhabited_locality
        })
        
        return schemas.ExplorerPatientDTO(**patient_data)