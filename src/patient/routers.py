from fastapi import APIRouter, Depends

from . import schemas
from .service import PatientService
from .dependencies import get_current_therapist, get_current_user
from ..auth.models import User


patient_router = APIRouter(prefix="/patient_router")


@patient_router.post("/create_patient", response_model=schemas.Patient)
async def create_patient(
    patient_data: schemas.PatientCreate,
    user: User = Depends(get_current_therapist)
):
    return await PatientService.create_patient(patient_data=patient_data, user=user)

@patient_router.get("/get_patient", response_model=schemas.Patient | dict)
async def get_patient(
    patient_id: str,
    user: User = Depends(get_current_therapist)
):
    return await PatientService.get_patient(patient_id=patient_id, user=user)

@patient_router.get("/get_all_patients", response_model=list[schemas.Patient] | list[schemas.ExplorerPatientDTO])
async def get_all_patients(
    limit: int = 100,
    offset: int = 0,
    user: User = Depends(get_current_user)
):
    return await PatientService.get_all_patients(user=user, offset=offset, limit=limit)

@patient_router.get("/get_all_patients_by_therapist", response_model=list[schemas.Patient])
async def get_all_patients_by_therapist(
    limit: int = 100,
    offset: int = 0,
    user: User = Depends(get_current_therapist)
):
    return await PatientService.get_all_patients_by_therapist(user=user, offset=offset, limit=limit, therapist_id=user.id)

@patient_router.patch("/update_patient", response_model=schemas.Patient)
async def update_patient(
    patient_id: str,
    patient_in: schemas.PatientUpdate,
    user: User = Depends(get_current_therapist)
):
    return await PatientService.update_patient(patient_id=patient_id, patient_in=patient_in, user=user)

@patient_router.delete("/delete_patient", response_model=dict)
async def delete_patient(
    patient_id: str,
    user: User = Depends(get_current_therapist)
):
    return await PatientService.delete_patient(patient_id=patient_id, user=user)

@patient_router.delete("/delete_all_patients", response_model=dict)
async def delete_all_patients(
    user: User = Depends(get_current_therapist)
):
    return await PatientService.delete_all_patients(user=user)

