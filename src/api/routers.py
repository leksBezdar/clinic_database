import uuid
from fastapi import APIRouter, Depends

from . import schemas
from .service import PatientManager
from ..auth.dependencies import get_current_superuser, get_current_user
from ..auth.models import User

router = APIRouter()


@router.post("/create_patient_record", response_model=schemas.Patient)
async def create_patient_record(
  	patient_data: schemas.PatientCreate,
	user: User = Depends(get_current_user)
):
    patient_manager = PatientManager()
    patient_crud = patient_manager.patient_crud

    return await patient_crud.create_patient(patient_data=patient_data, user=user)

@router.get("/get_patient_records", response_model=list[schemas.Patient])
async def get_patient_records(
    patient_id: int,
    limit: int = 100,
    offset: int = 0,
	user: User = Depends(get_current_user)
):
    patient_manager = PatientManager()
    patient_crud = patient_manager.patient_crud

    return await patient_crud.get_patient_records(
        patient_id=patient_id, user=user,
        limit=limit, offset=offset)
    
@router.get("/get_all_patient_records", response_model=list[schemas.Patient])
async def get_all_patient_records(
	user: User = Depends(get_current_user), 
    limit: int = 1000,
    offset: int = 0,
):
    patient_manager = PatientManager()
    patient_crud = patient_manager.patient_crud

    return await patient_crud.get_all_patient_records(limit=limit, offset=offset, user=user)

@router.patch("/update_patient_record", response_model=schemas.Patient)
async def update_patient_record(
    patient_id: int, 
    patient_data: schemas.PatientUpdate,
	user: User = Depends(get_current_user)
):
    patient_manager = PatientManager()
    patient_crud = patient_manager.patient_crud

    return await patient_crud.update_patient_record(user=user, patient_in=patient_data, patient_id=patient_id)

@router.delete("/delete_patient_record")
async def delete_patient_record(
    patient_id: int,
	user: User = Depends(get_current_user),
):  
    patient_manager = PatientManager()
    patient_crud = patient_manager.patient_crud

    return await patient_crud.delete_patient_record(user=user, patient_id=patient_id)
