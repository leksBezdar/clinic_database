import uuid

from pydantic import BaseModel


class PatientRecordsBase(BaseModel):
    visit: str | None = None

    diagnosis: str | None = None
    treatment: str | None = None

    patient_id: uuid.UUID | str


class PatientRecordsCreate(PatientRecordsBase):
    pass


class PatientRecordsCreateDB(PatientRecordsBase):
    pass


class PatientRecords(PatientRecordsBase):
    id: uuid.UUID

    class Config:
        from_attributes = True


class PatientRecordsUpdate(BaseModel):
    visit: str | None = None

    diagnosis: str | None = None
    treatment: str | None = None


class ExplorerPatientDTO(BaseModel):
    birthday: str
    gender: str
    inhabited_locality: str | None = None
    diagnosis: str | None = None
    treatment: str | None = None
    bp: bool = False
    ischemia: bool = False
    dep: bool = False

    class Config:
        from_attributes = True
