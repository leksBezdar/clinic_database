import uuid

from loguru import logger
from sqlalchemy import and_

from ..auth.models import User
from ..auth.schemas import UserRole
from ..patient.dao import PatientDAO
from ..patient.models import Patient
from ..utils import log_error_with_method_info
from . import models, schemas
from .dao import PatientRecordsDAO


class PatientRecordsService:

    @classmethod
    async def create_patient_record(
        cls, patient_record_data: schemas.PatientRecordsCreate, user: User
    ) -> models.PatientRecord:
        try:
            logger.info(
                f"Терапевт {user.username} создает запись о пациенте {patient_record_data.patient_id}"
            )
            db_patient_record = await cls.__create_patient_record_db(patient_record_data)
            logger.info(f"Запись о пациенте: {db_patient_record}")
            return db_patient_record

        except Exception as e:
            log_error_with_method_info(e)

    @staticmethod
    async def __create_patient_record_db(
        patient_record_data: schemas.PatientRecordsCreate,
    ) -> models.PatientRecord:
        return await PatientRecordsDAO.add(
            schemas.PatientRecordsCreateDB(
                **patient_record_data.model_dump(),
            )
        )

    @classmethod
    async def get_patient_records(
        cls, user: User, patient_id: uuid.UUID, offset: int, limit: int, **filter_by
    ) -> list[models.PatientRecord]:
        try:
            logger.info(
                f"Пользователь {user.username} с ролью {user.role} получает данные о записях пациента {patient_id}"
            )
            patient_records = await PatientRecordsDAO.find_all(
                models.PatientRecord.patient_id == patient_id, offset=offset, limit=limit, **filter_by
            )

            return await cls.__format_patient_data(user=user, patient_records=patient_records)

        except Exception as e:
            log_error_with_method_info(e)

    @classmethod
    async def get_one_patient_record(
        cls, user: User, patient_id: uuid.UUID, patient_record_id: uuid.UUID, **filter_by
    ) -> models.PatientRecord | None:
        try:
            logger.info(
                f"Пользователь {user.username} с ролью {user.role} получает данные о записи пациента {patient_record_id}"
            )
            patient_record = (
                await PatientRecordsDAO.find_one_or_none(
                    and_(
                        models.PatientRecord.patient_id == patient_id,
                        models.PatientRecord.id == patient_record_id,
                    ),
                    **filter_by,
                ),
            )
            if patient_record[
                0
            ]:  # BaseDAO.find_one_or_none возвращает кортеж, поэтому нужно достать значение # noqa
                list_patient_record = []
                list_patient_record.append(
                    patient_record[0]
                )  # __format_patient_data трубует список с типом list[PatientRecord] # noqa
                return await cls.__format_patient_data(user=user, patient_records=list_patient_record)
            return {"Message": "Запись не найдена"}

        except Exception as e:
            log_error_with_method_info(e)

    @classmethod
    async def get_all_patient_records(
        cls, *filter, user: User, offset: int, limit: int, **filter_by
    ) -> list[models.PatientRecord]:
        try:
            logger.info(f"Пользователь {user.username} с ролью {user.role} получает все записи пациентов")
            patient_records = await PatientRecordsDAO.find_all(
                *filter, offset=offset, limit=limit, **filter_by
            )
            formatted_patient_data = await cls.__format_patient_data(
                user=user, patient_records=patient_records
            )

            return formatted_patient_data

        except Exception as e:
            log_error_with_method_info(e)

    @classmethod
    async def get_all_patient_records_by_therapist(
        cls, *filter, user: User, offset: int, limit: int, **filter_by
    ) -> list[models.PatientRecord]:
        try:
            logger.info(f"Терапевт {user.username} получает список всех своих пациентов")
            patients = await PatientDAO.find_all(*filter, **filter_by)

            patient_records = []

            patient_ids = [patient.id for patient in patients]

            patient_records = await PatientRecordsDAO.find_all()
            for patient_record in patient_records:
                if patient_record.patient_id in patient_ids:

                    if len(patient_records) >= limit:
                        return patient_records

                    patient_records.append(patient_record)
            return patient_records

        except Exception as e:
            log_error_with_method_info(e)

    @classmethod
    async def update_patient_record(
        cls, user: User, patient_record_id: int, patient_in: schemas.PatientRecordsUpdate
    ) -> models.PatientRecord:
        try:
            logger.info(f"Терапевт {user.username} обновляет запись пациента {patient_record_id}")
            patient_record = await PatientRecordsDAO.update(
                models.PatientRecord.id == patient_record_id, obj_in=patient_in
            )
            logger.info(f"Обновленная запись пациента: {patient_record}")

            return patient_record

        except Exception as e:
            log_error_with_method_info(e)

    @classmethod
    async def delete_patient_record(cls, user: User, patient_record_id: int) -> dict:
        try:
            logger.info(f"Терапевт {user.username} удаляет запись пациента {patient_record_id}")

            await PatientRecordsDAO.delete(models.PatientRecord.id == patient_record_id)
            status_message = f"Терапевт {user.username} успешно удалил запись пациента {patient_record_id}"
            logger.info(status_message)

            return {"Message": status_message}

        except Exception as e:
            log_error_with_method_info(e)

    @classmethod
    async def delete_all_patient_records(cls, superuser: User) -> dict:
        await PatientRecordsDAO.delete()
        return {"message": "успех"}

    @classmethod
    async def __format_patient_data(cls, user: User, patient_records: list[models.PatientRecord]) -> list:
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
    async def __format_patient_data_for_explorer(cls, patient_records: list[models.PatientRecord]) -> list:
        try:
            formatted_patient_records = []

            for patient_record in patient_records:
                patient_record = schemas.PatientRecords(**patient_record.__dict__)
                formatted_record = await cls.__get_data_into_explorer_dto_scheme(
                    patient_record=patient_record
                )

                if len(patient_records) == 1:
                    return formatted_record

                formatted_patient_records.append(formatted_record)

            logger.info("Возвращение отформатированных данных для пользователя с ролью исследователь")
            return formatted_patient_records

        except Exception as e:
            log_error_with_method_info(e)

    @staticmethod
    async def __get_data_into_explorer_dto_scheme(
        patient_record: schemas.PatientRecords,
    ) -> schemas.ExplorerPatientDTO:
        try:
            patient = await PatientDAO.find_one_or_none(Patient.id == patient_record.patient_id)
            patient_data = patient_record.model_dump()

            patient_data.update(
                {
                    "bp": patient.bp,
                    "ishcemia": patient.ischemia,
                    "dep": patient.dep,
                    "birthday": patient.birthday,
                    "gender": patient.gender,
                    "inhabited_locality": patient.inhabited_locality,
                }
            )

            return schemas.ExplorerPatientDTO(**patient_data)

        except Exception as e:
            log_error_with_method_info(e)
