from typing import Union

from fastapi import APIRouter, Depends

from ..auth.dependencies import get_current_user
from ..auth.models import User
from . import schemas
from .dependencies import get_current_therapist
from .service import PatientRecordsService

patient_records_router = APIRouter(prefix="/patient_records_router")


@patient_records_router.post("/create_patient_record", response_model=schemas.PatientRecords)
async def create_patient_record(
    patient_record_data: schemas.PatientRecordsCreate, user: User = Depends(get_current_therapist)
):
    return await PatientRecordsService.create_patient_record(
        patient_record_data=patient_record_data, user=user
    )


@patient_records_router.get(
    "/get_one_patient_record", response_model=schemas.PatientRecords | schemas.ExplorerPatientDTO | None
)
async def get_one_patient_record(
    patient_id: str, patient_record_id: str, user: User = Depends(get_current_user)
):
    return await PatientRecordsService.get_one_patient_record(
        user=user, patient_id=patient_id, patient_record_id=patient_record_id
    )


@patient_records_router.get(
    "/get_patient_records", response_model=list[schemas.PatientRecords] | list[schemas.ExplorerPatientDTO]
)
async def get_patient_records(
    patient_id: str, limit: int = 100, offset: int = 0, user: User = Depends(get_current_user)
):
    return await PatientRecordsService.get_patient_records(
        patient_id=patient_id, user=user, limit=limit, offset=offset
    )


@patient_records_router.get(
    "/get_all_patient_records",
    response_model=Union[list[schemas.PatientRecords], list[schemas.ExplorerPatientDTO]],
)
async def get_all_patient_records(
    user: User = Depends(get_current_user),
    limit: int = 1000,
    offset: int = 0,
):
    return await PatientRecordsService.get_all_patient_records(limit=limit, offset=offset, user=user)


@patient_records_router.get(
    "/get_all_patient_records_by_therapist",
    response_model=Union[list[schemas.PatientRecords], list[schemas.ExplorerPatientDTO]],
)
async def get_all_patient_records_by_therapist(
    limit: int = 100, offset: int = 0, user: User = Depends(get_current_user)
):
    return await PatientRecordsService.get_all_patient_records_by_therapist(
        user=user, offset=offset, limit=limit, therapist_id=user.id
    )


@patient_records_router.patch("/update_patient_record", response_model=schemas.PatientRecords)
async def update_patient_record(
    patient_record_id: str, patient_data: schemas.PatientRecordsUpdate, user: User = Depends(get_current_user)
):
    return await PatientRecordsService.update_patient_record(
        user=user, patient_in=patient_data, patient_record_id=patient_record_id
    )


@patient_records_router.delete("/delete_patient_record")
async def delete_patient_record(
    patient_record_id: str,
    user: User = Depends(get_current_user),
):
    return await PatientRecordsService.delete_patient_record(user=user, patient_record_id=patient_record_id)


@patient_records_router.delete("/delete_all_patient_records")
async def delete_all_patient_records(user: User = Depends(get_current_therapist)):
    return await PatientRecordsService.delete_all_patient_records(user=user)
