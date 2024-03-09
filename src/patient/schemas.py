import uuid

from pydantic import BaseModel


class PatientBase(BaseModel):
  full_name: str
  birthday: str | None = None
  gender: str
  job_title: str | None = None
  living_place: str | None = None
  inhabited_locality: str | None = None

class PatientCreate(PatientBase):
  pass

class PatientUpdate(BaseModel):
  full_name: str | None = None 
  birthday: str | None = None 
  gender: str | None = None
  job_title: str | None = None 
  living_place: str | None = None 
  inhabited_locality: str | None = None 
  
class Patient(PatientBase):
  id: uuid.UUID
  
  class Config:
    from_attributes = True
  