from . import schemas, models
from .dao import PatientDAO


class PatientCRUD:

  async def create_patient(self, patient_data: schemas.PatientCreate) -> models.Patient:

    db_patient = await PatientDAO.add(
        schemas.PatientCreate(
            **patient_data.model_dump(),
        ))

    return db_patient


class PatientManager:
  def __init__(self):
    self.patient_crud = PatientCRUD()
