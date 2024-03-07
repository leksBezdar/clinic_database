from datetime import date
import uuid

from pydantic import BaseModel


class PatientBase(BaseModel):
  birthday: str | None = None
  gender: str
  full_name: str
  living_place: str | None = None
  job_title: str | None = None
  inhabited_locality: str | None = None

class PatientCreate(PatientBase):
  pass

class PatientUpdate(BaseModel):
  birthday: str | None = None 
  full_name: str | None = None 
  gender: str | None = None
  living_place: str | None = None 
  job_title: str | None = None 
  inhabited_locality: str | None = None 
  
class Patient(PatientBase):
  id: uuid.UUID
  
  class Config:
    from_attributes = True
  