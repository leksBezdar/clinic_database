import uuid
from datetime import date
from enum import Enum

from pydantic import BaseModel, validator


class PatientBase(BaseModel):
    full_name: str
    birthday: date | None = None
    gender: str
    job_title: str | None = None
    living_place: str | None = None
    inhabited_locality: str | None = None

    bp: bool = False
    ischemia: bool = False
    dep: bool = False


class PatientCreate(PatientBase):
    pass


class PatientCreateDB(PatientBase):
    therapist_id: uuid.UUID | str


class PatientUpdate(BaseModel):
    full_name: str | None = None
    birthday: date | None = None
    gender: str | None = None
    job_title: str | None = None
    living_place: str | None = None
    inhabited_locality: str | None = None

    bp: bool | None = None
    ischemia: bool | None = None
    dep: bool | None = None


class Patient(PatientBase):
    id: uuid.UUID
    therapist_id: uuid.UUID

    class Config:
        from_attributes = True


class ExplorerPatientDTO(BaseModel):
    birthday: date
    gender: str
    inhabited_locality: str | None = None
    bp: bool = "Нет"
    ischemia: bool = "Нет"
    dep: bool = "Нет"

    class Config:
        from_attributes = True


class GetFilters(BaseModel):
    field: str
    rule: str
    value: str


class Order(Enum):
    ASC = "asc"
    DESC = "desc"


class GetSorting(BaseModel):
    field: str
    order: Order

    @validator("field")
    def validate_sorting(cls, field_value):
        if field_value not in PatientBase.__annotations__.keys():
            raise ValueError(f"Sorting field '{field_value}' is not a valid field")
        return field_value


class StringFilter(Enum):
    EQUALS = "equals"
    CONTAINS = "contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    NOT_EQUALS = "not_equals"
    NOT_CONTAINS = "not_contains"


class IntegerFilter(Enum):
    EQUALS = "equals"
    LESS_THAN_OR_EQUAL = "less_than_or_equal"
    GREATER_THAN_OR_EQUAL = "greater_than_or_equal"
    LESS_THAN = "less_than"
    GREATER_THAN = "greater_than"
    NOT_EQUALS = "not_equals"


class DatetimeFilter(Enum):
    EQUALS = "equals"
    LESS_THAN_OR_EQUAL = "less_than_or_equal"
    GREATER_THAN_OR_EQUAL = "greater_than_or_equal"
    LESS_THAN = "less_than"
    GREATER_THAN = "greater_than"
    NOT_EQUALS = "not_equals"


class BooleanFilter(Enum):
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"


class GlobalRule(Enum):
    SOME = "some"
    EVERY = "every"


class PatientStatictic(BaseModel):
    bp: int
    dep: int
    ischemia: int
    city: int
    district: int
    male: int
    female: int


class GetAllPatientsOut(BaseModel):
    patients: list[Patient] | list[ExplorerPatientDTO]
    statistic: PatientStatictic
