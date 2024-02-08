from datetime import date

from pydantic import BaseModel


class PatientBase(BaseModel):
  age: int
  birthday: date
  full_name: str
  living_place: str
  job_title: str
  diagnosis: str
  first_visit: date
  last_visit: date
  treatment: str
  inhabited_locality: str

class PatientCreate(PatientBase):
  pass


class PatientUpdate(BaseModel) :
  age: int | None = None 
  birthday: date | None = None 
  full_name: str | None = None 
  living_place: str | None = None 
  job_title: str | None = None 
  diagnosis: str | None = None 
  first_visit: date | None = None 
  last_visit: date| None = None 
  treatment: str | None = None 
  inhabited_locality: str | None = None 
