from datetime import date

from pydantic import BaseModel


class PatientBase(BaseModel):
  age: int
  birthday: str | None = None
  gender: str
  full_name: str
  living_place: str | None = None
  job_title: str | None = None
  inhabited_locality: str | None = None
  diagnosis: str | None = None
  first_visit: str | None = None
  last_visit: str | None = None
  treatment: str | None = None
  bp: str = "Нет"
  ischemia: str = "Нет"
  dep: str = "Нет"


class PatientCreate(PatientBase):
  pass

class PatientCreateDB(PatientCreate):
  therapist_id: str

class PatientUpdate(BaseModel):
  age: int | None = None 
  birthday: str | None = None 
  full_name: str | None = None 
  gender: str | None = None
  living_place: str | None = None 
  job_title: str | None = None 
  inhabited_locality: str | None = None 
  diagnosis: str | None = None
  first_visit: str | None = None
  last_visit: str | None = None
  treatment: str | None = None
  bp: str | None = None
  ischemia: str | None = None
  dep: str | None = None
  
class Patient(PatientBase):
  id: int
  therapist_id: str
  bp: str
  ischemia: str
  dep: str
