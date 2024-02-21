from . import schemas, models
from .dao import PatientDAO

from ..auth.service import AuthService, UserService
from ..auth.models import User


class PatientCRUD:

    async def create_patient(self, patient_data: schemas.PatientCreate, user: User) -> models.Patient:

        db_patient = await PatientDAO.add(
            schemas.PatientCreateDB(
                therapist_id=user.id,
                **patient_data.model_dump(),
            ))

        return db_patient

    async def get_patient_records(self, user: User, patient_id, offset: int, limit: int, **filter_by) -> list[models.Patient]:
        
        patient_records = await PatientDAO.find_all(
            models.Patient.id==patient_id,
            offset=offset,
            limit=limit
        )   
        
        return patient_records
        
    async def get_all_patient_records(self, *filter, user: User, offset: int, limit: int, **filter_by) -> list[models.Patient]:
        
        patient_records = await PatientDAO.find_all(*filter, offset=offset, limit=limit, **filter_by)
        
        return patient_records
    
    async def update_patient_record(self, user: User, patient_id: int, patient_in: schemas.PatientUpdate) -> models.Patient:
        
        patient_record = await PatientDAO.update(models.Patient.id==patient_id, obj_in=patient_in)

        return patient_record
    
    async def delete_patient_record(self, user: User, patient_id: int) -> dict:
        
        await PatientDAO.delete(models.Patient.id==patient_id)
        
        return {"Message": f"Therapist {user.id} deleted pathient record {patient_id} successfully"}

class PatientManager:
    def __init__(self):
        self.patient_crud = PatientCRUD()
