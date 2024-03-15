import uuid

from pydantic import BaseModel


class PatientBase(BaseModel):
  full_name: str
  birthday: str | None = None
  gender: str
  job_title: str | None = None
  living_place: str | None = None
  inhabited_locality: str | None = None

  bp: str = "Нет"
  ischemia: str = "Нет"
  dep: str = "Нет"

class PatientCreate(PatientBase):
  pass

class PatientCreateDB(PatientBase):
  therapist_id: uuid.UUID | str

class PatientUpdate(BaseModel):
  full_name: str | None = None 
  birthday: str | None = None 
  gender: str | None = None
  job_title: str | None = None 
  living_place: str | None = None 
  inhabited_locality: str | None = None 

  bp: str | None = None
  ischemia: str | None = None
  dep: str | None = None
  
class Patient(PatientBase):
  id: uuid.UUID
  therapist_id: uuid.UUID
  
  class Config:
    from_attributes = True
  
  
class ExplorerPatientDTO(BaseModel):
  birthday: str
  gender: str
  inhabited_locality: str | None = None
  bp: str = "Нет"
  ischemia: str = "Нет"
  dep: str = "Нет"

  class Config:
    from_attributes = True