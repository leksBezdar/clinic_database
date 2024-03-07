from datetime import date
import uuid

from pydantic import BaseModel

  
class PatientRecordsBase(BaseModel):
  first_visit: str | None = None
  last_visit: str | None = None
  
  diagnosis: str | None = None
  treatment: str | None = None
  bp: str = "Нет"
  ischemia: str = "Нет"
  dep: str = "Нет"
  
  patient_id: uuid.UUID
  
class PatientRecordsCreate(PatientRecordsBase):
  pass

class PatientRecordsCreateDB(PatientRecordsBase):
  therapist_id: uuid.UUID

class PatientRecords(PatientRecordsBase):
  id: uuid.UUID
  
  class Config:
    from_attributes = True

class PatientRecordsUpdate(BaseModel):
  first_visit: str | None = None
  last_visit: str | None = None
  
  diagnosis: str | None = None
  treatment: str | None = None
  bp: str | None = None
  ischemia: str | None = None
  dep: str | None = None
  

class ExplorerPatientDTO(BaseModel):
  id: int 
  therapist_id: uuid.UUID
  diagnosis: str | None = None
  treatment: str | None = None
  bp: str = "Нет"
  ischemia: str = "Нет"
  dep: str = "Нет"

  class Config:
    from_attributes = True
  