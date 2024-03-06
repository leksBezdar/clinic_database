from typing import Union
from fastapi import APIRouter, Depends

from . import schemas
from .service import PatientService
from ..auth.dependencies import get_current_user
from ..auth.models import User


api_router = APIRouter()


@api_router.post("/create_patient_record", response_model=schemas.Patient)
async def create_patient_record(
  	patient_data: schemas.PatientCreate,
	user: User = Depends(get_current_user)
):
    return await PatientService.create_patient(patient_data=patient_data, user=user)

# @api_router.get("/get_patient_records", response_model=list[schemas.Patient])
# async def get_patient_records(
#     patient_id: int,
#     limit: int = 100,
#     offset: int = 0,
# 	user: User = Depends(get_current_user)
# ):
#     return await PatientService.get_patient_records(patient_id=patient_id, user=user, limit=limit, offset=offset)
    
@api_router.get("/get_all_patient_records", response_model=Union[list[schemas.Patient], list[schemas.ExplorerPatientDTO]])
async def get_all_patient_records(
	user: User = Depends(get_current_user), 
    limit: int = 1000,
    offset: int = 0,
):
    return await PatientService.get_all_patient_records(limit=limit, offset=offset, user=user)

@api_router.patch("/update_patient_record", response_model=Union[schemas.Patient, schemas.ExplorerPatientDTO])
async def update_patient_record(
    patient_id: int, 
    patient_data: schemas.PatientUpdate,
	user: User = Depends(get_current_user)
):
    return await PatientService.update_patient_record(user=user, patient_in=patient_data, patient_id=patient_id)

@api_router.delete("/delete_patient_record")
async def delete_patient_record(
    patient_id: int,
	user: User = Depends(get_current_user),
):  
    return await PatientService.delete_patient_record(user=user, patient_id=patient_id)
