from async_lru import alru_cache
from fastapi import APIRouter, Depends

from ..auth.dependencies import get_current_superuser
from ..auth.models import User
from . import schemas
from .dependencies import get_current_therapist, get_current_user
from .service import PatientService


patient_router = APIRouter(prefix="/patient")


@patient_router.post("/create", response_model=schemas.Patient)
async def create_patient(patient_data: schemas.PatientCreate, user: User = Depends(get_current_therapist)):
    return await PatientService.create_patient(patient_data=patient_data, user=user)


@alru_cache
@patient_router.get("/get", response_model=schemas.Patient | dict)
async def get_patient(patient_id: str, user: User = Depends(get_current_therapist)):
    return await PatientService.get_patient(patient_id=patient_id, user=user)


@alru_cache
@patient_router.post("/get_all", response_model=list[schemas.Patient] | list[schemas.ExplorerPatientDTO])
async def get_all_patients(
    filters: list[schemas.GetFilters] | None = None,
    sorting_rules: list[schemas.GetSorting] | None = None,
    limit: int = 100,
    offset: int = 0,
    user: User = Depends(get_current_user),
    global_rule: schemas.GlobalRule = "every",
):
    return await PatientService.get_all_patients(
        user=user,
        offset=offset,
        limit=limit,
        filters=filters,
        global_rule=global_rule,
        sorting_rules=sorting_rules,
    )


@alru_cache
@patient_router.get("/get_all_by_therapist", response_model=list[schemas.Patient])
async def get_all_patients_by_therapist(
    limit: int = 100, offset: int = 0, user: User = Depends(get_current_therapist)
):
    return await PatientService.get_all_patients_by_therapist(
        user=user, offset=offset, limit=limit, therapist_id=user.id
    )


@patient_router.patch("/update", response_model=schemas.Patient)
async def update_patient(
    patient_id: str, patient_in: schemas.PatientUpdate, user: User = Depends(get_current_therapist)
):
    return await PatientService.update_patient(patient_id=patient_id, patient_in=patient_in, user=user)


@patient_router.delete("/delete", response_model=dict)
async def delete_patient(patient_id: str, user: User = Depends(get_current_therapist)):
    return await PatientService.delete_patient(patient_id=patient_id, user=user)


@patient_router.delete("/delete_all", response_model=dict)
async def delete_all_patients(superuser: User = Depends(get_current_superuser)):
    return await PatientService.delete_all_patients(superuser=superuser)
