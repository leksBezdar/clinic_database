from fastapi import APIRouter, Depends

from . import schemas
from .service import PatientService
from .dependencies import get_current_therapist
from ..auth.models import User


patient_router = APIRouter(prefix="/patient_router")


@patient_router.post("/create_patient", response_model=schemas.Patient | None)
async def create_patient(
    patient_data: schemas.PatientCreate,
    user: User = Depends(get_current_therapist)
):
    return await PatientService.create_patient(patient_data=patient_data, user=user)

@patient_router.get("/get_patient", response_model=schemas.Patient | None)
async def get_patient(
    patient_id: str,
    user: User = Depends(get_current_therapist)
):
    return await PatientService.get_patient(patient_id=patient_id, user=user)

@patient_router.get("/get_all_patients", response_model=list[schemas.Patient | None])
async def get_all_patients(
    limit: int = 100,
    offset: int = 0,
    user: User = Depends(get_current_therapist)
):
    return await PatientService.get_all_patients(user=user, offset=offset, limit=limit)

@patient_router.patch("/update_patient", response_model=schemas.Patient | None)
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

