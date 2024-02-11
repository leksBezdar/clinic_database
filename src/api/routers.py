from fastapi import APIRouter
from . import schemas
from .service import PatientManager

router = APIRouter()


@router.post("/create_patient_record", response_model=schemas.Patient)
async def create_patient_record(
  	patient_data: schemas.PatientCreate,
	access_token: str,
):
    patient_manager = PatientManager()
    patient_crud = patient_manager.patient_crud

    return await patient_crud.create_patient(patient_data=patient_data, access_token=access_token)

@router.get("/get_patient_records", response_model=list[schemas.Patient])
async def get_patient_records(
    access_token: str,
    patient_id: int,
    limit: int = 100,
    offset: int = 0,
):
    patient_manager = PatientManager()
    patient_crud = patient_manager.patient_crud

    return await patient_crud.get_patient_records(
        patient_id=patient_id, access_token=access_token,
        limit=limit, offset=offset)
    
@router.get("/get_all_patient_records", response_model=list[schemas.Patient])
async def get_all_patient_records(
    access_token: str, 
    limit: int = 1000,
    offset: int = 0,
):
    patient_manager = PatientManager()
    patient_crud = patient_manager.patient_crud

    return await patient_crud.get_all_patient_records(access_token=access_token, limit=limit, offset=offset)

@router.patch("/update_patient_record", response_model=schemas.Patient)
async def update_patient_record(
    access_token: str, 
    patient_id: int, 
    patient_data: schemas.PatientUpdate
):
    patient_manager = PatientManager()
    patient_crud = patient_manager.patient_crud

    return await patient_crud.update_patient_record(access_token=access_token, patient_in=patient_data, patient_id=patient_id)

@router.delete("/delete_patient_record")
async def delete_patient_record(
    access_token: str,
    patient_id: int
):  
    patient_manager = PatientManager()
    patient_crud = patient_manager.patient_crud

    return await patient_crud.delete_patient_record(access_token=access_token, patient_id=patient_id)
