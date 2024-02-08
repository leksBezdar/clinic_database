from fastapi import APIRouter
from . import models, schemas
from .service import PatientManager

router = APIRouter()


@router.post("/create_patient_record", response_model=schemas.PatientCreate)
async def create_patient_record(
  patient_data: schemas.PatientCreate
):

  patient_manager = PatientManager()
  patient_crud = patient_manager.patient_crud

  return await patient_crud.create_patient(patient_data=patient_data)
  