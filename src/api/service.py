from . import schemas, models
from .dao import PatientDAO

from ..auth.service import AuthService, UserService


class PatientCRUD:

    async def create_patient(self, patient_data: schemas.PatientCreate, access_token: str) -> models.Patient:
        
        user_id = await self._get_therapist_id_from_token(access_token)

        db_patient = await PatientDAO.add(
            schemas.PatientCreateDB(
                therapist_id=user_id,
                **patient_data.model_dump(),
            ))

        return db_patient

    async def _get_therapist_id_from_token(self, access_token: str) -> str:
        
        return await UserService._get_access_token_payload(access_token)
    
    async def get_patient_records(self, access_token: str, patient_id, offset: int, limit: int, **filter_by) -> list[models.Patient]:
        
        therapist_id = await self._get_therapist_id_from_token(access_token)
        
        patient_records = await PatientDAO.find_all(
            models.Patient.id==patient_id,
            offset=offset,
            limit=limit
        )   
        
        return patient_records
        
    async def get_all_patient_records(self, *filter, access_token: str, offset: int, limit: int, **filter_by) -> list[models.Patient]:
        
        therapist_id = await self._get_therapist_id_from_token(access_token)
        patient_records = await PatientDAO.find_all(*filter, offset=offset, limit=limit, **filter_by)
        
        return patient_records
    
    async def update_patient_record(self, access_token: str, patient_id: int, patient_in: schemas.PatientUpdate) -> models.Patient:
        
        therapist_id = await self._get_therapist_id_from_token(access_token)  
        patient_record = await PatientDAO.update(models.Patient.id==patient_id, obj_in=patient_in)

        return patient_record
    
    async def delete_patient_record(self, access_token: str, patient_id: int) -> dict:
        
        therapist_id = await self._get_therapist_id_from_token(access_token)
        await PatientDAO.delete(models.Patient.id==patient_id)
        
        return {"Message": f"Therapist {therapist_id} deleted pathient record {patient_id} successfully"}

class PatientManager:
    def __init__(self):
        self.patient_crud = PatientCRUD()
