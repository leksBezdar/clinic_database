import uuid

from pydantic import BaseModel


class PatientBase(BaseModel):
    full_name: str
    birthday: str | None = None
    gender: str
    job_title: str | None = None
    living_place: str | None = None
    inhabited_locality: str | None = None

    bp: bool = False
    ischemia: bool = False
    dep: bool = False


class PatientRecordsBase(BaseModel):
    visit: str | None = None
    diagnosis: str | None = None
    treatment: str | None = None
    patient_id: uuid.UUID | str
