import datetime
import typing
import uuid
from operator import not_
from types import NoneType

from fastapi import HTTPException
from loguru import logger
from sqlalchemy import BinaryExpression, ColumnElement, and_, asc, desc, or_, select

from ..auth.models import User
from ..auth.schemas import UserRole
from ..database import async_session_maker
from ..utils import log_error_with_method_info
from . import models, schemas
from .dao import PatientDAO


class FilterRules:
    VALID_FIELDS: list[str] = []
    VALID_RULES: dict[str, list[str]] = {}

    @classmethod
    def _initialize(cls) -> None:
        if not cls.VALID_FIELDS or not cls.VALID_RULES:
            cls.VALID_FIELDS = cls.__get_valid_fields()
            cls.VALID_RULES = cls.__get_valid_rules()

    @classmethod
    def __get_valid_fields(cls, model: schemas.PatientBase = schemas.PatientBase) -> list[str]:
        return list(model.model_fields.keys())

    @classmethod
    def __get_valid_rules(cls, model: schemas.PatientBase = schemas.PatientBase) -> dict[str, list[str]]:
        valid_rules: dict[str, list[str]] = {}
        for field, field_type in model.__annotations__.items():
            if not isinstance(field_type, type):
                args = typing.get_args(field_type)
                for arg in args:
                    if arg is not NoneType:
                        if arg is issubclass(arg, datetime.date):
                            field_type = datetime.date
                            break
                        field_type = arg
                        break
            valid_rules[field] = cls._get_valid_rules_for_field(field_type)
        return valid_rules

    @staticmethod
    def _get_valid_rules_for_field(field_type: type) -> list[str]:
        if issubclass(field_type, bool):
            return [f.value for f in schemas.BooleanFilter]
        if issubclass(field_type, str):
            return [f.value for f in schemas.StringFilter]
        if issubclass(field_type, datetime.date):
            return [f.value for f in schemas.DatetimeFilter]
        if issubclass(field_type, int):
            return [f.value for f in schemas.IntegerFilter]
        return []

    @classmethod
    def get_valid_rules_for_field(cls, field: str) -> list[str]:
        cls._initialize()
        return cls.VALID_RULES.get(field, [])

    @classmethod
    def get_valid_fields(cls) -> list[str]:
        cls._initialize()
        return cls.VALID_FIELDS

    @classmethod
    def get_valid_rules(cls) -> dict[str, list[str]]:
        cls._initialize()
        return cls.VALID_RULES


class FiltersBuilder:

    STRING_RULES_MAPPING = {
        schemas.StringFilter.CONTAINS.value: lambda field_attr, value: field_attr.ilike(f"%{value}%"),
        schemas.StringFilter.STARTS_WITH.value: lambda field_attr, value: field_attr.ilike(f"{value}%"),
        schemas.StringFilter.ENDS_WITH.value: lambda field_attr, value: field_attr.ilike(f"%{value}"),
        schemas.StringFilter.EQUALS.value: lambda field_attr, value: field_attr.ilike(value),
        schemas.StringFilter.NOT_CONTAINS.value: lambda field_attr, value: not_(
            field_attr.ilike(f"%{value}%")
        ),
        schemas.StringFilter.NOT_EQUALS.value: lambda field_attr, value: not_(field_attr.ilike(value)),
    }

    BOOLEAN_RULES_MAPPING = {
        schemas.BooleanFilter.EQUALS.value: lambda field_attr, value: field_attr == (value.lower() == "true"),
        schemas.BooleanFilter.NOT_EQUALS.value: lambda field_attr, value: field_attr
        != (value.lower() == "true"),
    }

    INTEGER_RULES_MAPPING = {
        schemas.IntegerFilter.EQUALS.value: lambda field_attr, value: field_attr == value,
        schemas.IntegerFilter.LESS_THAN_OR_EQUAL.value: lambda field_attr, value: field_attr <= value,
        schemas.IntegerFilter.GREATER_THAN_OR_EQUAL.value: lambda field_attr, value: field_attr >= value,
        schemas.IntegerFilter.LESS_THAN.value: lambda field_attr, value: field_attr < value,
        schemas.IntegerFilter.GREATER_THAN.value: lambda field_attr, value: field_attr > value,
        schemas.IntegerFilter.NOT_EQUALS.value: lambda field_attr, value: field_attr != value,
    }

    DATETIME_RULES_MAPPING = INTEGER_RULES_MAPPING

    GLOBAL_RULES_MAPPING = {
        schemas.GlobalRule.EVERY: lambda query_filters: select(models.Patient).filter(
            *query_filters.values()
        ),
        schemas.GlobalRule.SOME: lambda query_filters: select(models.Patient).filter(
            or_(*query_filters.values())
        ),
    }

    @classmethod
    async def apply_filters(
        cls, filters: list[schemas.GetFilters], global_rule: str
    ) -> list[BinaryExpression]:
        query_filters = await cls.build_query_filters(filters)
        if global_rule == schemas.GlobalRule.SOME:
            return or_(*query_filters.values())
        if global_rule == schemas.GlobalRule.EVERY:
            return and_(*query_filters.values())

        raise HTTPException(status_code=400, detail=("Please, use 'some' or 'every' global rules!"))

    @staticmethod
    async def remove_optional(field_type: type) -> type:
        args = typing.get_args(field_type)
        for arg in args:
            if arg is not NoneType:
                field_type = arg
                break
        return field_type

    @classmethod
    async def build_query_filters(cls, filters: list[schemas.GetFilters]) -> dict[str, BinaryExpression]:
        query_filters: dict[str, BinaryExpression] = {}
        VALID_FIELDS: list[str] = FilterRules.get_valid_fields()
        VALID_RULES: dict[str, list[str]] = FilterRules.get_valid_rules()
        for f in filters:
            field = f.field.lower()
            rule = f.rule.lower()

            if field not in VALID_FIELDS:
                raise ValueError(f"Invalid field: {field}")

            if rule not in VALID_RULES.get(field, []):
                raise ValueError(f"Invalid rule for {field} field.")

            field_type = schemas.PatientBase.__annotations__[field]
            field_type = await cls.remove_optional(field_type)
            value = f.value

            if field_type == datetime.date:
                try:
                    value = datetime.datetime.strptime(value, "%Y-%m-%d").date()
                except ValueError:
                    raise ValueError(f"Invalid value format for field {field}")

            field_attr: ColumnElement = getattr(models.Patient, field)
            rule_func = cls.get_rule_function(field_type, rule)
            query_filters[field] = rule_func(field_attr, value)

        return query_filters

    @classmethod
    def get_rule_function(cls, field_type: type, rule: str) -> dict:
        rule_mappings = {
            str: cls.STRING_RULES_MAPPING,
            bool: cls.BOOLEAN_RULES_MAPPING,
            int: cls.INTEGER_RULES_MAPPING,
            datetime.date: cls.DATETIME_RULES_MAPPING,
        }
        rule_mapping: dict = rule_mappings.get(field_type)
        if rule_mapping is None:
            raise NotImplementedError(f"Rule not implemented for field type {field_type}.")
        return rule_mapping.get(rule)


class PatientService:

    @classmethod
    async def create_patient(cls, patient_data: schemas.PatientCreate, user: User) -> models.Patient:
        try:
            logger.info(f"Терапевт {user.username} создает пациента {patient_data.full_name}")
            db_patient = await PatientDAO.add(
                schemas.PatientCreateDB(
                    **patient_data.model_dump(),
                    therapist_id=user.id,
                )
            )

            logger.info(f"Пациент: {db_patient}")
            return db_patient

        except Exception as e:
            log_error_with_method_info(e)

    @classmethod
    async def get_patient(cls, patient_id: uuid.UUID, user: User) -> models.Patient:
        try:
            patient = await PatientDAO.find_one_or_none(models.Patient.id == patient_id)
            if patient:
                logger.info(f"Терапевт {user.username} получает данные пациента {patient.full_name}")
                return patient
            return {"message": "Пациент не найден"}

        except Exception as e:
            log_error_with_method_info(e)

    @classmethod
    async def get_all_patients_by_therapist(
        cls, *filter, user: User, offset: int, limit: int, **filter_by
    ) -> list[models.Patient]:
        try:
            logger.info(f"Терапевт {user.username} получает список всех своих пациентов")
            patients = await PatientDAO.find_all(*filter, offset=offset, limit=limit, **filter_by)

            return patients or []

        except Exception as e:
            log_error_with_method_info(e)

    @classmethod
    async def get_all_patients(
        cls,
        user: User,
        offset: int,
        limit: int,
        global_rule: str,
        filters: list[schemas.GetFilters] = [],
        sorting_rules: list[schemas.GetSorting] = [],
    ) -> list[models.Patient]:
        async with async_session_maker() as session:
            query = select(models.Patient).offset(offset).limit(limit)

            if filters:
                query_filters = await FiltersBuilder.apply_filters(filters, global_rule)
                query = query.where(query_filters)

            if sorting_rules:
                for rule in sorting_rules:
                    if rule.order == schemas.Order.ASC:
                        query = query.order_by(asc(getattr(models.Patient, rule.field)))
                    elif rule.order == schemas.Order.DESC:
                        query = query.order_by(desc(getattr(models.Patient, rule.field)))

            result = await session.execute(query.offset(offset).limit(limit))
            patients = result.scalars().all()

            formatted_patients = await cls.__format_patient_data(user=user, patient_records=patients)

        return formatted_patients

    @classmethod
    async def update_patient(
        cls, patient_id: uuid.UUID, user: User, patient_in: schemas.PatientUpdate
    ) -> models.Patient:
        try:
            logger.info(f"Терапевт {user.username} изменяет данные пациента {patient_id}")
            patient = await PatientDAO.update(
                models.Patient.id == patient_id, models.Patient.therapist_id == user.id, obj_in=patient_in
            )
            logger.info(f"Обновленные данные пациента: {patient}")

            return patient

        except Exception as e:
            log_error_with_method_info(e)

    @classmethod
    async def delete_patient(cls, patient_id: uuid.UUID, user: User) -> dict:
        try:
            logger.info(f"Терапевт {user.username} удаляет пациента {patient_id}")
            await PatientDAO.delete(models.Patient.id == patient_id)

            return {"message": f"Терапевт {user.username} успешно удалил пациента {patient_id}"}

        except Exception as e:
            log_error_with_method_info(e)

    @classmethod
    async def delete_all_patients(cls, superuser: User) -> dict:
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
                formatted_record = await cls.__get_data_into_explorer_dto_scheme(
                    patient_record=patient_record
                )

                if len(patient_records) == 1:
                    return formatted_record

                formatted_patient_records.append(formatted_record)

            logger.info("Возвращение отформатированных данных для пользователя с ролью исследователя")
            return formatted_patient_records

        except Exception as e:
            log_error_with_method_info(e)

    @staticmethod
    async def __get_data_into_explorer_dto_scheme(
        patient_record: schemas.Patient,
    ) -> schemas.ExplorerPatientDTO:
        try:

            patient_record = patient_record.model_dump()

            return schemas.ExplorerPatientDTO(**patient_record)

        except Exception as e:
            log_error_with_method_info(e)
